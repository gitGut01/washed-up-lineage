# Handle various patterns:
# 1. myObject - Just an object name, no warehouse or schema (len=1)
# 2. mySchema.myObject - Schema and object, no warehouse (len=2)
# 3. ..myObject - No warehouse or schema, but with dots (parts[0] will be empty)
# 4. warehouse.schema.object - Full pattern (len=3 or more)
# 5. warehouse..object - Warehouse and object with no schema (len=3 or more)
# 6. if there are mre than two '.', than the rest belongs to the warehouse, ware.house.schema.object

from config import (
    DEFAULT_WAREHOUSE, 
    WAREHOUSE_DEFAULT_SCHEMA_MAPPING
)
SCHEMA_MISSING_MESSAGE = "<MISSING>"


def get_id_name(warhouse:str, schema:str, object:str):
    id_name = f"{warhouse.upper()}.{schema.upper()}.{object.upper()}"
    return id_name

def split_warehouse_schema_object(object_name: str, default_warehouse: str = DEFAULT_WAREHOUSE, warehouse_default_schema_mapping: dict = WAREHOUSE_DEFAULT_SCHEMA_MAPPING):
    if object_name is None:
        object_name = ""
    
    parts = object_name.split('.')

    warehouse = ''
    schema = ''
    object = ''

    parts = list(reversed(parts))
    for i, part in enumerate(parts):
        if i == 0:
            object = part
        elif i == 1:
            schema = part
        elif i == 2:
            _reverese = list(reversed(parts[2:]))
            warehouse = '.'.join(_reverese)
    
    if warehouse == '':
        warehouse = default_warehouse

    
    if schema == '':
        schema = SCHEMA_MISSING_MESSAGE
    
        warehouse_key = (warehouse).upper()
        if warehouse_key in (k.upper() for k in warehouse_default_schema_mapping):
            # Find the exact key match in the original dict
            for k, v in warehouse_default_schema_mapping.items():
                if k.upper() == warehouse_key:
                    schema = v
                    break

    warehouse = warehouse.replace('[', '').replace(']', '')
    schema = schema.replace('[', '').replace(']', '')
    object = object.replace('[', '').replace(']', '')
    return warehouse, schema, object