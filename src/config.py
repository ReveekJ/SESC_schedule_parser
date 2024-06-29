import os

from cryptography.fernet import Fernet
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
PATH_TO_PROJECT = os.environ.get('PATH_TO_PROJECT')
CRYPTO_KEY = Fernet.generate_key()
