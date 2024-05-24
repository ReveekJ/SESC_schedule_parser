#!/bin/bash
source .venv/bin/activate
#dir=$(dirname "$(pwd)")
pip install -r requirements.txt --break-system-packages
export PYTHONPATH=$PYTHONPATH:pwd
chmod +x ./docker.sh

./docker.sh &

cd src/ || exit
uvicorn services:app --reload &
cd .. || exit

#cd "$dir" || exit
exec python3 "$(pwd)"/src/tgbot/bot.py
