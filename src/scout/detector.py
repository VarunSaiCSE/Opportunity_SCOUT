from pydantic import BaseModel, Field
from scout.llm import generate_structured, LLMError
from scout.db import get_connection
from scout.filter import is_junk
from scout.deduper import is_duplicate

class OpportunityAnalysis(BaseModel):
    is_problem: bool = Field(description="Is the author describing a genuine problem or pain point?")
    problem_summary: str = Field(description="A 1-sentence summary of the problem. Empty if not a problem.")
    severity: int = Field(description="Score from 1 to 10 on how painful this problem seems.")
    target_audience: str = Field(description="Who exactly is experiencing this problem?")

def analyze_discovery(discovery_id: int, content: str) -> None:
    """
    Passes a unique discovery to the LLM. If it's a genuine problem, 
    saves it to the database and links it.
    """
    prompt = f"Analyze the following text to identify if a genuine problem is being discussed:\n\n{content}"
    
    try:
        result = generate_structured(
            prompt=prompt,
            response_model=OpportunityAnalysis,
            model_name="qwen2.5:14b"
        )
        
        if result.is_problem:
            print(f"Problem detected! {result.problem_summary} (Severity: {result.severity})")
            save_problem(discovery_id, result)
        else:
            print("No genuine problem detected.")
            
    except LLMError as e:
        print(f"Failed to analyze discovery {discovery_id}: {e}")

def save_problem(discovery_id: int, analysis: OpportunityAnalysis) -> None:
    """Saves the detected problem to the DB and links it to the discovery as evidence."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Insert the problem
        cursor.execute(
            """
            INSERT INTO problems (problem_summary, severity, target_audience)
            VALUES (?, ?, ?)
            """,
            (analysis.problem_summary, analysis.severity, analysis.target_audience)
        )
        problem_id = cursor.lastrowid
        
        # 2. Link it via evidence
        cursor.execute(
            """
            INSERT INTO evidence (problem_id, discovery_id)
            VALUES (?, ?)
            """,
            (problem_id, discovery_id)
        )
        
        conn.commit()
    finally:
        conn.close()

def get_unprocessed_discoveries():
    """Fetch discoveries that haven't been embedded or analyzed yet."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Find discoveries that don't have an entry in discovery_embeddings
        cursor.execute(
            """
            SELECT d.id, d.title, d.content 
            FROM discoveries d
            LEFT JOIN discovery_embeddings e ON d.id = e.discovery_id
            WHERE e.discovery_id IS NULL
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def run_pipeline():
    print("Starting SCOUT Pipeline (Phase 4 & 5)...\n")
    discoveries = get_unprocessed_discoveries()
    print(f"Found {len(discoveries)} unprocessed discoveries.")
    
    for disc in discoveries:
        disc_id = disc['id']
        title = disc['title']
        content = disc['content']
        
        print(f"\nProcessing ID {disc_id}: {title}")
        
        # Step 1: Heuristic Filter (Cheap)
        if is_junk(title, content):
            print("  -> Dropped by heuristic filter (junk/short).")
            # We insert a dummy embedding so we don't process it again
            conn = get_connection()
            conn.execute("INSERT OR REPLACE INTO discovery_embeddings (discovery_id, embedding_json) VALUES (?, '[]')", (disc_id,))
            conn.commit()
            conn.close()
            continue
            
        # Step 2: Deduplication (Cheap embedding generation + cosine sim)
        print("  -> Checking for duplicates (generating embedding)...")
        if is_duplicate(disc_id, content):
            print("  -> Dropped (duplicate).")
            continue
            
        # Step 3: LLM Extraction (Expensive)
        print("  -> Running LLM extraction...")
        analyze_discovery(disc_id, content)

if __name__ == "__main__":
    run_pipeline()
