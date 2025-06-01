from neo4j_integration.base_connector import driver
from neo4j_integration.utils import create_node_elements, create_edge_elements
from concurrent.futures import ThreadPoolExecutor

def fetch_object_lineage_edges_upstream(node_name):
    query = """
        MATCH path = (start {name: $node_name})-[:UPSTREAM_MODEL*]->(other)
        UNWIND relationships(path) AS rel
        WITH DISTINCT start, startNode(rel) AS sourceNode, endNode(rel) AS targetNode, rel
        WHERE NOT (sourceNode:StoredProcedure AND targetNode.name = $node_name)
        OPTIONAL MATCH (targetNode)-[r2:UPSTREAM_MODEL]->(sourceNode)
        WITH sourceNode, targetNode, r2,
            CASE 
                WHEN (sourceNode:StoredProcedure OR targetNode:StoredProcedure) AND r2 IS NOT NULL THEN 'bi'
                WHEN sourceNode:StoredProcedure THEN 'dash'
                ELSE null
            END AS line_mode
        WHERE 
            line_mode IS NULL
            OR line_mode = 'dash'
            OR (line_mode = 'bi' AND sourceNode:StoredProcedure)
        RETURN DISTINCT
            sourceNode.name AS source,
            targetNode.name AS target,
            'UPSTREAM' AS direction,
            sourceNode.name + '.' + targetNode.name AS id,
            line_mode
    """
    with driver.session() as session:
        result = session.run(query, node_name=node_name)
        return create_edge_elements(result)



def fetch_object_lineage_edges_downstream(node_name):
    query = """
        MATCH path = (start {name: $node_name})<-[:UPSTREAM_MODEL*]-(other)
        UNWIND relationships(path) AS rel
        WITH DISTINCT start, startNode(rel) AS sourceNode, endNode(rel) AS targetNode, rel
        WHERE NOT (targetNode:StoredProcedure AND sourceNode.name = $node_name)
        OPTIONAL MATCH (targetNode)-[r2:UPSTREAM_MODEL]->(sourceNode)
        WITH sourceNode, targetNode, r2,
            CASE 
                WHEN (sourceNode:StoredProcedure OR targetNode:StoredProcedure) AND r2 IS NOT NULL THEN 'bi'
                WHEN sourceNode:StoredProcedure THEN 'dash'
                ELSE null
            END AS line_mode
        WHERE 
            line_mode IS NULL
            OR line_mode = 'dash'
            OR (line_mode = 'bi' AND sourceNode:StoredProcedure)
        RETURN DISTINCT
            sourceNode.name AS source,
            targetNode.name AS target,
            'DOWNSTREAM' AS direction,
            sourceNode.name + '.' + targetNode.name AS id,
            line_mode
    """
    with driver.session() as session:
        result = session.run(query, node_name=node_name)
        return create_edge_elements(result)



def fetch_nodes_by_name_list(node_names):
    query = """
        MATCH (n)
        WHERE n.name IN $node_names
        RETURN
            n.name AS name,
            n.node_type as node_type,
            n.type as type,
            n.warehouse as warehouse,
            n.schema as schema,
            n.object as object
    """

    with driver.session() as session:
        result = session.run(query, node_names=node_names)
        return create_node_elements(result)
        

def fetch_object_lineage(node_name):
    edges = fetch_object_lineage_edges(node_name)

    node_names = set()
    for edge in edges:
        node_names.add(edge['data']["source"])
        node_names.add(edge['data']["target"])
    
    nodes = fetch_nodes_by_name_list(list(node_names))
    return nodes + edges


def fetch_object_lineage_edges(node_name):
    with ThreadPoolExecutor() as executor:
        downstream_edges_future = executor.submit(fetch_object_lineage_edges_downstream, node_name)
        upstream_edges_future = executor.submit(fetch_object_lineage_edges_upstream, node_name)
        downstream_edges = downstream_edges_future.result()
        upstream_edges = upstream_edges_future.result()
    
    # Combine all edges
    all_edges = upstream_edges + downstream_edges
    
    return all_edges
