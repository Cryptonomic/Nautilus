import sqlite3


DATABASE_PATH = "./node_database.db"


def setup_database():
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """CREATE TABLE IF NOT EXISTS 'nodes' (
        name VARCHAR PRIMARY KEY,
        arronax_port INTEGER,
        conseil_port INTEGER,
        node_port INTEGER,
        network VARCHAR,
        history_mode VARCHAR,
        status VARCHAR 
        );"""
    cursor.execute(command)
    database.commit()


def is_name_taken(name):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT name FROM 'nodes' WHERE name="{}";""".format(name)
    cursor.execute(command)
    return not cursor.fetchall() == []


def get_node_names():
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT name FROM 'nodes';"""
    cursor.execute(command)
    data = cursor.fetchall()
    output = list()
    for item in data:
        output.append(item[0])
    return output


def result_to_dict(data):
    output = dict()
    output['name'] = data[0]
    output['arronax_port'] = data[1]
    output['conseil_port'] = data[2]
    output['node_port'] = data[3]
    output['network'] = data[4]
    output['history_mode'] = data[5]
    output['status'] = data[6]
    return output


def get_node_data(name):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT * FROM 'nodes' WHERE nodes.name="{}";""".format(name)
    cursor.execute(command)
    return result_to_dict(cursor.fetchone())


def add_node(data):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """INSERT INTO 'nodes' VALUES ("{}", {}, {}, {}, "{}", "{}", "{}");""".format(
        data["name"],
        data["arronax_port"],
        data["conseil_port"],
        data["node_port"],
        data["network"],
        data["history_mode"],
        data["status"]
    )
    cursor.execute(command)
    database.commit()


def get_status(name):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT status FROM 'nodes' WHERE name="{}";""".format(name)
    cursor.execute(command)
    result = cursor.fetchone()
    return result[0]

def get_network(name):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT network FROM 'nodes' WHERE name="{}";""".format(name)
    cursor.execute(command)
    result = cursor.fetchone()
    return result[0]


def update_status(name, status):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """UPDATE 'nodes' SET status="{}" WHERE name="{}";""".format(status, name)
    cursor.execute(command)
    database.commit()


def get_max_node_port():
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """SELECT MAX(node_port) FROM 'nodes';"""
    cursor.execute(command)
    result = cursor.fetchone()
    return result[0]


def remove_node(name):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    command = """DELETE FROM 'nodes' WHERE name="{}";""".format(name)
    cursor.execute(command)
    database.commit()
