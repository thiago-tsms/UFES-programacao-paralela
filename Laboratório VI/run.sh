#!/bin/bash

n_clientes=2


for n_c in $(seq $n_clientes); do
    python client.py &
done


# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait