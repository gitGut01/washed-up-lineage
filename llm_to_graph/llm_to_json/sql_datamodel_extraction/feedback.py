"""
This module contains feedback templates for improving datamodel extraction results.
These templates are used when initial extraction attempts fail.
"""
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate


# Define a template for feedback to improve extraction based on parsing errors
feedback_template = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("""
    You previously attempted to extract SQL data model information but your output had issues.
    
    Original SQL script:
    ```sql
    {sql_script}
    ```
    
    Your previous output:
    {previous_output}
    
    Error encountered: {error_message}
    
    PLEASE FIX YOUR OUTPUT:
    1. Make sure to include schema names in object names (e.g., "mySchema.tableName" not just "tableName")
    2. Follow EXACTLY this schema: {schema}
    3. DO NOT output the schema itself, but provide an ACTUAL instance with values following the schema
    4. Your output should be a DIRECT JSON OBJECT following the DataModel structure
    5. Remember to include ALL downstream models with their full names including schema when present
    6. For each column transformation, ensure proper tracking of source columns with schema names
    
    Provide your corrected output:
    """)
])
