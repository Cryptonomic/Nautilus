import os
import redis
from util.app_functions import setup_job_queue_server
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    setup_job_queue_server()
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()