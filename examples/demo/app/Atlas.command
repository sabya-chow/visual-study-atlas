#!/bin/bash
# Double-click to start the study atlas (keep this window open while you read).
cd "$(dirname "$0")"
PORT=$(python3 -c "import json;print(json.load(open('config.json'))['port'])")
if ! curl -s -m 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Starting Ollama..."; (open -a Ollama 2>/dev/null || (nohup ollama serve >/dev/null 2>&1 &)); sleep 5
fi
echo "First run builds a search index over the book (a few minutes). Questions work while it builds."
lsof -ti tcp:$PORT | xargs kill 2>/dev/null   # clear a stale copy on this port
sleep 1
python3 server.py --port "$PORT" &
SPID=$!
sleep 1; open "http://127.0.0.1:$PORT"
trap "kill $SPID 2>/dev/null" EXIT
wait $SPID
