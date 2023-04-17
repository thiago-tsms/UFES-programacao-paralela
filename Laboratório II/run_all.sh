#!/bin/bash

echo "Executando Tarefa com (2, 5, 10, 20, 40) Rounds"

for i in 2 5 10 20 40; do
    echo "\nIniciando execução: $i\n"
    sh run.sh $i
    echo "\nFinalizando execução: $i\n"
    sleep 5
done