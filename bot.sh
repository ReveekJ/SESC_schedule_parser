#!/bin/bash
cd src && uvicorn services:app --reload && cd .. &
alembic upgrade head
exec python3 -m src.tgbot.bot
