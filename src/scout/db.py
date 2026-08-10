import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = "scout.db"

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using schema.sql."""
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

def get_active_sources() -> List[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, name, url FROM sources WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_discovery(source_id: int, original_url: str, title: str, content: str, author: str = None) -> Optional[int]:
    """Inserts a discovery. Returns row ID if successful, None if it's a duplicate URL."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO discoveries (source_id, original_url, title, content, author) VALUES (?, ?, ?, ?, ?)",
            (source_id, original_url, title, content, author)
        )
        conn.commit()
        row_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        row_id = None # Duplicate URL
    conn.close()
    return row_id

def record_vote(opportunity_id: int, vote: int):
    """Records a user's upvote (+1) or downvote (-1) for an opportunity."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE opportunities SET user_vote = ? WHERE id = ?", (vote, opportunity_id))
    conn.commit()
    conn.close()

def get_user_preferences() -> Dict[str, List[str]]:
    """Returns a dictionary containing a list of recently liked and disliked problem descriptions."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get 3 liked problems
    cursor.execute("""
        SELECT p.description 
        FROM opportunities o 
        JOIN problems p ON o.problem_id = p.id 
        WHERE o.user_vote = 1 
        ORDER BY o.created_at DESC LIMIT 3
    """)
    liked = [row['description'] for row in cursor.fetchall()]
    
    # Get 3 disliked problems
    cursor.execute("""
        SELECT p.description 
        FROM opportunities o 
        JOIN problems p ON o.problem_id = p.id 
        WHERE o.user_vote = -1 
        ORDER BY o.created_at DESC LIMIT 3
    """)
    disliked = [row['description'] for row in cursor.fetchall()]
    
    conn.close()
    return {"liked": liked, "disliked": disliked}
