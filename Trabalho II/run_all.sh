#!/bin/bash

max_rounds=25
meta_acuracia=0.999

echo "Executando Treinamento com (4, 6, 8, 10) Clientes e um máximo de $max_rounds Rounds e meta de $meta_acuracia de acurácia"

for i in 4 6 8 10; do
    sh run.sh $i $max_rounds $meta_acuracia
    sleep 5
done