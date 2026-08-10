import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from scout.db import get_connection, record_vote

app = FastAPI(title="SCOUT Dashboard")

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@app.post("/api/vote/{opportunity_id}")
async def vote_opportunity(opportunity_id: int, vote: int = Form(...)):
    """Records an upvote (1) or downvote (-1)."""
    record_vote(opportunity_id, vote)
    return JSONResponse(content={"status": "success"})

def get_opportunities():
    """Fetch all scored opportunities from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.id, o.title, o.problem_description, o.score, o.created_at, o.sent_at,
                   p.severity, p.target_audience,
                   (SELECT d.original_url FROM evidence e JOIN discoveries d ON e.discovery_id = d.id WHERE e.problem_id = p.id LIMIT 1) as url,
                   (SELECT s.name FROM evidence e JOIN discoveries d ON e.discovery_id = d.id JOIN sources s ON d.source_id = s.id WHERE e.problem_id = p.id LIMIT 1) as source_name,
                   (SELECT s.type FROM evidence e JOIN discoveries d ON e.discovery_id = d.id JOIN sources s ON d.source_id = s.id WHERE e.problem_id = p.id LIMIT 1) as source_type
            FROM opportunities o
            JOIN problems p ON o.problem_id = p.id
            ORDER BY o.score DESC, o.created_at DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

@app.get("/")
async def read_root(request: Request):
    opportunities = get_opportunities()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"opportunities": opportunities}
    )
