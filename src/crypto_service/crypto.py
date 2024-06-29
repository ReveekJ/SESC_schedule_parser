from http import HTTPStatus
from fastapi import APIRouter
from cryptography.fernet import Fernet, InvalidToken

router = APIRouter(prefix='/crypt', tags=['crypto'])


@router.post('/encrypt')
async def encrypt(crypto_string: str, key: str | bytes):
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
async def decrypt(crypto_string: str, key: str | bytes):
    try:
        f = Fernet(bytes(key, 'utf-8'))
        decrypted_string = f.decrypt(bytes(crypto_string, 'utf-8')).decode('utf-8')
        return {'status': HTTPStatus.OK,
                'crypto_string': decrypted_string}
    except InvalidToken:
        return {'status': HTTPStatus.IM_A_TEAPOT}
    except Exception as e:
        return {'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'error': str(e)}
    