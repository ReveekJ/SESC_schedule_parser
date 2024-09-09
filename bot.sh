#!/bin/sh
cd src && uvicorn services:app && cd .. &
alembic upgrade head
exec python3 -m src.tgbot.bot
