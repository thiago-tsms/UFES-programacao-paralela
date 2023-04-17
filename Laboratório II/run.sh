
#!/bin/bash

echo "Iniciando Execução com $1 rounds"

echo "Iniciando Servidor"
python server.py $1 &

sleep 3  # Aguarda 10s antes de iniciar os clientes

for i in `seq 1 5`; do
    echo "Iniciando Cliente: $i"
    python client.py &
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait