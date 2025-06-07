"""
Base Neo4j connector that provides shared connection and database operations
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j Configuration from environment variables
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Create a shared driver instance
driver = GraphDatabase.driver(uri, auth=(username, password))

def reset_neo4j_database():
    """
    Reset the Neo4j database by removing all nodes and relationships.
    This is a shared operation that can be used by any module.
    """
    with driver.session() as session:
        session.run(
            "match (a) -[r] -> () delete a, r"
        )

        session.run(
            "match (a) delete a"
        )

def get_driver():
    """
    Returns the Neo4j driver instance to be used by specific modules.
    """
    return driver
