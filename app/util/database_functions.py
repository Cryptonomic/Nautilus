import sqlite3

DATABASE_PATH = "./node_database.db"


def setup_database():
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """CREATE TABLE IF NOT EXISTS 'nodes' (
        name VARCHAR PRIMARY KEY,
        rpc_port INTEGER,
        exposition_port INTEGER,
        conseil_port INTEGER,
        arronax_port INTEGER,
        postgres_port INTEGER,
        network VARCHAR,
        history_mode VARCHAR,
        status VARCHAR 
        );"""
    cursor.execute(command)
    database.commit()
    print("Database Setup")


def get_all_nodes():
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """SELECT name FROM 'nodes';"""
    cursor.execute(command)
    return cursor.fetchall()


def result_to_dict(data):
    output = dict()
    output['name'] = data[0]
    output['rpc_port'] = data[1]
    output['exposition_port'] = data[2]
    output['conseil_port'] = data[3]
    output['arronax_port'] = data[4]
    output['postgres_port'] = data[5]
    output['network'] = data[6]
    output['history_mode'] = data[7]
    output['status'] = data[8]
    return output


def get_node_data(name):
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """SELECT * FROM 'nodes' WHERE nodes.name="{}";""".format(name)
    cursor.execute(command)
    return result_to_dict(cursor.fetchone())


def add_node(data):
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """INSERT INTO 'nodes' VALUES ("{}", {}, {}, {}, {}, {}, "{}", "{}", "{}");""".format(
        data["name"],
        data["rpc_port"],
        data['exposition_port'],
        data["conseil_port"],
        data["arronax_port"],
        data["postgres_port"],
        data["network"],
        data["history_mode"],
        data["status"]
    )
    cursor.execute(command)
    database.commit()


def update_status(name, status):
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """UPDATE 'nodes' SET status="{}" WHERE name="{}";""".format(status, name)
    cursor.execute(command)
    database.commit()


def get_max_port():
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """SELECT MAX(postgres_port) FROM 'nodes';"""
    cursor.execute(command)
    result = cursor.fetchone()
    if result[0] == None:
        return 50000
    return result[0]


def remove_node(name):
    database = sqlite3.connect(DATABASE_PATH)  # opens existing file or it makes new one if it does not exit
    cursor = database.cursor()
    command = """DELETE FROM 'nodes' WHERE name="{}";""".format(name)
    cursor.execute(command)
    database.commit()
