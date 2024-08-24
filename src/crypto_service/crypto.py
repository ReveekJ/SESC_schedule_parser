from typing import Union

from http import HTTPStatus
from pprint import pprint

from fastapi import APIRouter
from cryptography.fernet import Fernet, InvalidToken
from pydantic import BaseModel
from requests import Request

router = APIRouter(prefix='/crypt', tags=['crypto'])


class CryptoItem(BaseModel):
    crypto_string: str
    key: Union[str, bytes]

@router.post('/encrypt')
async def encrypt(item: CryptoItem):
    crypto_string, key = item.crypto_string, item.key

    try:
        f = Fernet(bytes(key, 'utf-8'))
        encrypted_bytes = f.encrypt(bytes(crypto_string, 'utf-8'))
        encrypted_string = encrypted_bytes.decode('utf-8')
        return {'status': HTTPStatus.OK,
                'crypto_string': encrypted_string}
    except Exception as e:
        return {'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'error': str(e)}


@router.post('/decrypt')
async def decrypt(item: CryptoItem):
    crypto_string, key = item.crypto_string, item.key

    try:
        f = Fernet(bytes(key, 'utf-8'))
        decrypted_string = f.decrypt(bytes(crypto_string, 'utf-8')).decode('utf-8')
        return {'status': HTTPStatus.OK,
                'crypto_string': decrypted_string}
    except InvalidToken:
        return {'status': HTTPStatus.IM_A_TEAPOT,
                'crypto_string': ''}
    except Exception as e:
        return {'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'error': str(e)}
