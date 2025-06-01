from neo4j_integration.base_connector import driver
from neo4j_integration.utils import create_node_elements, create_edge_elements
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all_object_nodes():
    query = """
        MATCH (n)
        WHERE n:DataModel OR n:StoredProcedure
        RETURN
            n.name AS name,
            n.original_name AS original_name,
            n.node_type as node_type,
            n.type as type,
            n.warehouse AS warehouse,
            n.schema AS schema,
            n.object AS object,
            head(labels(n)) AS label
    """

    with driver.session() as session:
        result = session.run(query)
        return create_node_elements(result)



def fetch_all_object_edges():
    query = """
        MATCH (a)-[r:UPSTREAM_MODEL]->(b)
        WHERE 
            (a:DataModel OR a:StoredProcedure) AND 
            (b:DataModel OR b:StoredProcedure)
        OPTIONAL MATCH (b)-[r2:UPSTREAM_MODEL]->(a)
        WITH a, b, r, r2,
            CASE 
                WHEN (a:StoredProcedure OR b:StoredProcedure) AND r2 IS NOT NULL THEN 'bi'
                WHEN a:StoredProcedure THEN 'dash'
                ELSE null
            END AS line_mode
        WHERE 
            line_mode IS NULL
            OR line_mode = 'dash'
            OR (line_mode = 'bi' AND a:StoredProcedure)
        RETURN 
            a.name AS source,
            b.name AS target,
            toLower(type(r)) AS relationship,
            a.name + '.' + b.name AS id,
            line_mode
    """

    with driver.session() as session:
        result = session.run(query)
        return create_edge_elements(result)


def fetch_all_objects():

    with ThreadPoolExecutor() as executor:
        nodes_future = executor.submit(fetch_all_object_nodes)
        edges_future = executor.submit(fetch_all_object_edges)
        nodes = nodes_future.result()
        edges = edges_future.result()

    elements = nodes + edges
    return elements

def fetch_object_by_name(name):
    """
    Fetches a single data object (data model or stored procedure) by name.
    
    Args:
        name (str): The name of the data object to fetch.
        
    Returns:
        dict or None: A node element representing the data object, or None if not found.
    """
    query = """
        MATCH (n)
        WHERE n.name = $name AND (n:DataModel OR n:StoredProcedure)
        RETURN 
            n.name AS name,
            n.original_name AS original_name,
            n.node_type as node_type,
            n.type as type,
            n.warehouse AS warehouse,
            n.schema AS schema,
            n.object AS object,
            head(labels(n)) AS label
        LIMIT 1
    """

    with driver.session() as session:
        result = session.run(query, name=name)
        nodes = create_node_elements(result)
        return nodes[0] if nodes else None
