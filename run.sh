#!/usr/bin/env bash
set -e
export DB_PATH=${DB_PATH:-lancamentos.db}
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
