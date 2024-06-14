import sys

if sys.path[0] != '/home/user/PycharmProjects/SESC_parser':
    sys.path.insert(0, sys.path[0][:sys.path[0].rfind('/')])

from fastapi import FastAPI

from crypto_service import crypto
from lycreg_request_service import lycreg


app = FastAPI(
    title='SESC_schedule_services'
)

app.include_router(crypto.router)
app.include_router(lycreg.router)
