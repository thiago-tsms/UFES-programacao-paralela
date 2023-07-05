from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.hazmat.backends import default_backend

class Security():


    def __init__(self):
        self.__private_key = None
        self.__public_key = None
        self.__private_key_hex = None
        self.public_key_hex = None
        self.generate_key_pair()
     
    # Gera pares de chaves
    def generate_key_pair(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537, 
            key_size=2048
        )

        self.__public_key = self.__private_key.public_key()

        self.public_key_hex = self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM, 
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).hex()

        self.__private_key_hex = self.__private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).hex()
    

    # Criptografa mensagen com uso de chave pública
    def criptografar(self, data, public_key):
        pk = serialization.load_pem_public_key(
            bytes.fromhex(public_key),
            backend=default_backend(),
        )

        return pk.encrypt(
            data.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).hex()


    # Descriptografa usando cha privada local
    def descritografar(self, data):
        return self.__private_key.decrypt(
            bytes.fromhex(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode('utf-8')

