import sqlite3


DATABASE_PATH = "./node_database.db"


def execute(command):
    database = sqlite3.connect(DATABASE_PATH)
    cursor = database.cursor()
    cursor.execute(command)
    database.commit()
    return cursor.fetchall()


def setup_database():
    command = """CREATE TABLE IF NOT EXISTS 'nodes' (
        name VARCHAR PRIMARY KEY,
        arronax_port INTEGER,
        conseil_port INTEGER,
        node_port INTEGER,
        network VARCHAR,
        history_mode VARCHAR,
        status VARCHAR 
        );"""
    execute(command)


def is_name_taken(name):
    command = """SELECT name FROM 'nodes' WHERE name="{}";""".format(name)
    return not execute(command) == []


def get_node_names():
    command = """SELECT name FROM 'nodes';"""
    data = execute(command)
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
    command = """SELECT * FROM 'nodes' WHERE nodes.name="{}";""".format(name)
    return result_to_dict(execute(command)[0])


def add_node(data):
    command = """INSERT INTO 'nodes' VALUES ("{}", {}, {}, {}, "{}", "{}", "{}");""".format(
        data["name"],
        data["arronax_port"],
        data["conseil_port"],
        data["node_port"],
        data["network"],
        data["history_mode"],
        data["status"]
    )
    execute(command)


def get_status(name):
    command = """SELECT status FROM 'nodes' WHERE name="{}";""".format(name)
    return execute(command)[0]


def get_network(name):
    command = """SELECT network FROM 'nodes' WHERE name="{}";""".format(name)
    return execute(command)[0]


def update_status(name, status):
    command = """UPDATE 'nodes' SET status="{}" WHERE name="{}";""".format(status, name)
    execute(command)


def get_max_node_port():
    command = """SELECT MAX(node_port) FROM 'nodes';"""
    return execute(command)[0]


def remove_node(name):
    command = """DELETE FROM 'nodes' WHERE name="{}";""".format(name)
    execute(command)
