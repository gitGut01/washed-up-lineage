import os
import datetime

from config import (
    USE_ALREADY_EXTRACTED, 
    PATH_EXTRACTION_RUNS, 
    DEFAULT_EXTRACTION_DIR
)


def setup_extraction_environment(use_already_extracted=USE_ALREADY_EXTRACTED, specific_timestamp=PATH_EXTRACTION_RUNS):
    """Set up the extraction environment with appropriate parameters.
    
    Args:
        use_already_extracted: Whether to use already extracted data
        specific_timestamp: Specific timestamp to use for extraction runs
        
    Returns:
        Tuple of (use_already_extracted, save_extraction_responses, timestamp, extraction_runs_path)
    """
    if use_already_extracted:
        timestamp = specific_timestamp
        save_extraction_responses = False
        extraction_runs_path = os.path.join(DEFAULT_EXTRACTION_DIR, timestamp) if timestamp else None
    else:
        save_extraction_responses = True
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        extraction_runs_path = os.path.join(DEFAULT_EXTRACTION_DIR, timestamp)
        # Create base directory if it doesn't exist
        os.makedirs(extraction_runs_path, exist_ok=True)
        print(f"Created extraction runs directory: {extraction_runs_path}")
        
    return use_already_extracted, save_extraction_responses, timestamp, extraction_runs_path
