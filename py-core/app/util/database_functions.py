from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from util.tezos_node_functions import log_fatal_error

DATABASE_PATH = "/node_database.db"

# Setup code base for sqlalchemy
Base = declarative_base()
engine = create_engine('sqlite://{}'.format(DATABASE_PATH))
Session = sessionmaker(bind=engine)
session = Session()


class Node(Base):
    # Setup sqlalchemy tablename
    __tablename__ = "nodes"
    # Define table schema
    name = Column(String, primary_key=True)
    arronax_port = Column(Integer)
    conseil_port = Column(Integer)
    node_port = Column(Integer)
    network = Column(String)
    history_mode = Column(String)
    status = Column(String)


def get_new_session():
    try:
        engine = create_engine('sqlite://{}'.format(DATABASE_PATH))
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except Exception as e:
        log_fatal_error(e, "Could not retrieve local database session.")
        exit(1)


def setup_database():
    Base.metadata.create_all(engine)


def is_name_taken(name):
    query = get_new_session().query(Node).filter_by(name=name)
    return query.count() > 0


def get_node_names():
    query = get_new_session().query(Node.name).all()
    output = list()
    for node in query:
        output.append(node[0])
    return output


def result_to_dict(data):
    output = dict()
    output['name'] = data.name
    output['arronax_port'] = data.arronax_port
    output['conseil_port'] = data.conseil_port
    output['node_port'] = data.node_port
    output['network'] = data.network
    output['history_mode'] = data.history_mode
    output['status'] = data.status
    return output


def get_node_data(name):
    query = get_new_session().query(Node).filter_by(name=name).first()
    return result_to_dict(query)


def add_node(data):
    s = get_new_session()
    node = Node(name=data["name"],
                arronax_port=data["arronax_port"],
                conseil_port=data["conseil_port"],
                node_port=data["node_port"],
                network=data["network"],
                history_mode=data["history_mode"],
                status=data["status"]
                )
    s.add(node)
    s.commit()


def get_status(name):
    query = get_new_session().query(Node).filter_by(name=name).first()
    return query.status


def get_network(name):
    query = get_new_session().query(Node).filter_by(name=name).first()
    return query.network


def update_status(name, status):
    s = get_new_session()
    query = s.query(Node).filter_by(name=name).first()
    query.status = status
    s.commit()


def get_max_node_port():
    query = get_new_session().query(func.max(Node.node_port)).scalar()
    return query


def remove_node(name):
    s = get_new_session()
    s.query(Node).filter_by(name=name).delete()
    s.commit()
