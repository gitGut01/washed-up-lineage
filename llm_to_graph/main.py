import time

from print_util import print_summary
from neo4j_integration.base_connector import reset_neo4j_database, create_name_indexes
from neo4j_integration.post_processing.propagate_column_types import propagate_column_types
from neo4j_integration.post_processing.classify_datamodel_types import classify_datamodel_types
from neo4j_integration.post_processing.classify_column_types import classify_column_types
from neo4j_integration.post_processing.connect_orphaned_columns import connect_orphaned_columns
from neo4j_integration.post_processing.add_metadata_to_columns import add_metadata_to_columns

from sql_datamodel_extraction.process import process_datamodel_sql_files
from sql_stored_procedure_extraction.process import process_stored_procedures_from_sql

from setup_extraction_environment import setup_extraction_environment

from config import (
    DO_SIMPLE_EXTRACT, 
    DATAMODEL_SQL_PATHTS, 
    STORED_PROCEDURE_SQL_PATHS,
    DO_RESET_NEO4J_DATABASE
)

def proccess_by_path(
    sql_paths,
    save_extraction_responses,
    use_already_extracted,
    extraction_runs_path,
    overall_stats,
    extraction_type:str = 'datamodel' 
    
):
    all_failed_scripts = []
    
    
    for sql_path in sql_paths:

        if extraction_type == 'datamodel':
            print(f"\n=== DATAMODEL EXTRACTION [{sql_path}] ===")
            func_process_sql_files = process_datamodel_sql_files

        elif extraction_type == 'stored_procedure':
            print(f"\n=== STORED PROCEDURE EXTRACTION [{sql_path}] ===")
            func_process_sql_files = process_stored_procedures_from_sql


        failed_scripts, processing_stats = func_process_sql_files(
                sql_path,
                save_extraction_responses=save_extraction_responses,
                use_already_extracted=use_already_extracted,
                extraction_runs_path=extraction_runs_path,
                do_simple_extract=DO_SIMPLE_EXTRACT
            )

        all_failed_scripts.extend(failed_scripts)

        
        # Aggregate statistics
        overall_stats["total_files"] += processing_stats["total_files"]
        overall_stats["success_count"] += processing_stats["success_count"]
        overall_stats["failed_count"] += processing_stats["failed_count"]

        overall_stats["input_token_count"] += processing_stats["input_token_count"]
        overall_stats["input_cost"] += processing_stats["input_cost"]
        overall_stats["output_token_count"] += processing_stats["output_token_count"]
        overall_stats["output_cost"] += processing_stats["output_cost"]
        
    return all_failed_scripts


def main():
    """Main function to orchestrate the extraction process."""
    # Configuration
    
    # Reset database and track time
    if DO_RESET_NEO4J_DATABASE:
        reset_neo4j_database()
    
    overall_start_time = time.time()
    
    # Initialize statistics
    overall_stats = {
        "total_files": 0,
        "success_count": 0,
        "failed_count": 0,
        "input_token_count": 0,
        "input_cost": 0,
        "output_token_count": 0,
        "output_cost": 0,
    }
    
    # Set up environment
    use_already_extracted, save_extraction_responses, timestamp, extraction_runs_path = \
        setup_extraction_environment()
    

    # Process stored procedure SQL paths
    stored_proc_failed_scripts = proccess_by_path(
        STORED_PROCEDURE_SQL_PATHS,
        save_extraction_responses, 
        use_already_extracted,
        extraction_runs_path,
        overall_stats,
        extraction_type = 'stored_procedure'
    )

    # Process datamodel SQL paths
    datamodel_failed_scripts = proccess_by_path(
        DATAMODEL_SQL_PATHTS,
        save_extraction_responses,
        use_already_extracted,
        extraction_runs_path,
        overall_stats,
        extraction_type = 'datamodel'
    )
    # Post processing steps:
    if len(DATAMODEL_SQL_PATHTS) > 0:
        propagate_column_types()
        classify_datamodel_types()
        classify_column_types()
        connect_orphaned_columns()
        add_metadata_to_columns()
        create_name_indexes()  # Create indexes on name property to speed up queries
    
    # Combine all failed scripts
    all_failed_scripts = datamodel_failed_scripts + stored_proc_failed_scripts
    
    # Calculate execution time
    overall_execution_time = time.time() - overall_start_time
    
    # Print summary
    print_summary(overall_stats, overall_execution_time)
    
    # Optionally export failed scripts
    # export_failed_scripts(all_failed_scripts)
    
    return all_failed_scripts, overall_stats


# Run the process when executed directly
if __name__ == "__main__":
    main()
