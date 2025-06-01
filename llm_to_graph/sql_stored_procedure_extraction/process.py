from neo4j_integration.sql_stored_procedure_inserter import insert_procedure_into_neo4j
from shared.data_models import StoredProcedure, StoredProcedureSimple
from shared.validation import validate_output
from shared.extraction import extract_from_sql
from shared.processor import process_sql_files
from sql_stored_procedure_extraction.feedback import feedback_template as procedure_feedback_template
from sql_stored_procedure_extraction.prompt import prompt as procedure_prompt
from sql_stored_procedure_extraction.prompt_simple import prompt_simple as procedure_prompt_simple
from config import (
    DO_SIMPLE_EXTRACT
)

# Stored procedure validation and extraction functions moved from sql_stored_procedure_extraction/extract_and_process.py
def validate_procedure_output(response_str, do_simple_extract:bool=DO_SIMPLE_EXTRACT):
    """Wrapper for shared validation with StoredProcedure"""
    if do_simple_extract:
        return validate_output(response_str, StoredProcedureSimple)
    return validate_output(response_str, StoredProcedure)


def extract_procedures_from_sql(
    sql_script, 
    do_simple_extract=False,
    max_attempts=3, 
    save_responses=True, 
    save_path=None, 
    sql_file_path=None, 
    load_from_file=False,
    ):
    """Extracts stored procedure information using the generic extraction function.
    
    Args:
        sql_script: The SQL script containing stored procedures to analyze
        max_attempts: Maximum number of extraction attempts
        save_responses: Whether to save extraction responses to files
        save_path: Path where to save extraction responses
        sql_file_path: Path of the original SQL file being processed
        load_from_file: Whether to load extraction from a saved file instead of using LLM
    
    Returns:
        A tuple of (StoredProcedure or None, error_message or None, debug_info)
    """

    promp_to_use = procedure_prompt_simple if do_simple_extract else procedure_prompt
    model_class = StoredProcedureSimple if do_simple_extract else StoredProcedure

    return extract_from_sql(
        sql_script=sql_script,
        model_class=model_class,
        prompt_template=promp_to_use,
        feedback_template=procedure_feedback_template,
        validation_func=validate_procedure_output,
        max_attempts=max_attempts,
        save_responses=save_responses,
        save_path=save_path,
        sql_file_path=sql_file_path,
        load_from_file=load_from_file
    )


def process_stored_procedures_from_sql(directory_path, save_extraction_responses=False, use_already_extracted=False, extraction_runs_path=None, do_simple_extract=False):
    """
    Process stored procedure SQL files and extract their datamodel and lineage.
    
    Args:
        directory_path: Path to the directory containing stored procedure SQL files
        
    Returns:
        Tuple of (failed_scripts, processing_stats)
    """
    # Create a wrapper function for the Neo4j inserter that includes the warehouse parameter
    def insert_wrapper(stored_procedure):
        return insert_procedure_into_neo4j(stored_procedure)
        
    
    return process_sql_files(
        directory=directory_path,
        extraction_function=extract_procedures_from_sql,
        neo4j_insert_function=insert_wrapper,
        save_extraction_responses=save_extraction_responses,
        use_already_extracted=use_already_extracted,
        extraction_runs_path=extraction_runs_path,
        do_simple_extract=do_simple_extract
    )
