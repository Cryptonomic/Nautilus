import secrets
import os
import threading
import atexit
import docker
from app.worker import main
from app import start

APP_PATH = os.getcwd() + "/app"

def start_worker():
    password = secrets.token_urlsafe(32)
    password_file = open("redis_password.txt", "w+")
    password_file.write(password)
    password_file.close()

    thread = threading.Thread(target=main())
    thread.daemon = True
    thread.start()


@atexit.register
def cleanup():
    docker_client = docker.from_env()
    docker_client.containers.remove("nautilus-core-redis")


if __name__ == '__main__':
    os.chdir(APP_PATH)
    start_worker()
    start()

