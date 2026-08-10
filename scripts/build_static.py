import os
from jinja2 import Environment, FileSystemLoader
from scout.db import get_connection

def build_static_site():
    print("Building static HTML export...")
    
    # 1. Setup Jinja2 Environment
    template_dir = os.path.join("src", "scout", "web", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("index.html")
    
    # 2. Fetch Data from SQLite
    conn = get_connection()
    conn.row_factory = sqlite3.Row if 'sqlite3' in globals() else None
    
    import sqlite3
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT o.id, o.title, o.problem_description, o.score, o.created_at, o.sent_at,
               p.severity, p.target_audience,
               (SELECT d.original_url FROM evidence e JOIN discoveries d ON e.discovery_id = d.id WHERE e.problem_id = p.id LIMIT 1) as url,
               (SELECT s.name FROM evidence e JOIN discoveries d ON e.discovery_id = d.id JOIN sources s ON d.source_id = s.id WHERE e.problem_id = p.id LIMIT 1) as source_name,
               (SELECT s.type FROM evidence e JOIN discoveries d ON e.discovery_id = d.id JOIN sources s ON d.source_id = s.id WHERE e.problem_id = p.id LIMIT 1) as source_type
        FROM opportunities o
        JOIN problems p ON o.problem_id = p.id
        ORDER BY o.score DESC, o.created_at DESC
        LIMIT 50
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    opportunities = [dict(row) for row in rows]
    conn.close()
    
    # 3. Render HTML
    rendered_html = template.render(opportunities=opportunities)
    
    # 4. Save to /public directory
    os.makedirs("public", exist_ok=True)
    with open(os.path.join("public", "index.html"), "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    print(f"Successfully generated public/index.html with {len(opportunities)} opportunities.")

if __name__ == "__main__":
    build_static_site()
