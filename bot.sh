#!/bin/bash
dir=$(dirname "$(pwd)")

export PYTHONPATH=$PYTHONPATH:$dir/SESC_parser
chmod +x ./docker.sh

./docker.sh &

cd "$dir" || exit
exec python3 SESC_parser/tgbot/bot.py
