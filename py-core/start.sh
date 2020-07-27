#!/bin/bash

python3 -m venv ./venv || (echo "Python virtual environment not setup properly ... Is python3 installed?" ; exit 1)

source ./venv/bin/activate || (echo "Python virtual environment not setup properly ... Is python3 installed?" ; exit 1)

pip3 install -r requirements.txt || (echo "Cannot install pip3 requirements ... Is python3 installed?" ; exit 1)

cd app/ || (echo "Cannot find root app directory ... The installation may be corrupted, you may want to try reinstalling" ; exit 1)

python3 __init__.py || (echo "Cannot run main python script ... Is python3 installed? ... The installation may be corrupted, you may want to try reinstalling" ; exit 1)