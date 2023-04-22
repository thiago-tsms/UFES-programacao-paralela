# LABORATÓRIO I

### Problema de ordenação de um vetor executado com diferente número de threads

Para executar o programa: <br/>
<ul>
    <li>requisitos: <em>sudo apt-get install time</em></li>
    <li>compilação: <em>cc -pthread main.c -o m</em></li>
    <li>execução: <em>./m (numero de elementos) (nomero de threads)</em></li>
    <li>execução do script: <em>sh run.sh</em></li>
</ul>

Para diferentes parâmetros altere o script

Colab: https://colab.research.google.com/drive/1O5kP5IiOXUDI-Jcwl8j3blBKsdyk-Oe4?usp=share_link


# LABORATÓRIO II

### Experimentar o treinamento de modelos de aprendizado de máquina por meio do framework de aprendizado flwr e comparar os resultados atingidos pelo modelo treinado de maneira local e federada.

Requisitos: **python** e **pip** instalados

Para executar o programa:
<ul>
    <li>criar ambiente: <em>python -m venv .venv</em></li>
    <li>ativar ambiente: <em>source .venv/bin/activate</em></li>
    <li>configurar ambiente: <em>pip install -r requirements.txt</em></li>
    <li>executar: <em>jupyter notebook</em></li>
</ul>

Para executar a simulação:
<ul>
    <li>ativar ambiente virtual: <em>source .venv/bin/activate</em></li>
    <li>executar um teste com *n* ronds: <em>sh run.sh (número de rounds)</em></li>
    <li>executar teste com (2, 5, 10, 20, 40) rounds: <em>sh run_all.sh</em></li>
</ul>

São usados 5 cliente e um servidor


# LABORATÓRIO III