#!/bin/bash

echo "Executando Tarefa com (2, 5, 10, 20, 40) Rounds"


for i in $(seq 10); do

    # Inicia os clientes
    for j in $(seq $i); do
        python client.py &
    done

    sleep 5

    echo "\n*Iniciando execução: $i\n"
    python server.py $i 40
    echo "\n*Finalizando execução: $i\n"

    # Finaliza todos os clientes
    killall python
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait