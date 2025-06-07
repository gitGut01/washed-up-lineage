import os
import json
from pathlib import Path
import glob
import tqdm

from data_models import StoredProcedure, DataModel
from json_to_graph.neo4j_integration.base_connector import reset_neo4j_database
from json_to_graph.neo4j_integration.sql_stored_procedure_inserter import insert_procedure_into_neo4j
from json_to_graph.neo4j_integration.sql_datamodel_inserter import insert_datamodel_into_neo4j

from json_to_graph.neo4j_integration.post_processing.add_metadata_to_columns import add_metadata_to_columns
from json_to_graph.neo4j_integration.post_processing.connect_orphaned_columns import connect_orphaned_columns
from json_to_graph.neo4j_integration.post_processing.classify_column_types import classify_column_types
from json_to_graph.neo4j_integration.post_processing.classify_datamodel_types import classify_datamodel_types
from json_to_graph.neo4j_integration.post_processing.propagate_column_types import propagate_column_types
from json_to_graph.neo4j_integration.post_processing.create_indices_from_names import create_indices_from_names

from logger import logg_print
from config import (
    DEFAULT_EXTRACTION_DIR, 
    PATH_EXTRACTION_RUNS
)


def get_latest_response(file_path:str):
    current_dir = '/'.join(str(file_path).split("/")[:-1]) + '/'
    base_name = str(file_path).split(".")[-3]

    pattern = os.path.join(current_dir, f'{base_name}.sql_response_*.json')
    matches = glob.glob(pattern)
    matches.sort()

    if str(file_path) == matches[-1]: return file_path
    return None


def load_json_files(directory, logger):
    dir_path = Path(directory).resolve()

    for file_path in tqdm.tqdm(list(Path(dir_path).glob('**/*.json'))):
        latest_response_file_path = get_latest_response(file_path)
        if latest_response_file_path is None:
            continue
    
        try:
            with open(latest_response_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

                if json_data["data"]["type"] == 'stored_procedure':
                    stored_procedure = StoredProcedure(**json_data["data"])
                    insert_procedure_into_neo4j(stored_procedure)
                    logger.info(f"Success inserting: {stored_procedure.name} [stored_procedure]")
                elif json_data["data"]["type"] in ['table', 'view']:
                    datamodel = DataModel(**json_data["data"])
                    insert_datamodel_into_neo4j(datamodel)
                    logger.info(f"Success inserting: {datamodel.name} [{datamodel.type}]")
                
        except Exception as e:
            logger.error(f"Failed inserting: {latest_response_file_path}")

def json_to_graph(logger):

    dir_path = os.path.join(DEFAULT_EXTRACTION_DIR, PATH_EXTRACTION_RUNS)
    
    logg_print(logger, "----- JSON to Neo4j ----")
    reset_neo4j_database()
    load_json_files(dir_path, logger)

    print()
    logg_print(logger, "----- Post processing ----")
    propagate_column_types(logger)
    classify_datamodel_types(logger)
    classify_column_types(logger)
    connect_orphaned_columns(logger)
    add_metadata_to_columns(logger)
    create_indices_from_names(logger)
    logg_print(logger, "")


