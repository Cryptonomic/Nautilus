import redis
import time
import logging

from util.app_functions import setup_job_queue_server
from rq import Worker, Queue, Connection

# Imports for the job queue worker
import docker
import os
from conseil import conseil
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Logging variables
LOGGING_FILE_PATH = "./logs/logs.txt"
LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"

logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)

listen = ['default']

redis_url = 'localhost'
port = 6379

try:
    conn = redis.Redis(
        host=redis_url,
        port=port,
        password="conseil"
    )
except:
    print("Connection Error to Redis")
    exit(1)

if __name__ == '__main__':
    setup_job_queue_server()
    time.sleep(1)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
