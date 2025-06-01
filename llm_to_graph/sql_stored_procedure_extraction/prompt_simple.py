from langchain.prompts import PromptTemplate

from sql_stored_procedure_extraction.examples import EXAMPLE_SQL, EXAMPLE_OUTPUT_SIMPLE
from shared.data_models import StoredProcedureSimple

# Define the prompt template for stored procedure extraction
prompt_simple = PromptTemplate(
    input_variables=["sql_script"],
    template="""
    You are an expert SQL analyst.

    Analyze the provided SQL script and extract:
    1. All **source objects** (tables/views read from)
    2. All **target objects** (tables modified)

    Rules:
    - The SQL contains one stored procedure.
    - Always include the schema name if present (e.g., "schema.tableName").
    - Preserve special formats like "warehouse..object" exactly as is.
    - Ignore commented-out code.
    - Source objects usually appear in SELECT and JOIN clauses.
    - Target objects usually appear in INSERT, UPDATE, and DELETE clauses.
    - DO NOT RETURN ANY Columns

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
        "example_output": EXAMPLE_OUTPUT_SIMPLE.model_dump_json(indent=2),
        "output_schema": StoredProcedureSimple.schema_json(indent=2)
    }
)
