from scout.db import get_connection
from scout.filter import is_junk
from scout.deduper import is_duplicate
from scout.detector import analyze_discovery

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
            # In a real system we'd have a 'status' column in discoveries
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
