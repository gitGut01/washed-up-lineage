from data_models import DataModel
from json_to_graph.split_warehouse_schema_object import split_warehouse_schema_object, get_id_name
from json_to_graph.neo4j_integration.sql_column_inserter import insert_column, insert_downstream_columns
from json_to_graph.neo4j_integration.base_connector import driver
from config import DEFAULT_WAREHOUSE, DO_SIMPLE_EXTRACT

def insert_datamodel(session, full_object_name:str, datamodel_type:str): 
    datamodel_type = datamodel_type.lower()
    if datamodel_type not in ["table", "view"]:
        print(full_object_name, "yooo")
    
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
            o.type = $datamodel_type,
            o.is_external = $is_external
        """,
        {
            "name": id_name,
            "original_object_name": full_object_name,
            "warehouse": warehouse,
            "schema": schema,
            "object": object,
            "datamodel_type": datamodel_type,
            "is_external": is_external,
        }
    )



def insert_downstream_datamodels(session, datamodel: DataModel):
    if not datamodel.downstream_models:
        return
    
    warehouse, schema, object  = split_warehouse_schema_object(datamodel.name)
    datamodel_id_name = get_id_name(warehouse, schema, object)

    for downstream_model in datamodel.downstream_models:
        warehouse, schema, object  = split_warehouse_schema_object(downstream_model)
        downstream_model_id_name = get_id_name(warehouse, schema, object)
        
        # Use the provided session parameter instead of creating a new one
        session.run(
            """
            MATCH (d:DataModel {name: $current_model_name})

            MERGE (t:DataModel {name: $downstream_name})
            SET 
                t.original_name = $original_downstream_name,
                t.warehouse = $warehouse,
                t.schema = $schema,
                t.object = $object

            MERGE (t)-[:UPSTREAM_MODEL]->(d)
            """,
            {
                "current_model_name": datamodel_id_name,
                "downstream_name": downstream_model_id_name,
                "original_downstream_name": downstream_model,
                "warehouse": warehouse,
                "schema": schema,
                "object": object
            }
        )


def insert_datamodel_into_neo4j(datamodel: DataModel):
    with driver.session() as session:
        
        insert_datamodel(session, datamodel.name, datamodel.type)
        insert_downstream_datamodels(session, datamodel)
        
        if not DO_SIMPLE_EXTRACT:
            if datamodel.columns:
                for column in datamodel.columns:
                    insert_column(session, column, datamodel.name)
                    insert_downstream_columns(session, column, datamodel.name)
