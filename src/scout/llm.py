import json
import httpx
import time
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Any

T = TypeVar('T', bound=BaseModel)

OLLAMA_API_URL = "http://localhost:11434/api/generate"

class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass

def generate_structured(
    prompt: str, 
    response_model: Type[T], 
    model_name: str = "qwen2.5:14b",
    system_prompt: str = "You are a highly analytical research assistant.",
    timeout: int = 120,
    max_retries: int = 3
) -> T:
    """
    Sends a prompt to Ollama, forces JSON output, and validates it against a Pydantic model.
    """
    
    # We append the schema to the system prompt to guide the LLM
    schema_json = json.dumps(response_model.model_json_schema(), indent=2)
    full_system_prompt = f"""{system_prompt}

You MUST output your response in valid JSON format.
Your output MUST perfectly match this JSON schema:

{schema_json}

Do not include any markdown formatting, explanations, or extra text. Output ONLY the JSON object.
"""

    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": full_system_prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1 # Keep it deterministic for JSON extraction
        }
    }

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(OLLAMA_API_URL, json=payload)
                response.raise_for_status()
                
            data = response.json()
            response_text = data.get("response", "")
            
            # Ollama sometimes wraps json in markdown even when format=json is set.
            # We strip common markdown wrappers if they exist.
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse the JSON string and validate with Pydantic
            parsed_data = json.loads(response_text)
            return response_model.model_validate(parsed_data)
            
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                raise LLMError(f"Failed to connect to Ollama after {max_retries} attempts: {e}")
            time.sleep(5)  # Wait for Ollama to recover (e.g. from a 500 Server Error)
        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                raise LLMError(f"Ollama returned invalid JSON: {e}\nResponse was: {response_text}")
            time.sleep(2)
        except ValidationError as e:
            if attempt == max_retries - 1:
                raise LLMError(f"Ollama returned JSON that doesn't match the schema: {e}\nResponse was: {response_text}")
            time.sleep(2)
            
    raise LLMError("Failed to generate structured output.")

def unload_model(model_name: str = "qwen2.5:14b") -> None:
    """
    Forcefully unloads the model from Mac's unified memory by setting keep_alive to 0.
    """
    try:
        with httpx.Client(timeout=10) as client:
            client.post(OLLAMA_API_URL, json={
                "model": model_name,
                "keep_alive": 0
            })
    except Exception as e:
        print(f"Failed to unload model {model_name}: {e}")
