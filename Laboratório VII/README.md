# Laboratório VII - Assinaturas Digitais

Objetivos
* Reimplementar o protótipo desenvolvido no Laboratório VI, considerando aspectos de Assinatura
Digital na troca de mensagem entre os pares;
* Explorar bibliotecas na linguagem de programação Python para geração de chaves criptográficas
assimétricas, criptografia e descriptografia, assinatura e geração de certificados digitais;
* Experimentar a verificação de assinaturas de mensagens por meio de chaves públicas/ privadas;


# Integrantes

* ... - ... - Thiago ...
* 2022241702 - Doutorado - Vitor Fontana Zanotelli 

# Introdução

O objetivo desse trabalho é implementar uma simulação simples de um cenário de mineração de criptomoedas utilizando o modelo de comunicação Publish/Subscribe através do protocolo MQTT para a troca de mensagens entre os participantes. Uma camada adicional de segurança é feita através do uso de assinatura digital nas mensagens. Para isso foi implementada uma autoridade certificadora onde são armazenadas as chaves públicas dos participantes, dessa forma permitindo a verificação da origem das mensagens trocadas entre os participantes e impedindo, por exemplo, que algum participante se passe por outro.

# Requisitos e Execução do código

Requisitos: python e pip instalados

Para executar o ambiente:

* criar ambiente: python -m venv .venv
* ativar ambiente: source .venv/bin/activate
* configurar ambiente: pip install -r requirements.txt

# Detalhes de Implementação 

As bibliotecas principais utilizadas para esse trabalho são:

* [cryptography](https://pypi.org/project/cryptography/): funções de criptografia e assinatura de mensagens;
* [paho-mqtt](https://pypi.org/project/paho-mqtt/): client para o mqtt.

# Resultados e Discussões

...
