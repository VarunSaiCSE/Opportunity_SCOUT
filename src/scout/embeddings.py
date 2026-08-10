import httpx

OLLAMA_API_URL = "http://localhost:11434/api/embeddings"

def get_embedding(text: str, model_name: str = "nomic-embed-text") -> list[float]:
    """
    Calls Ollama to generate a vector embedding for the given text.
    Assumes `nomic-embed-text` is installed (`ollama pull nomic-embed-text`).
    """
    payload = {
        "model": model_name,
        "prompt": text
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
