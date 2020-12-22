#!/bin/bash

source ./venv/bin/activate || (echo "Python virtual environment not setup properly ... Is python3 installed?" ; exit 1)

cd app/ || (echo "Cannot find root app directory ... The installation may be corrupted, you may want to try reinstalling" ; exit 1)

REDIS_PASS=$(openssl rand -base64 6)

touch redis_password.txt

echo "$REDIS_PASS" > redis_password.txt

python3 worker.py "$REDIS_PASS" || (echo "Cannot run main python script ... Is python3 installed? ... The installation may be corrupted, you may want to try reinstalling" ; exit 1)