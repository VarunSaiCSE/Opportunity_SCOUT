from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSource(ABC):
    """Abstract base class for all research sources."""
    
    def __init__(self, source_id: int, url: str):
        self.source_id = source_id
        self.url = url
        
    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetches data from the source.
        Must return a list of dictionaries, where each dict has:
        - original_url: str
        - title: str
        - content: str
        - author: str (optional)
        """
        pass
