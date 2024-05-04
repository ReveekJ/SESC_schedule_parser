from fastapi import FastAPI
from crypto_config import CRYPTO_KEY

app = FastAPI(
    title='crypto_service'
)


class CryptorEncryptor:
    def __init__(self, text: str, key: list):
        self.__text = [ord(i) for i in text]
        self.__key = key[:len(text)]

    def xor(self):
        return ''.join([chr(i ^ j) for i, j in zip(self.__text, self.__key)])


@app.get('/encrypt/')
@app.get('/crypt/')
async def crypt(crypto_string: str):
    try:
        return {'status': 200,
                'crypto_string': CryptorEncryptor(crypto_string, CRYPTO_KEY).xor()}
    except Exception as e:
        return {'status': 500,
                'error': str(e)}
