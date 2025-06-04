"""
This module provides generic SQL file processing functionality.
It handles reading, processing, and reporting on SQL files for various extraction types.
"""

import os
import re
import sys
import time
import datetime
from typing import Callable, Dict, List, Tuple, Any, Optional
from datetime import timedelta

from shared.token_estimation import calculate_token_costs
from shared.extraction import DEFAULT_EXTRACTION_DIR

def setup_extraction_runs_path(save_extraction_responses: bool, use_already_extracted: bool, extraction_runs_path: Optional[str] = None) -> Optional[str]:
    """Sets up the extraction runs path for saving or loading extraction responses.
    
    Args:
        save_extraction_responses: Whether to save extraction responses
        use_already_extracted: Whether to use already extracted responses
        extraction_runs_path: Optional specific path to use
        
    Returns:
        The path to use for saving/loading extraction responses, or None if not needed
    """
    if not (save_extraction_responses or use_already_extracted):
        return None
        
    if extraction_runs_path is None:
        # Create a new timestamp directory for this run
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_runs_path = os.path.join(DEFAULT_EXTRACTION_DIR, timestamp)
    
    # Create directory if it doesn't exist
    os.makedirs(extraction_runs_path, exist_ok=True)
    print(f"{'Using' if use_already_extracted else 'Created'} extraction runs directory: {extraction_runs_path}")
    
    return extraction_runs_path


def process_sql_files(
    directory: str,
    extraction_function: Callable,
    neo4j_insert_function: Callable,
    save_extraction_responses: bool = False,
    use_already_extracted: bool = False,
    extraction_runs_path: Optional[str] = None,
    do_simple_extract: bool = False
) -> Tuple[List[Dict], Dict]:
    """Generic processor for SQL files with extraction and Neo4j insertion.
    
    Args:
        directory: Path to directory containing SQL files
        extraction_function: Function to extract structured data from SQL
        neo4j_insert_function: Function to insert extracted data into Neo4j
        save_extraction_responses: Whether to save extraction responses to files
        use_already_extracted: Whether to use already extracted responses instead of LLM
        extraction_runs_path: Path to extraction runs directory, if None, will create a new one
        
    Returns:
        Tuple of (failed_scripts, processing_stats)
    """
     
    # Set up extraction runs path
    extraction_runs_path = setup_extraction_runs_path(
        save_extraction_responses=save_extraction_responses and not use_already_extracted,  # Don't save if we're loading
        use_already_extracted=use_already_extracted,
        extraction_runs_path=extraction_runs_path
    )
        
    # Count total SQL files first
    total_files = 0
    sql_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sql"):
                total_files += 1
                sql_files.append(os.path.join(root, file))
    
    print(f"\nFound {total_files} SQL files to process\n")
    
    # Process each file with progress counter
    failed_scripts = []
    total_start_time = time.time()
    processing_stats = {
        "total_files": total_files,
        "success_count": 0,
        "failed_count": 0,
        "start_time": total_start_time,
        "input_token_count": 0,
        "input_cost": 0,
        "output_token_count": 0,
        "output_cost": 0,
    }
    
    for count, file_path in enumerate(sql_files, 1):
        # Start timing
        start_time = time.time()
        
        print(f"\n[{count}/{total_files}] Processing: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
            # Update additional args with file path and extraction options
            extraction_kwargs = {}
            
            # Add extraction options if we have an extraction runs path
            if extraction_runs_path:
                extraction_kwargs.update({
                    # Only save if save_extraction_responses is True and we're not loading from files
                    "save_responses": save_extraction_responses and not use_already_extracted,
                    "load_from_file": use_already_extracted,
                    "save_path": extraction_runs_path,
                    "sql_file_path": file_path
                })

            # Call the extraction function with the SQL script and any additional args
            extracted_data, error_message, debug_info = extraction_function(sql_script, do_simple_extract, **extraction_kwargs)
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            time_str = str(timedelta(seconds=round(elapsed)))
            
            if extracted_data:
                # Insert into Neo4j if successful
                neo4j_insert_function(extracted_data)
                print(f"✅ Processed in {time_str}")
                processing_stats["success_count"] += 1
            else:
                # Store failed script info with detailed debug information
                failed_scripts.append({
                    "file_path": file_path,
                    "error_message": error_message,
                    "debug_info": debug_info
                })
                processing_stats["failed_count"] += 1
                print(f"❌ Failed in {time_str} - Error: {error_message}")
                
                # Show reasoning from the agent's attempts if available
                if debug_info and "reasoning" in debug_info and debug_info["reasoning"]:
                    # Extract just the analysis and strategy sections to keep output manageable
                    reasoning = debug_info["reasoning"][0]
                    analysis_match = re.search(r'Step 1: ERROR ANALYSIS\s*(.+?)Step 2:', reasoning, re.DOTALL)
                    strategy_match = re.search(r'Step 3: STRATEGY\s*(.+?)Step 4:', reasoning, re.DOTALL)
                    
                    if analysis_match or strategy_match:
                        print("\n💭 Agent's analysis:")
                        if analysis_match:
                            print(f"   {analysis_match.group(1).strip()}")
                        if strategy_match:
                            print("\n🔍 Agent's strategy:")
                            print(f"   {strategy_match.group(1).strip()}")
                    print("\n")

            # Calculate token costs
            input_token_count, input_cost, _ = calculate_token_costs(sql_script)
            output_token_count, _, output_cost = calculate_token_costs(extracted_data.json())

            print(
                f"Input/Output token count: {input_token_count}/{output_token_count} "
                f"(cost ${input_cost:.6f}/${output_cost:.6f})"
            )
            
            processing_stats["input_token_count"] += input_token_count
            processing_stats["input_cost"] += input_cost
            processing_stats["output_token_count"] += output_token_count
            processing_stats["output_cost"] += output_cost
            
    
    # Report summary with timing statistics
    total_time = time.time() - processing_stats["start_time"]
    processing_stats["total_time"] = total_time
    processing_stats["time_str"] = str(timedelta(seconds=round(total_time)))
    
    print(f"\n=== PROCESSING SUMMARY ===")
    print(f"Total files processed: {processing_stats['total_files']}")
    success_percentage = processing_stats['success_count']/total_files*100 if total_files > 0 else 0
    failed_percentage = processing_stats['failed_count']/total_files*100 if total_files > 0 else 0
    print(f"Successfully processed: {processing_stats['success_count']} ({success_percentage:.1f}%)")
    print(f"Failed: {processing_stats['failed_count']} ({failed_percentage:.1f}%)")
    print(f"Total time: {processing_stats['time_str']}")
    
    # Report details of failures if any
    if failed_scripts:
        print("\nFAILED SQL SCRIPTS:")
        print("===================")
        for i, failed in enumerate(failed_scripts):
            print(f"{i+1}. {failed['file_path']}")
            print(f"   Error: {failed['error_message']}")
    
    return failed_scripts, processing_stats
