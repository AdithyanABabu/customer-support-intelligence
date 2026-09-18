import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import database as db
from backend import insights as insight_engine
from backend.insights import combine_analysis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="Zentrix AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.path.dirname(db.DB_PATH), exist_ok=True)
db.init_db()

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class AnalyzeRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    result = combine_analysis(request.text)
    if result.get("error"):
        return result
    result["history_id"] = db.save_analysis(result)
    return result


@app.get("/api/messages")
def messages(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return {"total": len(db.recent_ids()), "messages": db.list_results(limit=limit, offset=offset)}


@app.get("/api/insights")
def insights(limit: int = Query(100, ge=1, le=500)):
    ids = db.recent_ids(limit=limit)
    rows = db.list_messages(limit=len(ids), offset=0)
    history = [
        {
            "topic": r["topic"],
            "sentiment": r["sentiment"],
            "sentiment_score": r["sentiment_score"],
            "urgency": r["urgency"],
            "phishing_detected": bool(r["phishing_detected"]),
            "risk_level": r["risk_level"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    return insight_engine.analyze_messages_bulk(history)