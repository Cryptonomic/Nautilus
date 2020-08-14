import redis
import time
from util.app_functions import setup_job_queue_server
from rq import Worker, Queue, Connection

# Imports for the job queue worker
import docker
import os
from conseil import conseil
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

listen = ['default']

redis_url = 'redis://localhost:6379'

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    setup_job_queue_server()
    time.sleep(1)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
