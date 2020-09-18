from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


def setup_database():
    Base.metadata.create_all(engine)


def is_name_taken(name):
    query = session.query(Node).filter_by(name=name)
    return query.count() > 0


def get_node_names():
    query = session.query(Node.name).all()
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
    query = session.query(Node).filter_by(name=name).first()
    return result_to_dict(query)


def add_node(data):
    node = Node(name=data["name"],
                arronax_port=data["arronax_port"],
                conseil_port=data["conseil_port"],
                node_port=data["node_port"],
                network=data["network"],
                history_mode=data["history_mode"],
                status=data["status"]
                )
    session.add(node)
    session.commit()


def get_status(name):
    query = session.query(Node).filter_by(name=name).first()
    return query.status


def get_network(name):
    query = session.query(Node).filter_by(name=name).first()
    return query.network


def update_status(name, status):
    query = session.query(Node).filter_by(name=name).first()
    query.status = status
    session.commit()


def get_max_node_port():
    query = session.query(func.max(Node.node_port)).scalar()
    return query


def remove_node(name):
    session.query(Node).filter_by(name=name).delete()
    session.commit()
