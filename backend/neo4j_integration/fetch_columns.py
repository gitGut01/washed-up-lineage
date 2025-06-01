# Import shared Neo4j connection
from neo4j_integration.base_connector import driver
from neo4j_integration.utils import create_node_elements, create_edge_elements


def fetch_columns(datamodel_name):
    """
    Fetches all columns for a specific datamodel.
    
    Args:
        datamodel_name: The name of the datamodel.
        
    Returns:
        list: A list of node elements representing columns.
    """
    query = """
        MATCH (d:DataModel {name: $datamodel_name})-[:HAS_COLUMN]->(c:Column)
        RETURN 
            c.name as name,
            c.original_name as original_name,
            c.type as type,
            c.is_type_guessed AS is_type_guessed,
            c.is_type_updated AS is_type_updated,
            c.datamodel_name AS datamodel_name,
            c.original_datamodel_name AS original_datamodel_name,
            c.node_type AS node_type,
            c.transformations as transformations,
            c.warehouse AS warehouse,
            c.schema AS schema,
            c.object AS object,
            c.object_type AS object_type
    """
    with driver.session() as session:
        result = session.run(query, datamodel_name=datamodel_name)
        return create_node_elements(result)


def fetch_column_lineage_nodes(name):
    """
    Fetches a column and all related upstream and downstream columns.
    
    Args:
        name: The name of the column.
        
    Returns:
        list: A list of node elements representing the column lineage.
    """
    query = """
        // Column <n> itself
        MATCH (a:Column)
        WHERE a.name = $name
        RETURN DISTINCT
            a.name AS name,
            a.original_name AS original_name,
            a.type AS type,
            a.is_type_guessed AS is_type_guessed,
            a.is_type_updated AS is_type_updated,
            a.datamodel_name AS datamodel_name,
            a.original_datamodel_name AS original_datamodel_name,
            a.node_type AS node_type,
            a.transformations AS transformations,
            a.warehouse AS warehouse,
            a.schema AS schema,
            a.object AS object,
            a.object_type AS object_type

        UNION

        // Upstream columns
        MATCH (a:Column)-[:UPSTREAM_COLUMN*]->(b:Column)
        WHERE a.name = $name
        RETURN DISTINCT
            b.name AS name,
            b.original_name AS original_name,
            b.type AS type,
            b.is_type_guessed AS is_type_guessed,
            b.is_type_updated AS is_type_updated,
            b.datamodel_name AS datamodel_name,
            b.original_datamodel_name AS original_datamodel_name,
            b.node_type AS node_type,
            b.transformations AS transformations,
            b.warehouse AS warehouse,
            b.schema AS schema,
            b.object AS object,
            b.object_type AS object_type
        UNION

        // Downstream columns
        MATCH (a:Column)<-[:UPSTREAM_COLUMN*]-(b:Column)
        WHERE a.name = $name
        RETURN DISTINCT
            b.name AS name,
            b.original_name AS original_name,
            b.type AS type,
            b.is_type_guessed AS is_type_guessed,
            b.is_type_updated AS is_type_updated,
            b.datamodel_name AS datamodel_name,
            b.original_datamodel_name AS original_datamodel_name,
            b.node_type AS node_type,
            b.transformations AS transformations,
            b.warehouse AS warehouse,
            b.schema AS schema,
            b.object AS object,
            b.object_type AS object_type
    """
    with driver.session() as session:
        result = session.run(query, name=name)
        return create_node_elements(result)


def fetch_column_lineage_edges(name):
    """
    Fetches the relationships between a column and its upstream/downstream columns.
    
    Args:
        name: The name of the column.
        
    Returns:
        list: A list of edge elements representing the relationships.
    """
    query = """
        // Downstream to column <name>
        MATCH p=(start:Column)-[:UPSTREAM_COLUMN*]->(end:Column)
        WHERE end.name = $name
        UNWIND relationships(p) AS rel
        RETURN 
            startNode(rel).name AS source,
            endNode(rel).name AS target,
            toLower(type(rel)) AS relationship,
            'DOWNSTREAM' AS direction

        UNION

        // Upstream from column <name>
        MATCH p=(start:Column)-[:UPSTREAM_COLUMN*]->(end:Column)
        WHERE start.name = $name
        UNWIND relationships(p) AS rel
        RETURN 
            startNode(rel).name AS source,
            endNode(rel).name AS target,
            toLower(type(rel)) AS relationship,
            'UPSTREAM' AS direction
    """

    with driver.session() as session:
        result = session.run(query, name=name)
        return create_edge_elements(result)
