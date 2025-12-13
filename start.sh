#!/bin/bash
python3 -m bot.bot &
uvicorn app.main:app --host 0.0.0.0 --port 8000