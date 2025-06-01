"""
Shared utility functions for Neo4j data handling and transformation.
"""

def create_node_elements(results):
    """
    Creates node elements from Neo4j query results.
    
    Args:
        results: A Neo4j query result containing node data
        
    Returns:
        list: A list of node elements in the format expected by the frontend
    """
    if not results:
        return []

    elements = []
    for result in results:
        record = dict(result)
        data = {
            "id": record["name"],
        }

        for k, v in record.items():
            # Deduplicate transformations by converting to a set and back to a list
            if k == "transformations" and v is not None:
                data[k] = list(set(v))
            else:
                data[k] = v

        elements.append({"data": data, "group": "nodes"})

    return elements



def create_edge_elements(result):
    return [
        {
            "data": dict(record),
            "group": "edges"
        }
        for record in result
    ]

def create_edge_elements_2(result):
    """
    Creates edge elements from Neo4j query results.
    
    Args:
        result: A Neo4j query result containing relationship data with source and target.
               May include a relationship field to specify the relationship type.
        
    Returns:
        list: A list of edge elements in the format expected by the frontend
    """
    if not result: 
        return []
        
    elements = []
    for record in result:
        edge_data = {
            "id": f'{record["source"]}.{record["target"]}',
            "source": record["source"],
            "target": record["target"],
        }
        
        for k, v in record.items():
            edge_data[k] = v
            
        elements.append({
            "data": edge_data,
            "group": "edges"
        })

    return elements
