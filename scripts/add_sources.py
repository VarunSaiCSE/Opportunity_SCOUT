import sqlite3
from scout.db import get_connection

def add_default_sources():
    conn = get_connection()
    cursor = conn.cursor()
    
    sources_to_add = [
        # Reddit sources
        ("Reddit SaaS", "reddit", "r/SaaS"),
        ("Reddit SideProject", "reddit", "r/SideProject"),
        ("Reddit Startups", "reddit", "r/startups"),
        ("Reddit Entrepreneur", "reddit", "r/Entrepreneur"),
        
        # RSS Sources
        ("TechCrunch", "rss", "https://techcrunch.com/feed/"),
        ("The Verge", "rss", "https://www.theverge.com/rss/index.xml")
    ]
    
    print("Seeding new sources into database...")
    added = 0
    for name, s_type, url in sources_to_add:
        # Check if exists
        cursor.execute("SELECT id FROM sources WHERE name = ? AND type = ?", (name, s_type))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO sources (name, type, url, is_active) VALUES (?, ?, ?, 1)",
                (name, s_type, url)
            )
            added += 1
            print(f"  Added {s_type} source: {name} ({url})")
        else:
            print(f"  Skipped {name} (already exists)")
            
    conn.commit()
    conn.close()
    print(f"Finished seeding {added} new sources.")

if __name__ == "__main__":
    add_default_sources()
