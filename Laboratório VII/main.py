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

    signature = sec.assinar_mensagem(json.dumps(data))
    status = sec.verificar_assinatura(sec.public_key_hex, json.dumps(data), signature)
    print(status)

    certificado = sec.gerar_certificado_digital(1)
    sec.verificar_certificado_digital(certificado)
    #print(certificado)


if __name__ == '__main__':
    run()