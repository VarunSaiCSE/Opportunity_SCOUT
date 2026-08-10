import sys
from pydantic import BaseModel, Field
from scout.llm import generate_structured, LLMError

# Define a strict schema for what we want to extract
class OpportunityAnalysis(BaseModel):
    is_problem: bool = Field(description="Is the author describing a genuine problem or pain point?")
    problem_summary: str = Field(description="A 1-sentence summary of the problem. Empty if not a problem.")
    severity: int = Field(description="Score from 1 to 10 on how painful this problem seems.")
    target_audience: str = Field(description="Who exactly is experiencing this problem?")

def main():
    print("Testing SCOUT Local LLM Engine...\n")
    
    # A dummy text mimicking a HackerNews or Reddit comment
    dummy_text = """
    I've been trying to set up local LLMs on my Mac all weekend and it's a nightmare. 
    Every time I switch projects, I have to re-download gigabytes of weights, and there's 
    no easy way to see what's actually running in the background and eating my RAM. 
    I just want a simple menu bar app that manages all this for me.
    """
    
    prompt = f"Analyze the following text:\n\n{dummy_text}"
    
    try:
        print("Sending prompt to Ollama (this might take a few seconds)...")
        result = generate_structured(
            prompt=prompt,
            response_model=OpportunityAnalysis,
            model_name="qwen2.5:14b"
        )
        
        print("\nSuccess! The LLM adhered to the Pydantic schema:")
        print("-" * 40)
        print(f"Is Problem:      {result.is_problem}")
        print(f"Summary:         {result.problem_summary}")
        print(f"Severity:        {result.severity}/10")
        print(f"Target Audience: {result.target_audience}")
        print("-" * 40)
        
        # You can see it's a real Python object, not a string
        print(f"\nRaw Python Dict: {result.model_dump()}")
        
    except LLMError as e:
        print(f"\nError interacting with LLM: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
