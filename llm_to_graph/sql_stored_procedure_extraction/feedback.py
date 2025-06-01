"""
This module contains feedback templates for improving extraction results.
These templates are used when initial extraction attempts fail.
"""
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# Define a template for feedback to improve extraction based on parsing errors
feedback_template = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("""
    You previously attempted to extract SQL stored procedure information but your output had issues.
    
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
    4. Your output should be a DIRECT JSON OBJECT with name, source_objects, and target_objects fields
    5. Remember to include ALL source and target objects, with schema names when present
    6. Pay close attention to FULL object names with schema (e.g., "mySchema.tableName")
    
    Provide your corrected output:
    """)
])
