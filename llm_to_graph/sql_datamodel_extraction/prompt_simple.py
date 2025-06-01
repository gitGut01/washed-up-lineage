from langchain.prompts import PromptTemplate, prompt

from shared.data_models import DataModelSimple
from sql_datamodel_extraction.examples import EXAMPLE_SQL, EXAMPLE_OUTPUT_SIMPLE

# Define Prompt for SQL Structure Extraction
prompt_simple = PromptTemplate(
    input_variables=["sql_script"],
    template="""
    Analyze the provided SQL script and extract:

    1. The name of the data model being created (table or view). Always include the schema name if present.
    2. A list of downstream models (tables or views) used in the logic. These are any models referenced in FROM, JOIN, or subqueries. Do not include hardcoded SELECT values (e.g., `SELECT 1, 'A'`) or derived data not from a model.

    Important Rules:
    - Ignore commented-out lines (those starting with `--` or within `/* */`).
    - Always extract the correct type: "view" or "table".
    - Tables (i.e., CREATE TABLE) have no downstream models.
    - A model may or may not include a schema.
    - Downstream models must come from actual tables or views referenced in FROM or JOIN clauses.
    - Hardcoded UNION/SELECT statements are not downstream models.
    
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
        "output_schema": DataModelSimple.schema_json(indent=2)
    }
)
