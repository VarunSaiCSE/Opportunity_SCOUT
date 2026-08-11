import time
from scout.db import get_connection
from scout.sources.manager import SourceManager
from scout.detector import run_pipeline as run_detection
from scout.scorer import score_all

def run_processor():
    import time
    start_time = time.time()
    # 2 hours and 55 minutes deadline (5 min buffer before 5:00 AM if started at 2:00 AM)
    deadline = start_time + (2.9 * 3600)
    
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
        
        # 2. Sync Cloudflare Votes
        print("--- STAGE 0: SYNCING VOTES ---")
        try:
            from scout.sync_votes import sync_votes_from_cloud
            sync_votes_from_cloud()
        except Exception as e:
            print(f"Failed to sync votes: {e}")
            
        # 3. Scrape data (Phase 3)
        print("\n--- STAGE 1: INGESTION ---")
        manager = SourceManager()
        manager.run_all()
        
        # 4. Detect problems (Phases 4 & 5)
        print("\n--- STAGE 2: PROBLEM DETECTION ---")
        run_detection(deadline=deadline)
        
        # 5. Score opportunities (Phase 6)
        print("\n--- STAGE 3: OPPORTUNITY SCORING ---")
        score_all(deadline=deadline)
        
        # 6. Update Cloudflare Static Site
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
            env = dict(os.environ, PATH="/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", ""))
            
            subprocess.run(["/usr/bin/git", "add", "public/index.html"], cwd=repo_root, check=True, env=env)
            # We allow git commit to fail if there are no changes, so we don't use check=True here
            subprocess.run(["/usr/bin/git", "commit", "-m", "chore: auto-update static site after nightly run"], cwd=repo_root, env=env)
            subprocess.run(["/usr/bin/git", "push"], cwd=repo_root, check=True, env=env)
            print("Successfully updated live website!")
        except Exception as e:
            print(f"Failed to auto-update live website: {e}")
            
        # 7. Cleanup Database
        print("\n--- STAGE 5: DATABASE CLEANUP ---")
        try:
            from scout.db import cleanup_old_data
            cleanup_old_data(days=30)
        except Exception as e:
            print(f"Failed to cleanup database: {e}")
        
        # 8. Mark as success
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
