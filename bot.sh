#!/bin/bash
source .venv/bin/activate
dir=$(dirname "$(pwd)")
pip install -r requirements.txt --break-system-packages
export PYTHONPATH=$PYTHONPATH:$dir/SESC_parser
chmod +x ./docker.sh

./docker.sh &

cd "$dir" || exit
exec python3 SESC_parser/tgbot/bot.py
