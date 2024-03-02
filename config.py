import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
TOKEN = os.environ.get('TOKEN')
PATH_TO_FONT = os.environ.get('PATH_TO_FONT')
ADMINS = list(map(int, os.environ.get('ADMINS').split('_')))
