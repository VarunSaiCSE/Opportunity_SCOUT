import httpx
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BaseSource

class HackerNewsSource(BaseSource):
    """Fetches recent posts from Hacker News via Algolia API."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self) -> List[Dict[str, Any]]:
        # For this example, let's fetch recent "Ask HN" posts since they often contain problems
        api_url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "tags": "ask_hn",
            "hitsPerPage": 15
        }
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
        discoveries = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            story_text = hit.get("story_text", "")
            
            # Clean HTML from story text
            content = ""
            if story_text:
                soup = BeautifulSoup(story_text, "html.parser")
                content = soup.get_text(separator=" ", strip=True)
            
            # If there's no body text, just use the title
            if not content:
                content = title
                
            discoveries.append({
                "original_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                "title": title,
                "content": content,
                "author": hit.get("author", "unknown")
            })
            
        return discoveries
