from langchain.prompts import PromptTemplate

from shared.data_models import DataModel
from sql_datamodel_extraction.examples import EXAMPLE_SQL, EXAMPLE_OUTPUT

# Define Prompt for SQL Structure Extraction
prompt = PromptTemplate(
    input_variables=["sql_script"],
    template="""
    You are an expert SQL analyst specializing in structural extraction and column lineage tracking.
    Analyze the provided SQL script and extract all data models (tables and views) with their complete structure.
    Remember that there might be a wide variety of SQL dialects used.

    INSTRUCTIONS:
    1. For TABLES (CREATE TABLE):
       - Extract table name and all columns with their data types
       - For the table name, ALWAYS include the schema name in the name field when present (e.g., "mySchema.tblName" not just "tblName")
       - Tables have no transformations or references
    2. For VIEWS (CREATE VIEW):
    - Extract the view name and all output columns.
    - For the view name, ALWAYS include the schema name in the name field when present (e.g., "mySchema.viewName" not just "viewName")
    - For each column, trace its lineage **all the way back to base tables**, even if intermediate transformations occurred through CTEs.
    - Inline all CTE logic into the final transformation chain (i.e., treat CTEs as transparent logic steps, not standalone models).
    - Output only one data model per view, even if CTEs are used.
    - Include all referenced base tables or existing views in the `downstream_models` WITH THEIR SCHEMA names.
    - When a transformation (e.g., `SUM`, `COUNT`, `CAST`, etc.) implies a specific data type, assign that data type to the resulting column.
    3. For complex transformations:
       - Break down each operation (e.g., "CONCAT(first_name, ' ', last_name)" → ["concat", "space join"])
       - Note calculated fields clearly (e.g., "price * quantity" → ["multiply"])
       - When CASE, include the whole CASE with its WHEN and ELSE into one transformation, dont put the same CASE in twice

    OUTPUT REQUIREMENTS:
    - Return ONLY valid JSON matching the provided schema
    - IMPORTANT: Return only ONE DataModel object (not a list or wrapped in another object) as there will always be just ONE CREATE statement in the SQL
    - Include ALL columns and their complete lineage
    - Be precise with transformation descriptions
    - ALWAYS include schema names in original_name fields and in all references to tables/views when present
    - Don't invent information that isn't in the SQL
    - Be careful some SQLs might contain commented out lines as well

    You need to support a bunch of different SQL Formats, here is just one example:
    
    EXAMPLE SQL:
    ```sql
    {example_sql}
    ```

    EXAMPLE OUTPUT:
    {example_output}

    ACTUAL SQL TO ANALYZE:
    ```sql
    {sql_script}
    ```

    Remember the output must strictly follow this schema:
    {output_schema}
    """,
    partial_variables={
        "example_sql": EXAMPLE_SQL,
        "example_output": EXAMPLE_OUTPUT.model_dump_json(indent=2),
        "output_schema": DataModel.schema_json(indent=2)
    }
)
