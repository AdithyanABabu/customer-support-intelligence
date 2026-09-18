@echo off
echo Starting Zentrix AI...
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
pause