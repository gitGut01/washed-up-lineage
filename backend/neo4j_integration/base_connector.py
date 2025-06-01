from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neo4j Connection details from environment variables
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Create the driver instance
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Method to check connection and verify credentials
def verify_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                return True, "Connection successful"
            return False, "Connection returned invalid data"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
