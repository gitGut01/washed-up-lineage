from json_to_graph.neo4j_integration.base_connector import driver
from logger import logg_print

def create_indices_from_names(logger):
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
        
        logg_print(logger, "☑️ Created indexes on name property for all node types")
