from neo4j_integration.base_connector import driver

def classify_column_types():
    """
    Classifies Column nodes in Neo4j as:
    - Root: columns with no upstream columns (no incoming UPSTREAM_COLUMN relationships)
    - Leaf: columns with no downstream columns (no outgoing UPSTREAM_COLUMN relationships)
    - Normal: columns that have both upstream and downstream columns
    
    This classification is set in a property called 'node_type' for each Column.
    """
    with driver.session() as session:
        # Identify and mark root columns (columns with no upstream columns)
        session.run(
            """
            MATCH (col:Column)
            WHERE NOT EXISTS { MATCH (col)<-[:UPSTREAM_COLUMN]-() }
            SET col.node_type = "ROOT"
            RETURN count(col) as root_count
            """
        )

        # Identify and mark leaf columns (columns with no downstream columns)
        session.run(
            """
            MATCH (col:Column)
            WHERE NOT EXISTS { MATCH (col)-[:UPSTREAM_COLUMN]->() }
            SET col.node_type = "LEAF"
            RETURN count(col) as leaf_count
            """
        )

        # Mark all remaining columns as normal (have both upstream and downstream)
        session.run(
            """
            MATCH (col:Column)
            WHERE 
              EXISTS { MATCH (col)<-[:UPSTREAM_COLUMN]-() } AND
              EXISTS { MATCH (col)-[:UPSTREAM_COLUMN]->() }
            SET col.node_type = "NORMAL"
            RETURN count(col) as normal_count
            """
        )

        # Get statistics for each column type
        result = session.run(
            """
            MATCH (col:Column)
            RETURN 
              col.node_type as node_type, 
              count(col) as count
            ORDER BY node_type
            """
        )
        
        stats = {}
        for record in result:
            node_type = record["node_type"] if record["node_type"] else "UNCLASSIFIED"
            stats[node_type] = record["count"]
        
        print(f"Column classification complete:")
        for node_type, count in stats.items():
            print(f"  - {node_type}: {count} columns")
