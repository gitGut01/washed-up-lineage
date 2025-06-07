from json_to_graph.neo4j_integration.base_connector import driver
from json_to_graph.split_warehouse_schema_object import split_warehouse_schema_object, get_id_name
from logger import logg_print

def connect_orphaned_columns(logger):
    """
    Post-processing step to connect orphaned columns to their respective data models.
    
    This function identifies column nodes that don't have an incoming HAS_COLUMN relationship
    (orphaned columns) and connects them to the appropriate DataModel nodes.
    
    It uses the existing split_warehouse_schema_object function to extract datamodel components
    from column names rather than doing this parsing in Cypher.
    """
    try:
        # Use a single session for the entire operation
        with driver.session() as session:
            # Step 1: Find all orphaned columns
            orphaned_columns = []
            result = session.run(
                """
                // Find all columns without an incoming HAS_COLUMN relationship
                MATCH (c:Column)
                WHERE NOT ()-[:HAS_COLUMN]->(c)
                RETURN c.name as column_name
                """
            )
            
            for record in result:
                orphaned_columns.append(record["column_name"])
                
            total_columns = session.run("MATCH (c:Column) RETURN count(c) as total").single()["total"]
            
            if not orphaned_columns:
                logg_print(logger, f"☑️ Found {total_columns} total Column nodes, 0 orphaned columns to connect")
                return
                
            connected_count = 0
                
            # Step 2: Process each orphaned column using Python logic
            for column_name in orphaned_columns:
                # Extract the last part as the actual column name
                parts = column_name.split('.')
                if len(parts) < 3:
                    # Not enough parts to determine datamodel
                    continue
                    
                # The last part is the column name
                actual_column_name = parts[-1]
                
                # Use our existing function to extract the datamodel parts
                # Column name follows format WAREHOUSE.SCHEMA.TABLE.COLUMN
                # So to get datamodel, we join all but the last part
                datamodel_name_parts = '.'.join(parts[:-1])
                
                # Get the standardized datamodel name
                warehouse, schema, object_name = split_warehouse_schema_object(datamodel_name_parts)
                datamodel_name = get_id_name(warehouse, schema, object_name)
                
                # Now connect the column to its datamodel (using the same session)
                result = session.run(
                    """
                    // Find the datamodel and orphaned column
                    MATCH (d:DataModel {name: $datamodel_name})
                    MATCH (c:Column {name: $column_name})
                    WHERE NOT ()-[:HAS_COLUMN]->(c)
                    
                    // Connect them and update properties
                    MERGE (d)-[:HAS_COLUMN]->(c)
                    
                    // Update properties to match columns created through insert_column
                    // LEAVE original_name INTACT
                    SET c.datamodel_name = d.name,
                        c.original_datamodel_name = d.original_name,
                        c.is_type_guessed = COALESCE(c.is_type_guessed, true),
                        c.is_type_updated = COALESCE(c.is_type_updated, false)
                    
                    RETURN count(c) as connected
                    """,
                    {"datamodel_name": datamodel_name, "column_name": column_name}
                )
                
                record = result.single()
                if record and record["connected"] > 0:
                    connected_count += 1
            
            # Print the single line summary
            logg_print(logger, f"☑️ Found {total_columns} total Column nodes, successfully connected {connected_count} orphaned columns")
                
    except Exception as e:
        logg_print(logger, f"❌ Error connecting orphaned columns: {e}")
