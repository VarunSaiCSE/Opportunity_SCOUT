import time
from typing import List, Dict, Any
from scout.db import get_active_sources, insert_discovery
from scout.sources import SOURCE_REGISTRY

class SourceManager:
    """Manages the execution of all active research sources."""
    
    def run_all(self):
        print("Starting SourceManager...")
        sources = get_active_sources()
        
        if not sources:
            print("No active sources found in the database.")
            return
            
        for source_row in sources:
            source_id = source_row['id']
            source_type = source_row['type']
            name = source_row['name']
            url = source_row['url']
            
            print(f"Running source: {name} ({source_type})...")
            
            source_class = SOURCE_REGISTRY.get(source_type)
            if not source_class:
                print(f"Unknown source type '{source_type}', skipping.")
                continue
                
            try:
                # Instantiate the source implementation
                source_instance = source_class(source_id=source_id, url=url)
                
                # Fetch discoveries
                discoveries = source_instance.fetch()
                print(f"  Fetched {len(discoveries)} items.")
                
                # Insert into DB
                new_items = 0
                for disc in discoveries:
                    row_id = insert_discovery(
                        source_id=source_id,
                        original_url=disc['original_url'],
                        title=disc['title'],
                        content=disc['content'],
                        author=disc.get('author')
                    )
                    if row_id:
                        new_items += 1
                        
                print(f"  Inserted {new_items} new discoveries (skipped {len(discoveries) - new_items} duplicates).")
                
            except Exception as e:
                print(f"  Error running source {name}: {e}")
                
            # Be nice to APIs
            time.sleep(1)
            
        print("SourceManager finished.")
