#!/bin/bash
sleep 5

echo "run migration"
poetry run alembic upgrade head

echo "run fastapi app"
poetry run python main.py