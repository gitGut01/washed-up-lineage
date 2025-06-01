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


def create_name_indexes():
    """
    Create indexes on the name property for all node types to speed up lookups and traversals.
    This should be called after the database is populated but before queries are run.
    """
    with driver.session() as session:
        # Create index for DataModel nodes
        session.run("CREATE INDEX IF NOT EXISTS FOR (n:DataModel) ON (n.name)")
        
        # Create index for StoredProcedure nodes
        session.run("CREATE INDEX IF NOT EXISTS FOR (n:StoredProcedure) ON (n.name)")
        
        # Create index for Column nodes
        session.run("CREATE INDEX IF NOT EXISTS FOR (n:Column) ON (n.name)")
        
        # If you've unified DataModel and StoredProcedure into Objects as per memory
        session.run("CREATE INDEX IF NOT EXISTS FOR (n:Object) ON (n.name)")
        
        print("Created indexes on name property for all node types")
