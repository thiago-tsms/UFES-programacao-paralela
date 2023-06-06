#!/bin/bash

n_clientes=$1
max_rounds=$2
metaAcuracia=$3

echo "Executando Tarefa com (3, 6, 9) Clientes e um máximo de $max_rounds Rounds e $metaAcuracia de acurácia"

echo "\n*Iniciando execução: $n_clientes\n"
for i in $(seq $n_clientes); do
    python execucao.py $n_clientes $max_rounds $metaAcuracia &
done

echo "\n*Finalizando execução: $n_clientes\n"

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait