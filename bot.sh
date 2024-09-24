#!/bin/sh
alembic upgrade head
exec python3 -m src.tgbot.bot
