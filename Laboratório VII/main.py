from crypto import *
from mqtt import *
import json
from json import JSONEncoder


def run():
    sec = Security()
    sec2 = Security()

    data = {
        "msg": "Funcionando"
    }
    
    # Criptografia
    #ciphertext = sec.criptografar(json.dumps(data), sec.public_key_hex)
    #print(json.loads(sec.descritografar(ciphertext)))

    # Cria certificado
    certificado = sec.gerar_certificado_digital(1, sec.public_key_hex)
    certificado2 = sec.gerar_certificado_digital(2, sec2.public_key_hex)

    # Mensagem assinada
    signature = sec.assinar_mensagem(json.dumps(data))

    # Verificação com certificado 1 (sec.public_key_hex)
    chave = sec.obter_public_key_certificado_digital(certificado)
    status = sec.verificar_assinatura(chave, json.dumps(data), signature)
    print(status)

    # Verificação com certificado 2
    chave2 = sec2.obter_public_key_certificado_digital(certificado2)
    status = sec2.verificar_assinatura(chave2, json.dumps(data), signature)
    print(status)


if __name__ == '__main__':
    run()