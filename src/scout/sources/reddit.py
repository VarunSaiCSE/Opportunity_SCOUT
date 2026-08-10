import feedparser
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BaseSource

class RedditSource(BaseSource):
    """Fetches top daily posts from a specified subreddit using its RSS feed."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self) -> List[Dict[str, Any]]:
        # url in DB is expected to be the subreddit, e.g., 'r/SaaS'
        subreddit = self.url.strip('/')
        api_url = f"https://www.reddit.com/{subreddit}/top/.rss?t=day"
        
        feed = feedparser.parse(api_url)
        
        if feed.get('status') == 429:
            raise Exception("Reddit rate limit exceeded.")
            
        discoveries = []
        entries = feed.entries[:15]
        
        for entry in entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            author = entry.get("author", "unknown")
            
            html_content = ""
            if "content" in entry and len(entry.content) > 0:
                html_content = entry.content[0].value
            else:
                html_content = entry.get("summary", "")
                
            content = ""
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                content = soup.get_text(separator=" ", strip=True)
                
            if not content:
                content = title
                
            discoveries.append({
                "original_url": link,
                "title": title,
                "content": content,
                "author": author
            })
            
        return discoveries
