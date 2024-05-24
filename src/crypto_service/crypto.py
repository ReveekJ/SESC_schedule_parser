from fastapi import APIRouter

from src.crypto_service.crypto_config import CRYPTO_KEY

router = APIRouter(prefix='/crypt', tags=['crypto'])


class CryptorEncryptor:
    def __init__(self, text: str, key: list):
        self.__text = [ord(i) for i in text]
        self.__key = key[:len(text)]

    def xor(self):
        return ''.join([chr(i ^ j) for i, j in zip(self.__text, self.__key)])


@router.get('/')
async def crypt(crypto_string: str):
    try:
        return {'status': 200,
                'crypto_string': CryptorEncryptor(crypto_string, CRYPTO_KEY).xor()}
    except Exception as e:
        return {'status': 500,
                'error': str(e)}
