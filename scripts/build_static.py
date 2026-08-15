import os
import datetime
from jinja2 import Environment, FileSystemLoader
from scout.db import get_connection

def build_static_site():
    print("Building static HTML export...")
    
    # 1. Setup Jinja2 Environment
    template_dir = os.path.join("src", "scout", "web", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # 2. Fetch Data from SQLite
    conn = get_connection()
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
        ORDER BY o.created_at DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    opportunities = [dict(row) for row in rows]
    conn.close()
    
    today_opportunities = []
    archives_by_date = {}
    
    if opportunities:
        latest_dt = datetime.datetime.strptime(opportunities[0]['created_at'], "%Y-%m-%d %H:%M:%S")
        latest_date_str = latest_dt.strftime("%B %d, %Y")
        
        for opp in opportunities:
            opp_dt = datetime.datetime.strptime(opp['created_at'], "%Y-%m-%d %H:%M:%S")
            opp_date_str = opp_dt.strftime("%B %d, %Y")
            
            if opp_date_str == latest_date_str:
                today_opportunities.append(opp)
            else:
                if opp_date_str not in archives_by_date:
                    archives_by_date[opp_date_str] = []
                archives_by_date[opp_date_str].append(opp)
                
    # Sort opportunities within each day by score DESC
    today_opportunities.sort(key=lambda x: x['score'], reverse=True)
    for date_str in archives_by_date:
        archives_by_date[date_str].sort(key=lambda x: x['score'], reverse=True)

    # 3. Render HTML
    template_index = env.get_template("index.html")
    rendered_index = template_index.render(opportunities=today_opportunities, is_archive=False, today_date=latest_date_str if opportunities else "Today")
    
    template_archive = env.get_template("archive.html")
    rendered_archive = template_archive.render(archives=archives_by_date, is_archive=True)
    
    # 4. Save to /public directory
    os.makedirs("public", exist_ok=True)
    with open(os.path.join("public", "index.html"), "w", encoding="utf-8") as f:
        f.write(rendered_index)
        
    with open(os.path.join("public", "archive.html"), "w", encoding="utf-8") as f:
        f.write(rendered_archive)
        
    print(f"Successfully generated public/index.html with {len(today_opportunities)} opportunities.")
    print(f"Successfully generated public/archive.html with {sum(len(v) for v in archives_by_date.values())} opportunities.")

if __name__ == "__main__":
    build_static_site()
