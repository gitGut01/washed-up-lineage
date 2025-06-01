from pydantic import BaseModel
from typing import Optional, List, Literal

# Define structured output models
class Transformation(BaseModel):
    name: str  # Always include schema name if present (e.g., "mySchema.columnName")
    datamodel: Optional[str] = None  # Always include schema name if present (e.g., "mySchema.tableName")
    transformations: List[str] = []

class Column(BaseModel):
    name: str  # Always include schema name if present (e.g., "mySchema.columnName")
    type: Optional[str] = None  # Only for tables
    downstream_columns: Optional[List[Transformation]] = None  # Only for views

class DataModel(BaseModel):
    name: str  # Always include schema name if present (e.g., "mySchema.tableName")
    type: Optional[Literal["table", "view"]] = None
    columns: List[Column] = []
    downstream_models: List[str] = []  # Only for views, include schema names

class DataModelSimple(BaseModel):
    name: str
    type: Literal["table", "view"]
    downstream_models: List[str] = []

class StoredProcedure(BaseModel):
    name: str
    source_objects: List[DataModel] = []  # Objects the procedure reads from
    target_objects: List[DataModel] = []  # Objects the procedure writes to

class StoredProcedureSimple(BaseModel):
    name: str
    source_objects: List[str] = []
    target_objects: List[str] = []