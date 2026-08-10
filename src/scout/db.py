import sqlite3
import os
from pathlib import Path

# The path to the SQLite database
DB_PATH = Path(__file__).parent.parent.parent / "scout.db"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "schema.sql"

def get_connection():
    """Returns a connection to the SQLite database with WAL mode enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrent reads/writes
    conn.execute("PRAGMA journal_mode=WAL")
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Initializes the database using schema.sql."""
    print(f"Initializing database at {DB_PATH}...")
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def get_active_sources():
    """Returns a list of active sources."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sources WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def insert_discovery(source_id: int, original_url: str, title: str, content: str, author: str = None) -> int:
    """Inserts a new discovery. Returns the row ID, or None if it's a duplicate."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO discoveries (source_id, original_url, title, content, author)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, original_url, title, content, author)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # It's a duplicate URL
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
