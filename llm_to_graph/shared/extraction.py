"""
This module contains core extraction logic for SQL structures.
It handles extraction processes and self-correction mechanisms for different SQL components.
"""

import os
import json
import datetime
from typing import Dict, Optional, Tuple, Type
from pydantic import BaseModel
from langchain_core.prompts.chat import ChatPromptTemplate
from shared.data_models import DataModel, DataModelSimple, StoredProcedure, StoredProcedureSimple
from config import (
    DEFAULT_EXTRACTION_DIR
)

# Import LLM client
from shared.llm_client import LLMClient
from config import DEFAULT_EXTRACTION_DIR

# Initialize LLM 
llm_client = LLMClient()
initialized_llm = llm_client.get_model()



def get_extraction_file_path(sql_file_path: str, save_path: str, attempt: Optional[int] = None) -> str:
    """
    Generates the appropriate file path for saving/loading extraction results.
    
    Args:
        sql_file_path: Path to the original SQL file
        save_path: Base directory for saving extraction results
        attempt: Attempt number, if None, returns the base path
        
    Returns:
        Path to the extraction file
    """
    # Create directory structure that mirrors the SQL file's structure
    # We need to extract the relevant portion of the path
    
    # If the sql_file_path contains 'sql_scripts' folder, extract from there
    # This ensures we preserve the structure like sql_scripts/TortoiseRacing/kpi
    sql_dir = os.path.dirname(sql_file_path)
    
    # Find the position of 'sql_scripts' in the path
    sql_scripts_index = sql_file_path.find('sql_scripts')
    
    if sql_scripts_index != -1:
        # Extract the path starting from 'sql_scripts'
        preserved_path = sql_dir[sql_scripts_index:]
    else:
        # Fallback: use the last 3 path components if sql_scripts not found
        path_components = sql_dir.split(os.sep)
        preserved_path = os.path.join(*path_components[-3:]) if len(path_components) >= 3 else os.path.join(*path_components)
    
    sql_filename = os.path.basename(sql_file_path)
    response_dir = os.path.join(save_path, preserved_path)
    
    # Create directories if they don't exist
    os.makedirs(response_dir, exist_ok=True)
    
    # Base response file path without attempt number
    response_base = os.path.join(response_dir, f"{sql_filename}_response")
    
    # Return with attempt if provided, otherwise return the base
    if attempt is not None:
        return f"{response_base}_{attempt}.json"
    return response_base


def load_extraction_from_file(model_class: Type[BaseModel], sql_file_path: str, save_path: str, max_attempts: int) -> Tuple[Optional[BaseModel], Optional[str], Dict]:
    """
    Attempts to load extraction results from a file.
    
    Args:
        model_class: The Pydantic model class for validation and parsing
        sql_file_path: Path to the original SQL file
        save_path: Directory containing saved extraction results
        max_attempts: Maximum number of extraction attempts to check for
        
    Returns:
        Tuple of (Extracted model or None, error_message or None, debug_info)
    """
    # Initialize debug info
    debug_info = {"attempts": []}
    
    # Generate base path for response files
    response_base = get_extraction_file_path(sql_file_path, save_path)
    # Try to find the latest successful response file
    for attempt in range(max_attempts, 0, -1):
        file_path = f"{response_base}_{attempt}.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                    parsed_json = response_data.get('data', {})
                    
                    # Add to debug info
                    debug_info["attempts"].append({
                        "type": "loaded-from-file",
                        "file": file_path,
                        "response": json.dumps(parsed_json)
                    })
                    
                    # Return the loaded model
                    return model_class(**parsed_json), None, debug_info
            except Exception as e:
                # Continue trying other files if this one fails
                debug_info["attempts"].append({
                    "type": "file-load-error",
                    "file": file_path,
                    "error": str(e)
                })
    
    # If we get here, no valid response file was found
    return None, "No valid response file found", debug_info


