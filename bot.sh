#!/bin/bash
cd src && uvicorn services:app --reload && cd .. &
exec python3 -m src.tgbot.bot
