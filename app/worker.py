import redis
import time
import logging
import secrets
import sys

from util.app_functions import setup_job_queue_server, log_fatal_error
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
    password_file = open("redis_password.txt", "r")
    password = password_file.read().strip()
    password_file.close()
except Exception as e:
    log_fatal_error(e, "Could not access password file.")
    exit(1)

try:
    conn = redis.Redis(
        host=redis_url,
        port=port,
        password=password
    )
except Exception as e:
    log_fatal_error(e, "Connect not connect to Redis instance started on Docker.")
    exit(1)

if __name__ == '__main__':
    setup_job_queue_server(password)
    time.sleep(1)
    with Connection(conn):
        try:
            worker = Worker(list(map(Queue, listen)))
            worker.work()
        except Exception as e:
            log_fatal_error(e, "Could not start job queue worker.")
            exit(1)
