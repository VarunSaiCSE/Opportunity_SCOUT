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
        
        # 5. Update Cloudflare Static Site
        print("\n--- STAGE 4: UPDATING LIVE WEBSITE ---")
        try:
            import subprocess
            import sys
            import os
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            build_script = os.path.join(repo_root, "scripts", "build_static.py")
            
            print("Building static HTML...")
            subprocess.run([sys.executable, build_script], cwd=repo_root, check=True)
            
            print("Pushing to GitHub to trigger Cloudflare...")
            subprocess.run(["git", "add", "public/index.html"], cwd=repo_root, check=True)
            # We allow git commit to fail if there are no changes, so we don't use check=True here
            subprocess.run(["git", "commit", "-m", "chore: auto-update static site after nightly run"], cwd=repo_root)
            subprocess.run(["git", "push"], cwd=repo_root, check=True)
            print("Successfully updated live website!")
        except Exception as e:
            print(f"Failed to auto-update live website: {e}")
        
        # 6. Mark as success
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
