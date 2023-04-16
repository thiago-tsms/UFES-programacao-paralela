
#!/bin/bash

echo "Starting server"
python server.py &
sleep 10  # Aguarda 10s antes de iniciar os clientes

for i in `seq 0 5`; do
    echo "Starting client $i"
    python client.py &
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait