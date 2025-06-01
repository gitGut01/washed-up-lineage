from neo4j_integration.sql_datamodel_inserter import insert_datamodel_into_neo4j
from sql_datamodel_extraction.prompt import prompt as datamodel_prompt
from sql_datamodel_extraction.prompt_simple import prompt_simple as datamodel_prompt_simple
from sql_datamodel_extraction.feedback import feedback_template as datamodel_feedback_template
from shared.data_models import DataModel, DataModelSimple
from shared.validation import validate_output
from shared.extraction import extract_from_sql
from shared.processor import process_sql_files
from config import (
    DO_SIMPLE_EXTRACT,
)

# Data model validation and extraction functions moved from sql_datamodel_extraction/extract_and_process.py
def validate_datamodel_output(response_str, do_simple_extract:bool=DO_SIMPLE_EXTRACT):
    """Wrapper for shared validation with DataModel"""
    if do_simple_extract:
        return validate_output(response_str, DataModelSimple)
    return validate_output(response_str, DataModel)


def extract_datamodel_from_sql(
    sql_script, 
    do_simple_extract=False,
    max_attempts=3, 
    save_responses=True, 
    save_path=None, 
    sql_file_path=None, 
    load_from_file=False,
    ):
    """Extracts data model information using the generic extraction function.
    
    Args:
        sql_script: The SQL script containing data models to analyze
        max_attempts: Maximum number of extraction attempts
        save_responses: Whether to save extraction responses to files
        save_path: Path where to save extraction responses
        sql_file_path: Path of the original SQL file being processed
        load_from_file: Whether to load extraction from a saved file instead of using LLM
    
    Returns:
        A tuple of (DataModel or None, error_message or None, debug_info)
    """

    promp_to_use = datamodel_prompt_simple if do_simple_extract else datamodel_prompt
    model_class = DataModelSimple if do_simple_extract else DataModel

    return extract_from_sql(
        sql_script=sql_script,
        model_class=model_class,
        prompt_template=promp_to_use,
        feedback_template=datamodel_feedback_template,
        validation_func=validate_datamodel_output,
        max_attempts=max_attempts,
        save_responses=save_responses,
        save_path=save_path,
        sql_file_path=sql_file_path,
        load_from_file=load_from_file
    )


def process_datamodel_sql_files(directory, save_extraction_responses=False, use_already_extracted=False, extraction_runs_path=None, do_simple_extract=False):
    """Processes SQL files for data model extraction and updates Neo4j.
    
    Args:
        directory: Path to directory containing SQL files
        save_extraction_responses: Whether to save extraction responses to files
        use_already_extracted: Whether to use already extracted responses instead of LLM
        extraction_runs_path: Path to extraction runs directory, if None, will create a new one
        
    Returns:
        A tuple of (failed_scripts, processing_stats)
    """
    return process_sql_files(
        directory=directory,
        extraction_function=extract_datamodel_from_sql,
        neo4j_insert_function=insert_datamodel_into_neo4j,
        save_extraction_responses=save_extraction_responses,
        use_already_extracted=use_already_extracted,
        extraction_runs_path=extraction_runs_path,
        do_simple_extract=do_simple_extract
    )
