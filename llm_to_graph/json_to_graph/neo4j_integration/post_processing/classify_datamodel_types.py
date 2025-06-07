from json_to_graph.neo4j_integration.base_connector import driver
from logger import logg_print

def classify_datamodel_types(logger):
    """
    Classifies DataModel nodes in Neo4j as:
    - Root: nodes with no upstream models (no incoming UPSTREAM_MODEL relationships)
    - Leaf: nodes with no downstream models (no outgoing UPSTREAM_MODEL relationships)
    - Normal: nodes that have both upstream and downstream models
    
    This classification is set in a property called 'node_type' for each DataModel.
    """
    with driver.session() as session:
        # Identify and mark root nodes (nodes with no upstream models)
        session.run(
            """
            MATCH (model:DataModel)
            WHERE NOT EXISTS { MATCH (model)<-[:UPSTREAM_MODEL]-() }
            SET model.node_type = "ROOT"
            RETURN count(model) as root_count
            """
        )

        # Identify and mark leaf nodes (nodes with no downstream models)
        session.run(
            """
            MATCH (model:DataModel)
            WHERE NOT EXISTS { MATCH (model)-[:UPSTREAM_MODEL]->() }
            SET model.node_type = "LEAF"
            RETURN count(model) as leaf_count
            """
        )

        # Mark all remaining nodes as normal (have both upstream and downstream)
        session.run(
            """
            MATCH (model:DataModel)
            WHERE 
              EXISTS { MATCH (model)<-[:UPSTREAM_MODEL]-() } AND
              EXISTS { MATCH (model)-[:UPSTREAM_MODEL]->() }
            SET model.node_type = "NORMAL"
            RETURN count(model) as normal_count
            """
        )

        # Get statistics for each node type
        result = session.run(
            """
            MATCH (model:DataModel)
            RETURN 
              model.node_type as node_type, 
              count(model) as count
            ORDER BY node_type
            """
        )
        
        stats = {}
        for record in result:
            node_type = record["node_type"] if record["node_type"] else "UNCLASSIFIED"
            stats[node_type] = record["count"]
        
        logg_print(logger, f"☑️ Node classification complete:")
        for node_type, count in stats.items():
            logg_print(logger, f"  - {node_type}: {count} nodes")
