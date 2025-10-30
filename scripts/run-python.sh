#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source .env
fastapi dev src/main.py --host "$API_HOST" --port "$API_PORT"