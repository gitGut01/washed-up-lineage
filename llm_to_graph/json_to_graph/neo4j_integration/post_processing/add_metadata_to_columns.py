from json_to_graph.neo4j_integration.base_connector import driver
from logger import logg_print

def add_metadata_to_columns(logger):
    """Add warehouse, schema, and object metadata to columns by traversing the HAS_COLUMN relationship in reverse.
    For each column, find the object node that has the column via the HAS_COLUMN relationship
    and add the warehouse, schema, and object properties to the column.
    """
    
    with driver.session() as session:
        # Get all columns and their parent objects
        result = session.run("""
        MATCH (obj)-[:HAS_COLUMN]->(col:Column)
        RETURN col.name as column_name, obj.warehouse as warehouse, obj.schema as schema, obj.object as object, obj.type as object_type
        """)
        
        for record in result:
            column_name = record["column_name"]
            warehouse = record["warehouse"]
            schema = record["schema"]
            object_name = record["object"]
            object_type = record["object_type"]
            
            try:
                # Update the column with warehouse, schema, and object information directly from parent object
                session.run("""
                MATCH (col:Column {name: $column_name})
                SET col.warehouse = $warehouse,
                    col.schema = $schema,
                    col.object = $object,
                    col.object_type = $object_type
                """, {
                    "column_name": column_name,
                    "warehouse": warehouse,
                    "schema": schema,
                    "object": object_name,
                    "object_type": object_type
                })
            except Exception as e:
                logg_print(logger, f"❌ Error adding metadata to column {column_name}: {e}")
    
    logg_print(logger, "☑️ Finished adding metadata to columns")