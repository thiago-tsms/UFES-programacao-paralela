from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509 import CertificateBuilder
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.x509.oid import NameOID
import datetime


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


    # Descriptografa usando chave privada local
    def descritografar(self, data):
        return self.__private_key.decrypt(
            bytes.fromhex(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode('utf-8')

    # Efetua a assinatura de uma mensagem
    def assinar_mensagem(self, data):
        return self.__private_key.sign(
            bytes(data, "utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ).hex()
        
    # Verifica a assinatura de uma mensagem
    def verificar_assinatura(self, public_key, data, signature):
        pk = serialization.load_pem_public_key(
            bytes.fromhex(public_key),
            backend=default_backend(),
        )
        try:
            pk.verify(
                bytes.fromhex(signature),
                bytes(data, "utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
    
    # Gera um certificado digital
    def gerar_certificado_digital(self, id):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.USER_ID, str(id)),
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Espirito Santo"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Vitoria"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Universidade Federal do Espirito Santo (Ufes)"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"UFES"),
        ])

        cert_builder = x509.CertificateBuilder()
        cert_builder = cert_builder.subject_name(subject)
        cert_builder = cert_builder.issuer_name(issuer)
        cert_builder = cert_builder.public_key(self.__public_key)
        cert_builder = cert_builder.serial_number(x509.random_serial_number())
        cert_builder = cert_builder.not_valid_before(datetime.datetime.utcnow())
        cert_builder = cert_builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        cert_builder = cert_builder.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        cert_builder = cert_builder.sign(self.__private_key, hashes.SHA256(), default_backend())

        return cert_builder.public_bytes(Encoding.PEM)
    
    # Verifica um certificado digital
    def verificar_certificado_digital(self, certificate):
        loaded_certificate = x509.load_pem_x509_certificate(certificate, default_backend())

        current_time = datetime.datetime.utcnow()
        if loaded_certificate.not_valid_before <= current_time <= loaded_certificate.not_valid_after:
            return True
        else:
            return False