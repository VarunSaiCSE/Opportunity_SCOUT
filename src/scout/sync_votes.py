import httpx
import os
from scout.db import record_vote

# You can set this via environment variables or hardcode it for local use
# It MUST match the SYNC_SECRET environment variable set in Cloudflare Pages.
SYNC_SECRET = os.environ.get("SYNC_SECRET", "super-secret-sync-key-123")
PAGES_URL = "https://opportunity-scout.pages.dev" 

def sync_votes_from_cloud():
    print(f"Syncing votes from Cloudflare KV: {PAGES_URL}...")
    try:
        response = httpx.get(f"{PAGES_URL}/api/sync?secret={SYNC_SECRET}", timeout=30.0)
        
        if response.status_code == 401:
            print("ERROR: Unauthorized. The SYNC_SECRET on your Mac does not match the one in Cloudflare Pages.")
            return
            
        response.raise_for_status()
        data = response.json()
        votes = data.get("votes", [])
        
        if not votes:
            print("No new votes found in Cloudflare KV.")
            return
            
        print(f"Downloaded {len(votes)} new votes. Applying to local SQLite database...")
        
        for v in votes:
            opp_id = v.get("opportunity_id")
            vote_val = v.get("vote")
            print(f" -> Opportunity {opp_id}: {'Upvote (+1)' if vote_val == 1 else 'Downvote (-1)'}")
            record_vote(opp_id, vote_val)
            
        print("Successfully synced all votes!")
        
    except Exception as e:
        print(f"Failed to sync votes from Cloudflare: {e}")

if __name__ == "__main__":
    sync_votes_from_cloud()