def save_extraction_to_file(parsed_json: Dict, sql_file_path: str, save_path: str, attempt: int) -> bool:
    """
    Saves extraction results to a file.
    
    Args:
        parsed_json: The parsed JSON data to save
        sql_file_path: Path to the original SQL file
        save_path: Directory to save extraction results
        attempt: The attempt number
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Generate file path for this attempt
        file_path = get_extraction_file_path(sql_file_path, save_path, attempt)
        
        # Create a dictionary with metadata and the parsed data
        save_data = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "attempt": attempt,
                "sql_file": sql_file_path
            },
            "data": parsed_json
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Failed to save response to file: {str(e)}")
        return False


def extract_with_llm(sql_script: str, model_class: Type[BaseModel], prompt_template: ChatPromptTemplate, 
                   feedback_template: ChatPromptTemplate, validation_func, max_attempts: int,
                   save_responses: bool, save_path: Optional[str], sql_file_path: Optional[str]) -> Tuple[Optional[BaseModel], Optional[str], Dict]:
    """
    Extracts data from SQL using LLM with self-correction.
    
    Args:
        sql_script: The SQL script to analyze
        model_class: The Pydantic model class for validation and parsing
        prompt_template: The initial prompt template for extraction
        feedback_template: The feedback template for retry attempts
        validation_func: The validation function to use
        max_attempts: Maximum number of extraction attempts
        save_responses: Whether to save extraction responses to files
        save_path: Path where to save extraction responses
        sql_file_path: Path of the original SQL file being processed
        
    Returns:
        A tuple of (Extracted model or None, error_message or None, debug_info)
    """
    # Debug information to track extraction process
    debug_info = {"attempts": []}
    
    # Initial extraction chain
    extraction_chain = prompt_template | initialized_llm
    
    # Track previous attempts and errors
    previous_output = None
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            # Log retry attempts
            if attempt > 0:
                print(f"  Retry {attempt}/{max_attempts-1} with self-correction...")
                
                # Create a feedback chain for retry with self-correction
                feedback_chain = feedback_template | initialized_llm
                
                # Invoke feedback chain with previous errors
                response = feedback_chain.invoke({
                    "sql_script": sql_script,
                    "previous_output": previous_output,
                    "error_message": last_error,
                    "schema": model_class.schema_json(indent=2)
                })
            else:
                # First attempt with original prompt
                response = extraction_chain.invoke({"sql_script": sql_script})
            
            # Store response for debugging
            response_content = response.content if hasattr(response, 'content') else str(response)
            debug_info["attempts"].append({
                "type": f"attempt-{attempt+1}", 
                "response": response_content
            })
            
            # Store for potential next retry
            previous_output = response_content
            
            # Validate and parse the output
            success, error, parsed_json = validation_func(response_content)
            
            if success:
                # Successfully parsed output
                # Save successful response to file if requested
                if save_responses and save_path and sql_file_path:
                    save_extraction_to_file(parsed_json, sql_file_path, save_path, attempt+1)
                        
                return model_class(**parsed_json), None, debug_info
            else:
                # Store error for next retry
                last_error = error
                print(f"  Extraction error: {error}")
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            print(f"  Exception: {last_error}")
    
    # If we've exhausted all attempts
    return None, f"Failed after {max_attempts} attempts. Last error: {last_error}", debug_info


def map_simple_to_real_datamodel(datamodel_name:str, type:str="view"):
    new_model = DataModel(
        name = datamodel_name,
        type = type,
        columns = [],
        downstream_models = []
    )
    return new_model


def map_simple_to_real(model:BaseModel, model_class: Type[BaseModel]):
    if model_class == DataModelSimple:
        new_model = map_simple_to_real_datamodel(model.name, model.type)
        new_model.downstream_models = model.downstream_models
        return new_model
    
    if model_class == StoredProcedureSimple:
        new_model = StoredProcedure(
            name = model.name,
            source_objects = [map_simple_to_real_datamodel(o) for o in model.source_objects],
            target_objects = [map_simple_to_real_datamodel(o) for o in model.target_objects]

        )
        return new_model
    
    return model


def extract_from_sql(
    sql_script: str,
    model_class: Type[BaseModel],
    prompt_template: ChatPromptTemplate,
    feedback_template: ChatPromptTemplate,
    validation_func,
    max_attempts: int = 3,
    save_responses: bool = True,
    save_path: Optional[str] = None,
    sql_file_path: Optional[str] = None,
    load_from_file: bool = False
) -> Tuple[Optional[BaseModel], Optional[str], Dict]:
    """Generic extraction function for SQL components using LLM with self-correction.
    
    Args:
        sql_script: The SQL script to analyze
        model_class: The Pydantic model class for validation and parsing
        prompt_template: The initial prompt template for extraction
        feedback_template: The feedback template for retry attempts
        validation_func: The validation function to use
        max_attempts: Maximum number of extraction attempts
        save_responses: Whether to save extraction responses to files
        save_path: Path where to save extraction responses
        sql_file_path: Path of the original SQL file being processed
        load_from_file: Whether to load extraction from a saved file instead of using LLM
    
    Returns:
        A tuple of (Extracted model or None, error_message or None, debug_info)
    """
    # Ensure save_path is set with default if not provided
    if (save_responses or load_from_file) and not save_path:
        save_path = DEFAULT_EXTRACTION_DIR
    
    # First try to load from file if requested
    if load_from_file and sql_file_path and save_path:
        # print(f"  Attempting to load extraction from file for {os.path.basename(sql_file_path)}...")
        model, error, debug_info = load_extraction_from_file(model_class, sql_file_path, save_path, max_attempts)
        # If loading was successful, return the model
        if model is not None:
            print(f"  📂  Successfully loaded extraction from file")
            model = map_simple_to_real(model, model_class)
            return model, None, debug_info
        else:
            # If loading failed, fall back to LLM extraction
            save_responses = True
            print(f"  ⚠️  {error} - Falling back to LLM extraction")
    

    # Extract using LLM if we couldn't load from file or weren't asked to
    model, error, debug_info = extract_with_llm(
        sql_script=sql_script,
        model_class=model_class,
        prompt_template=prompt_template,
        feedback_template=feedback_template,
        validation_func=validation_func,
        max_attempts=max_attempts,
        save_responses=save_responses,
        save_path=save_path,
        sql_file_path=sql_file_path
    )

    if model:
        model = map_simple_to_real(model, model_class)

    return model, error, debug_info
