# Global configuration settings
DEFAULT_WAREHOUSE = "MY_WAREHOUSE"
WAREHOUSE_DEFAULT_SCHEMA_MAPPING = {
    DEFAULT_WAREHOUSE: "dbo",
    "Organizer": "yo"
}
DO_RESET_NEO4J_DATABASE = True
DO_SIMPLE_EXTRACT = True
DEFAULT_EXTRACTION_DIR = "extraction_runs"
PATH_EXTRACTION_RUNS = "BURGER_SIMPLE"


# SQL file paths for processing
DATAMODEL_SQL_PATHTS = [
    "../example_sql_scripts/Burger"
]

STORED_PROCEDURE_SQL_PATHS = [
]