from crypto import *
import json
from json import JSONEncoder


def run():
    sec = Security()

    data = {
        "msg": "Funcionando"
    }
    ciphertext = sec.criptografar(json.dumps(data), sec.public_key_hex)
    print(json.loads(sec.descritografar(ciphertext)))


if __name__ == '__main__':
    run()