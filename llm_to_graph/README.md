# LLM to Graph

A tool that leverages Large Language Models (LLMs) to extract information from SQL files and build a comprehensive data lineage graph in Neo4j. The tool supports both data models (tables/views) and stored procedures. 

## Features

- Extracts tables, views, and their column definitions from SQL files
- Processes stored procedures to identify data dependencies
- Creates a unified data lineage graph in Neo4j
- Supports schema name inclusion in object identifiers
- Configurable for different warehouse environments
- Multiple LLM backend options (Google Vertex AI/Gemini, Ollama... configure them under `shared/llm_client.py`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd llm_to_graph
   ```

2. Install Neo4j:
   - Download and install `Neo4j Desktop` from [https://neo4j.com/deployment-center/?desktop-gdb](https://neo4j.com/deployment-center/?desktop-gdb)
   - Start Neo4j
   - Set up username and password.

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy the `.env_example` file to `.env`
   - Add your Neo4j connection details (URI, username, password)

The `.env` file is included in `.gitignore` to ensure credentials aren't accidentally committed.

## Configuration

The project uses `config.py` for non-sensitive configuration:

### Key Configuration Options

| Parameter | Description |
| --------- | ----------- |
| `DEFAULT_WAREHOUSE` | Default data warehouse identifier |
| `WAREHOUSE_DEFAULT_SCHEMA_MAPPING` | Maps warehouse names to their default schemas. This is to know what schema to put `AnotherWarehouse..ObjectName` in. |
| `DO_RESET_NEO4J_DATABASE` | Whether to reset the Neo4j database before extraction (default: True) |
| `DO_SIMPLE_EXTRACT` | Enable simpler extraction, if `True`, will ignore columns |
| `DEFAULT_EXTRACTION_DIR` | Directory for storing extraction results |
| `PATH_EXTRACTION_RUNS` | Subfolder for extraction runs |
| `DATAMODEL_SQL_PATHTS` | List of paths to SQL files containing table/view definitions |
| `STORED_PROCEDURE_SQL_PATHS` | List of paths to SQL files containing stored procedures |

Example customization:

```python
# Global configuration settings
DEFAULT_WAREHOUSE = "MY_WAREHOUSE"
WAREHOUSE_DEFAULT_SCHEMA_MAPPING = {
    DEFAULT_WAREHOUSE: "dbo",
    "Organizer": "yo"
}
DO_SIMPLE_EXTRACT = True
DEFAULT_EXTRACTION_DIR = "extraction_runs"
PATH_EXTRACTION_RUNS = "BURGER_SIMPLE"


# SQL file paths for processing
DATAMODEL_SQL_PATHTS = [
    "../example_sql_scripts/Burger"
]

STORED_PROCEDURE_SQL_PATHS = [
]
```

## Usage

Make sure Neo4j is running before starting the extraction process:

```bash
# Start Neo4j if it's not already running
neo4j start

# Run the extraction process
python main.py
```

This will:
1. Reset the Neo4j database (optional)
2. Process all SQL files in the configured paths
4. Extract data models and stored procedures into `.json` files
5. Create relationships between entities in Neo4j
6. Apply post-processing steps to enhance the graph
7. Create indexes for efficient querying

## Accessing the Graph

After running the extraction, access your Neo4j database to view and query the lineage graph. The graph includes:

- Object nodes (tables, views, stored procedures)
- Column nodes with type information
- Relationships between objects (UPSTREAM_MODEL)
- Relationships between columns and their parent objects
