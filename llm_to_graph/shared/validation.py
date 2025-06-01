"""
This module contains shared validation logic for SQL extraction.
It provides functions to validate and parse LLM outputs against the expected schema.
"""
import json
import re
from typing import Dict, Optional, Tuple, Type
from pydantic import ValidationError, BaseModel

def validate_output(response: str, model_class: Type[BaseModel]) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """Validates the LLM response and tries to extract valid JSON.
    
    Args:
        response: The raw response string from the LLM
        model_class: The Pydantic model class to validate against
        
    Returns:
        Tuple of (success, error_message, extracted_json)
    """
    # First try to extract JSON from markdown block with json tag
    json_match = re.search(r'```json\s*(.+?)\s*```', response, re.DOTALL)
    
    # If not found, try any code block
    if not json_match:
        json_match = re.search(r'```\s*(.+?)\s*```', response, re.DOTALL)
    
    # If still not found, use the whole response
    json_str = json_match.group(1).strip() if json_match else response.strip()
    
    # Try to find JSON within the text by looking for the opening brace
    try:
        # Look for the start and end of a JSON object
        start_idx = json_str.find('{')
        if start_idx >= 0:
            # Find the matching closing brace by counting nested objects
            brace_count = 0
            end_idx = -1
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_str[start_idx:], start=start_idx):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\' and in_string:
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
            
            if end_idx > 0:
                json_str = json_str[start_idx:end_idx]
        
        # Try to parse the JSON
        parsed_json = json.loads(json_str)
        
        # Validate against our schema
        model_class(**parsed_json)
        return True, None, parsed_json
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {str(e)}", None
    except ValidationError as e:
        return False, f"Schema validation error: {str(e)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None
