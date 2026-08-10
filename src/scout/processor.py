import time
from scout.db import get_connection
from scout.sources.manager import SourceManager
from scout.detector import run_pipeline as run_detection
from scout.scorer import score_all

def run_processor():
    print("========================================")
    print("Starting SCOUT Nightly Processor Job...")
    print("========================================\n")
    
    conn = get_connection()
    run_id = None
    try:
        # 1. Log the run
        cursor = conn.cursor()
        cursor.execute("INSERT INTO runs (run_type, status) VALUES ('processor', 'started')")
        run_id = cursor.lastrowid
        conn.commit()
        
        # 2. Scrape data (Phase 3)
        print("--- STAGE 1: INGESTION ---")
        manager = SourceManager()
        manager.run_all()
        
        # 3. Detect problems (Phases 4 & 5)
        print("\n--- STAGE 2: PROBLEM DETECTION ---")
        run_detection()
        
        # 4. Score opportunities (Phase 6)
        print("\n--- STAGE 3: OPPORTUNITY SCORING ---")
        score_all()
        
        # 5. Mark as success
        cursor.execute(
            """
            UPDATE runs SET status = 'success', completed_at = CURRENT_TIMESTAMP, log_message = 'Pipeline finished'
            WHERE id = ?
            """, (run_id,)
        )
        conn.commit()
        print("\n========================================")
        print("SCOUT Processor finished successfully.")
        print("========================================\n")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        if run_id:
            conn.execute(
                "UPDATE runs SET status = 'failed', log_message = ? WHERE id = ?",
                (str(e), run_id)
            )
            conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    run_processor()
