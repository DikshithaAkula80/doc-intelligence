#!/bin/bash
cd ~/doc-intelligence
source venv/bin/activate
echo "Starting API server..."
uvicorn api:app --reload --port 8000 &
sleep 3
echo "Starting Streamlit UI..."
streamlit run app.py
