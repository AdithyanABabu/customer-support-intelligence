@echo off
echo Starting Customer Support Intelligence...
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
pause