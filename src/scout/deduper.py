import json
import numpy as np
from scout.db import get_connection
from scout.embeddings import get_embedding

SIMILARITY_THRESHOLD = 0.85

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Computes cosine similarity between two vectors."""
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def is_duplicate(discovery_id: int, content: str) -> bool:
    """
    Checks if this discovery is highly similar to a recently processed one.
    Returns True if it's a duplicate, False otherwise.
    Also saves the embedding for this discovery.
    """
    try:
        new_embedding = get_embedding(content)
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return False # Fail open if embedding generation fails
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Save the new embedding for future comparisons
        cursor.execute(
            "INSERT OR REPLACE INTO discovery_embeddings (discovery_id, embedding_json) VALUES (?, ?)",
            (discovery_id, json.dumps(new_embedding))
        )
        conn.commit()
        
        # Fetch recent embeddings (e.g., from the last 7 days)
        # For this simple prototype, we'll fetch the last 1000
        cursor.execute(
            """
            SELECT e.embedding_json, d.id 
            FROM discovery_embeddings e
            JOIN discoveries d ON e.discovery_id = d.id
            WHERE d.id != ?
            ORDER BY d.collection_timestamp DESC
            LIMIT 1000
            """,
            (discovery_id,)
        )
        
        for row in cursor.fetchall():
            existing_embedding = json.loads(row['embedding_json'])
            if not existing_embedding:
                continue
            similarity = cosine_similarity(new_embedding, existing_embedding)
            
            if similarity > SIMILARITY_THRESHOLD:
                print(f"Discovery {discovery_id} is a duplicate of {row['id']} (similarity: {similarity:.2f})")
                return True
                
        return False
        
    finally:
        conn.close()
