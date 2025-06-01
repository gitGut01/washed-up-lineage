
from neo4j_integration.base_connector import driver
from shared.data_models import Column
from shared.split_warehouse_schema_object import split_warehouse_schema_object, get_id_name


def get_transformations(column: Column):
    transformations = []
    
    if not column.downstream_columns: return []
    for downstream_column in column.downstream_columns:
        if not downstream_column: continue
        for transformation in downstream_column.transformations:
            transformations.append(transformation.upper())
    
    return transformations


def insert_column(session, column: Column, datamodel_name: str):
    warehouse, schema, object = split_warehouse_schema_object(datamodel_name)
    datamodel_id_name = get_id_name(warehouse, schema, object)
    column_id_name = f"{datamodel_id_name}.{column.name.upper()}"

    transformations = get_transformations(column)

    # Use the provided session instead of creating a new one
    session.run(
        """
        MATCH (d:DataModel {name: $datamodel_name})

        MERGE (t:Column {name: $column_name})
        SET t.original_name = $original_name,
            t.original_datamodel_name = $original_datamodel_name,
            t.type = $type,
            t.is_type_guessed = false,
            t.is_type_updated = false,
            t.datamodel_name = $datamodel_name,
            t.transformations = $transformations

        MERGE (d)-[:HAS_COLUMN]->(t)
        """,
        {
            "datamodel_name": datamodel_id_name,
            "original_datamodel_name": datamodel_name,
            "column_name": column_id_name,
            "original_name": column.name,
            "type": column.type,
            "transformations": transformations
        }
    )
        

def insert_downstream_columns(session, column: Column, datamodel_name: str):
    warehouse, schema, object = split_warehouse_schema_object(datamodel_name)
    current_datamodel_id_name = get_id_name(warehouse, schema, object)
    current_column_id_name = f"{current_datamodel_id_name}.{column.name.upper()}"

    if not column.downstream_columns:
        return

    for downstream_column in column.downstream_columns:
        warehouse, schema, object = split_warehouse_schema_object(downstream_column.datamodel)
        downstream_datamodel_id_name = get_id_name(warehouse, schema, object)
        downstream_column_id_name = f"{downstream_datamodel_id_name}.{downstream_column.name.upper()}"

        # Use the provided session instead of creating a new one
        session.run(
            """
            MATCH (d:Column {name: $current_column_name})

            MERGE (t:Column {name: $downstream_column_name})
            SET t.original_name = $original_downstream_name

            MERGE (t)-[:UPSTREAM_COLUMN]->(d)
            """,
            {
                "current_column_name": current_column_id_name,
                "downstream_column_name": downstream_column_id_name,
                "original_downstream_name": downstream_column.name
            }
        )