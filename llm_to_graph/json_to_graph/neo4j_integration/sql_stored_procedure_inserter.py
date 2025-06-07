from typing import List
from data_models import StoredProcedure
from json_to_graph.split_warehouse_schema_object import split_warehouse_schema_object, get_id_name
from json_to_graph.neo4j_integration.base_connector import driver

from config import DEFAULT_WAREHOUSE

def insert_stored_procedure(session, stored_procedure: StoredProcedure):
    warehouse, schema, object  = split_warehouse_schema_object(stored_procedure.name)
    id_name = get_id_name(warehouse, schema, object)

    # Insert the stored procedure node
    session.run(
        """
        MERGE (p:StoredProcedure {name: $name})
        SET p.original_name = $original_name,
            p.warehouse = $warehouse,
            p.schema = $schema,
            p.object = $object,
            p.node_type = 'StoredProcedure',
            p.type = 'StoredProcedure'
        """,
        {
            "name": id_name,
            "original_name": stored_procedure.name,
            "warehouse": warehouse,
            "schema": schema,
            "object": object
        }
    )


# Process source objects (UPSTREAM_STORED_PROCEDURE)
def insert_datamodel_reads_from(session, stored_procedure_name:str, source_objects: List[str]):
    warehouse, schema, object  = split_warehouse_schema_object(stored_procedure_name)
    procedure_id_name = get_id_name(warehouse, schema, object)

    for source_object in source_objects:
        full_object_name = source_object
        insert_sp_adjacent_datamodel(session, full_object_name)

        warehouse, schema, object  = split_warehouse_schema_object(full_object_name)
        reads_from_id_name = get_id_name(warehouse, schema, object)

        # Create the UPSTREAM_STORED_PROCEDURE relationship
        session.run(
            f"""
            MATCH (p:StoredProcedure {{name: $procedure_name}})
            MATCH (o:DataModel {{name: $object_name}})
            MERGE (o)-[:UPSTREAM_MODEL]->(p)
            """,
            {
                "procedure_name": procedure_id_name,
                "object_name": reads_from_id_name
            }
        )
            

def insert_datamodel_writes_to(session, stored_procedure_name: str, target_objects: List[str]):
    warehouse, schema, object  = split_warehouse_schema_object(stored_procedure_name)
    procedure_id_name = get_id_name(warehouse, schema, object)

    for target_object in target_objects:
        full_object_name = target_object
        insert_sp_adjacent_datamodel(session, full_object_name)

        warehouse, schema, object  = split_warehouse_schema_object(full_object_name)
        writes_to_id_name = get_id_name(warehouse, schema, object)

        # Create the UPSTREAM_MODEL relationship
        session.run(
            f"""
            MATCH (p:StoredProcedure {{name: $procedure_name}})
            MATCH (o:DataModel {{name: $object_name}})
            MERGE (p)-[:UPSTREAM_MODEL]->(o)
            """,
            {
                "procedure_name": procedure_id_name,
                "object_name": writes_to_id_name
            }
        )


def insert_sp_adjacent_datamodel(session, full_object_name:str): 
    
    warehouse, schema, object = split_warehouse_schema_object(full_object_name)
    id_name = get_id_name(warehouse, schema, object)
    is_external = False if warehouse.upper() == DEFAULT_WAREHOUSE.upper() else True

    session.run(
        f"""
        MERGE (o:DataModel {{name: $name}})
        SET o.original_name = $original_object_name,
            o.warehouse = $warehouse,
            o.schema = $schema,
            o.object = $object,
            o.is_external = $is_external
        """,
        {
            "name": id_name,
            "original_object_name": full_object_name,
            "warehouse": warehouse,
            "schema": schema,
            "object": object,
            "is_external": is_external,
        }
    )


def insert_procedure_into_neo4j(stored_procedure: StoredProcedure):
    with driver.session() as session:
        insert_stored_procedure(session, stored_procedure)
        insert_datamodel_reads_from(session, stored_procedure.name, stored_procedure.source_objects)
        insert_datamodel_writes_to(session, stored_procedure.name, stored_procedure.target_objects)

