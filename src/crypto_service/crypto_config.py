from random import randint

KEY_LEN = 512
CRYPTO_KEY = [randint(0, 1000000) for i in range(KEY_LEN)]
