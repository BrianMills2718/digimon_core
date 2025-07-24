#!/bin/bash
cd ui
python3 -m http.server 8080 &
SERVER_PID=$!
echo "Test server started with PID: $SERVER_PID"
echo "Visit http://localhost:8080/research_ui.html"
echo "To stop: kill $SERVER_PID"