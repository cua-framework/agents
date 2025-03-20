#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

python -m playwright install chromium & # NEW

STREAMLIT_SERVER_PORT=8501 python -m streamlit run computer_use_demo/streamlit.py > /tmp/streamlit_stdout.log &

python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8085 > /tmp/fastapi_stdout.log 2>&1 & # NEW

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8080 in your browser to begin"
echo "➡️  FastAPI server is running at http://localhost:8085" # NEW

# Keep the container running
tail -f /dev/null
