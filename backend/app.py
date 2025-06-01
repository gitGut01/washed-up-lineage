from fastapi import FastAPI

# Import column functions
from neo4j_integration.fetch_columns import (
    fetch_columns,
    fetch_column_lineage_nodes,
    fetch_column_lineage_edges,
)

# Import unified object functions
from neo4j_integration.fetch_objects import (
    fetch_all_objects,
    fetch_object_by_name,
)

from neo4j_integration.fetch_object_lineage import (
    fetch_object_lineage,
    fetch_object_lineage_edges
)

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Adjust this to match your Angular app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# New unified object endpoints
@app.get('/api/objects')
async def get_objects():
    """Get all objects (data models and stored procedures)."""
    elements = fetch_all_objects()
    return {'elements': elements}


@app.get('/api/objects/{name}')
async def get_object(name: str):
    """Get a specific object (data model or stored procedure) by name."""
    obj = fetch_object_by_name(name)
    return {'elements': [obj] if obj else []}


@app.get('/api/object/lineage/{name}')
async def get_object_lineage(name: str):
    elements = fetch_object_lineage(name)    
    return {"elements": elements}


@app.get('/api/object/lineage/edges/{name}')
async def get_object_lineage_edges(name: str):
    elements = fetch_object_lineage_edges(name)
    return {"elements": elements}


@app.get('/api/columns/{datamodel_name}')
async def get_columns(datamodel_name: str):
    elements = fetch_columns(datamodel_name)
    return {'elements': elements}

@app.get('/api/column/lineage/{name}')
async def get_column_lineage(name: str):
    nodes = fetch_column_lineage_nodes(name)
    edges = fetch_column_lineage_edges(name)
    elements = nodes + edges
    return {'elements': elements}

# Legacy procedure endpoints removed - handled by object endpoints


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level="debug")