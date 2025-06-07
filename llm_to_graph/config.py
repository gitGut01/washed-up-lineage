# Global configuration settings
DEFAULT_WAREHOUSE = "MY_WAREHOUSE"
WAREHOUSE_DEFAULT_SCHEMA_MAPPING = {
    DEFAULT_WAREHOUSE: "dbo",
    "Organizer": "yo"
}
DO_RESET_NEO4J_DATABASE = True
DO_SIMPLE_EXTRACT = False
USE_ALREADY_EXTRACTED = True
DEFAULT_EXTRACTION_DIR = "../extraction_runs"
PATH_EXTRACTION_RUNS = "SP_BURGER_FULL"


# SQL file paths for processing
DATAMODEL_SQL_PATHTS = [
    "../example_sql_scripts/SP_Burger/join",
    "../example_sql_scripts/SP_Burger/stg",
    "../example_sql_scripts/SP_Burger/transform",
]

STORED_PROCEDURE_SQL_PATHS = [
    "../example_sql_scripts/SP_Burger/stored_procedure"
]