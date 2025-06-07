from langchain.prompts import PromptTemplate

from data_models import StoredProcedure
from llm_to_json.sql_stored_procedure_extraction.examples import EXAMPLE_SQL, EXAMPLE_OUTPUT

# Define the prompt template for stored procedure extraction
prompt = PromptTemplate(
    input_variables=["sql_script"],
    template="""
    You are an expert SQL analyst. Extract stored procedures and their data lineage from various SQL dialects.

    INSTRUCTIONS:
    1. For each stored procedure:
       - Include schema in procedure name ("mySchema.procName")
       - Identify source objects (tables/views read from)
       - Identify target objects (tables written to)

    2. Important rules:
       - SOURCE: Tables/views read in SELECT, JOIN statements
       - TARGET: Tables modified in INSERT, UPDATE, DELETE statements
       - ALWAYS include schema names in all object names when present
       - Preserve double dots (..) in names like "warehouse..object" exactly as is
       - If column types cannot be inferred, leave them as null
       - The name field MUST include schema when present ("mySchema.tableName" not just "tableName")

    OUTPUT REQUIREMENTS:
    - Return ONLY valid JSON for a SINGLE stored procedure following the schema pattern shown in the example below
    - Always include schema names in procedure name and all object references
    - For columns where type can't be determined, set type to null
    - Don't invent information not present in the SQL
    - Ignore commented code

    You need to support different SQL dialects and procedure formats. Here is an example:
    
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
        "output_schema": StoredProcedure.schema_json(indent=2)
    }
)
