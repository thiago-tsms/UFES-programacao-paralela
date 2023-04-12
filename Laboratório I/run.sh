#!/bin/bash

for n in $(seq 100000 100000 1000000); do
    for p in 2 4 8 16; do
        echo "Tamanho:$n - Processos:$p"
        time -a -o ./log.dat -f "$n;$p;%e" ./m $n $p;
    done
done