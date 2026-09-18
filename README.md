# Customer Support Intelligence

AI-based application for customer-support messages: it understands the customer
problem (sentiment, topic, urgency, summary) and detects security threats
(phishing, social engineering, malicious links/domains, impersonation).

## Quick start

1. Install Python 3.10+.
2. `pip install -r requirements.txt`
3. `python -m uvicorn backend.app:app --reload --port 8000`
4. Open http://127.0.0.1:8000

Windows: double-click `run.bat`.

## Tests

`python tests/test_engine.py`

## API

- `POST /api/analyze`  body `{"text": "..."}` -> full analysis
- `GET /api/messages`  recent analyses
- `GET /api/insights`  aggregated business insights

## Architecture

```
message -> processing -> Customer AI (sentiment/topic/urgency/summary)
                       -> Security AI (urls/domains/impersonation/social engineering)
                       -> Risk & insight engine -> SQLite history -> dashboard
```