from scout.db import get_connection
from scout.sources.manager import SourceManager

def seed_sources():
    """Adds a test Hacker News source to the database if it doesn't exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Check if it exists
        cursor.execute("SELECT id FROM sources WHERE name = 'HN: Ask HN'")
        if not cursor.fetchone():
            print("Adding Hacker News source to database...")
            cursor.execute(
                "INSERT INTO sources (name, type, url, is_active) VALUES (?, ?, ?, ?)",
                ("HN: Ask HN", "hn", "https://hn.algolia.com/api/v1/search_by_date", 1)
            )
            conn.commit()
    finally:
        conn.close()

def verify_discoveries():
    """Prints the newly added discoveries from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) as total FROM discoveries")
        total = cursor.fetchone()['total']
        print(f"\nTotal discoveries in DB: {total}")
        
        cursor.execute("SELECT title, author, original_url FROM discoveries LIMIT 3")
        rows = cursor.fetchall()
        print("\nSample Discoveries:")
        for row in rows:
            print(f"- [{row['author']}] {row['title']} ({row['original_url']})")
            
    finally:
        conn.close()

if __name__ == "__main__":
    print("Testing SCOUT Ingestion Pipeline...\n")
    
    # 1. Seed the DB with a source
    seed_sources()
    
    # 2. Run the manager to fetch and insert
    manager = SourceManager()
    manager.run_all()
    
    # 3. Verify it worked
    verify_discoveries()
