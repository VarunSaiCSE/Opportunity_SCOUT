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
        SELECT p.problem_summary 
        FROM opportunities o 
        JOIN problems p ON o.problem_id = p.id 
        WHERE o.user_vote = 1 
        ORDER BY o.created_at DESC LIMIT 3
    """)
    liked = [row['problem_summary'] for row in cursor.fetchall()]
    
    # Get 3 disliked problems
    cursor.execute("""
        SELECT p.problem_summary 
        FROM opportunities o 
        JOIN problems p ON o.problem_id = p.id 
        WHERE o.user_vote = -1 
        ORDER BY o.created_at DESC LIMIT 3
    """)
    disliked = [row['problem_summary'] for row in cursor.fetchall()]
    
    conn.close()
    return {"liked": liked, "disliked": disliked}

def cleanup_old_data(days=30):
    """Silently deletes raw data and un-scored problems older than `days` to prevent infinite DB bloat."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        print(f"Cleaning up database records older than {days} days...")
        
        # 1. Delete raw scrapes
        cursor.execute("DELETE FROM raw_scrapes WHERE created_at < datetime('now', ?)", (f"-{days} days",))
        deleted_raw = cursor.rowcount
        
        # 2. Delete problems that never became opportunities
        cursor.execute(
            """
            DELETE FROM problems 
            WHERE created_at < datetime('now', ?) 
            AND id NOT IN (SELECT problem_id FROM opportunities)
            """, (f"-{days} days",)
        )
        deleted_probs = cursor.rowcount
        
        conn.commit()
        
        # Reclaim disk space
        conn.execute("VACUUM")
        
        print(f"Cleanup complete. Deleted {deleted_raw} raw scrapes and {deleted_probs} un-scored problems.")
    except Exception as e:
        print(f"Failed to cleanup database: {e}")
    finally:
        conn.close()
