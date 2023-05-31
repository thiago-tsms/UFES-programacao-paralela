#!/bin/bash

python codigo.py &
python codigo.py &
python codigo.py &

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait