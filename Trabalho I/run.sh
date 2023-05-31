#!/bin/bash

max_rounds=20
metaAcuracia=1

echo "Executando Tarefa com (2, 4, 6, 8, 10) Clientes e um máximo de $max_rounds Rounds e $metaAcuracia de acurácia"

for n_clientes in 2 4 6 8 10; do

    # Inicia os clientes
    for j in $(seq $n_clientes); do
        python client.py &
    done

    sleep 5

    echo "\n*Iniciando execução: $n_clientes\n"
    python server.py $n_clientes $max_rounds $metaAcuracia
    echo "\n*Finalizando execução: $n_clientes\n"

    # Finaliza todos os clientes
    killall python
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait
