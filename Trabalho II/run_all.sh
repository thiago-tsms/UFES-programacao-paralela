#!/bin/bash

max_rounds=10
meta_acuracia=0.99

echo "Executando Treinamento com (4, 6, 8) Clientes e um máximo de $max_rounds Rounds e meta de $meta_acuracia de acurácia"

for i in 4 6 8; do
    sh run.sh $i $max_rounds $meta_acuracia
    sleep 5
done