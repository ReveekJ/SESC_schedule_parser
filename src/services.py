import sys

if sys.path[0] != '/home/user/PycharmProjects/SESC_parser':
    sys.path.insert(0, sys.path[0][:sys.path[0].rfind('/')])
    print(sys.path)

from fastapi import FastAPI

from crypto_service import crypto

app = FastAPI(
    title='SESC_schedule_services'
)

app.include_router(crypto.router)

