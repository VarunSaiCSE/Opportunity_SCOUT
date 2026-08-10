from pydantic import BaseModel, Field
from scout.llm import generate_structured, LLMError
from scout.db import get_connection, get_user_preferences

class OpportunityScore(BaseModel):
    title: str = Field(description="A catchy, 3-5 word title for the startup idea.")
    problem_description: str = Field(description="A clear, 1-2 sentence description of the problem and the opportunity to solve it.")
    build_difficulty: str = Field(description="Low, Medium, or High (for a solo developer).")
    monetization: str = Field(description="Low, Medium, or High.")
    score: float = Field(description="Overall score from 1.0 to 10.0 representing how good of an opportunity this is.")

def get_unscored_problems():
    """Fetches problems that haven't been scored yet."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id, p.problem_summary, p.severity, p.target_audience
            FROM problems p
            LEFT JOIN opportunities o ON p.id = o.problem_id
            WHERE o.id IS NULL
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def save_opportunity(problem_id: int, score_data: OpportunityScore) -> None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO opportunities (problem_id, title, problem_description, score)
            VALUES (?, ?, ?, ?)
            """,
            (problem_id, score_data.title, score_data.problem_description, score_data.score)
        )
        conn.commit()
    finally:
        conn.close()

def score_all():
    print("Starting SCOUT Opportunity Scorer...\n")
    problems = get_unscored_problems()
    print(f"Found {len(problems)} unscored problems.")
    
    prefs = get_user_preferences()
    liked_examples = "\n".join([f"- {desc}" for desc in prefs['liked']]) if prefs['liked'] else "None yet."
    disliked_examples = "\n".join([f"- {desc}" for desc in prefs['disliked']]) if prefs['disliked'] else "None yet."
    
    system_prompt = f"""You are a brilliant startup advisor and software engineer.
    
Here are examples of problems the user LIKED in the past:
{liked_examples}

Here are examples of problems the user DISLIKED in the past:
{disliked_examples}

Use this context to align your scoring with the user's specific preferences. Give higher scores to problems similar to those they liked, and drastically lower scores to problems similar to those they disliked."""

    for prob in problems:
        print(f"\nScoring Problem {prob['id']}: {prob['problem_summary']}")
        
        prompt = f"""
        Evaluate this problem as a potential software startup or side-project opportunity for a solo developer.
        
        Problem: {prob['problem_summary']}
        Severity: {prob['severity']}/10
        Target Audience: {prob['target_audience']}
        
        Constraints:
        - The developer is a solo dev with zero marketing budget.
        - The solution must be buildable in a few weeks or months.
        
        Score it from 1.0 to 10.0 based on these constraints and the user's preferences.
        """
        
        try:
            result = generate_structured(
                prompt=prompt,
                response_model=OpportunityScore,
                model_name="qwen2.5:14b",
                system_prompt=system_prompt
            )
            
            print(f"  -> Title: {result.title}")
            print(f"  -> Score: {result.score}/10 (Build: {result.build_difficulty}, Monetization: {result.monetization})")
            
            save_opportunity(prob['id'], result)
            
        except LLMError as e:
            print(f"  -> Failed to score problem: {e}")

if __name__ == "__main__":
    score_all()
