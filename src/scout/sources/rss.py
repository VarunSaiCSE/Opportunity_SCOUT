import feedparser
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseSource

class RSSSource(BaseSource):
    """Fetches entries from a standard RSS or Atom feed."""
    
    def fetch(self) -> List[Dict[str, Any]]:
        # Feedparser handles HTTP natively and is robust
        feed = feedparser.parse(self.url)
        
        discoveries = []
        
        # Limit to the newest 15 entries to avoid blowing up DB
        entries = feed.entries[:15]
        
        for entry in entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            author = entry.get("author", "unknown")
            
            # Some feeds put content in 'content' array, others in 'summary'
            html_content = ""
            if "content" in entry and len(entry.content) > 0:
                html_content = entry.content[0].value
            else:
                html_content = entry.get("summary", "")
                
            # Clean HTML from RSS content
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
