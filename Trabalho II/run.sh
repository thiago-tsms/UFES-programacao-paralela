#!/bin/bash

is_agregador=1
not_agregador=0

grupo_1=1
grupo_2=2
n_clientes=$1
max_rounds=$2
meta_acuracia=$3

echo "**Executando Tarefa com 2 grupos de $n_clientes Clientes, máximo de $max_rounds Rounds, meta $meta_acuracia de acurácia \n"

echo "*Iniciando Agregador:\n"
python main.py $is_agregador 0 $n_clientes $max_rounds $meta_acuracia &

echo "*Iniciando Clientes:\n"
for i in $(seq $n_clientes); do
    python main.py $not_agregador $grupo_1 $n_clientes $max_rounds $meta_acuracia &
    python main.py $not_agregador $grupo_2 $n_clientes $max_rounds $meta_acuracia &
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait

echo "**Finalizando Execução: $n_clientes\n"