"""
This file can be used to generate mock .sql files and there corresponding json output. 
Note that the .sql files will be empty.
"""

import json
import os
import random
import string
import datetime
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict

# Configuration
NUM_FILES = 1200  # Number of files to generate
JSON_OUTPUT_DIR = "mock_nodes_json"  # Directory to store generated JSON files
SQL_OUTPUT_DIR = "mock_nodes_sql"  # Directory to store empty SQL files
MAX_DOWNSTREAM = 8  # Maximum number of downstream models per file

# Create output directories if they don't exist
os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
os.makedirs(SQL_OUTPUT_DIR, exist_ok=True)

# Function to generate a random name
def generate_random_name() -> str:
    prefixes = ["get_", "process_", "transform_", "analyze_", "calculate_", "extract_", 
                "load_", "merge_", "join_", "filter_", "aggregate_", "sort_", "clean_",
                "format_", "validate_", "normalize_", "summarize_", "convert_", "map_",
                "reduce_", "enrich_", "sample_", "partition_", "segment_", "classify_"]
    
    nouns = ["data", "records", "transactions", "customers", "products", "orders", 
             "sales", "metrics", "statistics", "inventory", "users", "accounts", 
             "payments", "invoices", "shipments", "returns", "reviews", "ratings",
             "prices", "costs", "revenue", "profits", "losses", "taxes", "discounts",
             "promotions", "campaigns", "events", "sessions", "clicks", "views",
             "impressions", "conversions", "subscriptions", "memberships", "plans",
             "features", "attributes", "properties", "dimensions", "measures", "facts",
             "cheese", "meat", "vegetables", "fruits", "spices", "ingredients", "recipes"]
    
    # Randomly decide if we want to use a prefix
    if random.random() < 0.7:  # 70% chance to use a prefix
        return f"{random.choice(prefixes)}{random.choice(nouns)}"
    else:
        return random.choice(nouns)

# Generate a list of unique names
def generate_unique_names(count: int) -> List[str]:
    names = set()
    while len(names) < count:
        name = generate_random_name()
        names.add(name)
    return list(names)

# Generate a single JSON file
def generate_json_file(name: str, file_index: int) -> Dict[str, Any]:
    # Create metadata
    timestamp = datetime.datetime.now().isoformat()
    sql_file = f"sql_scripts/Generated/file_{file_index}.sql"
    
    # Create data
    data_type = random.choice(["view", "table"])
    
    # Create the JSON structure
    json_data = {
        "metadata": {
            "timestamp": timestamp,
            "attempt": 1,
            "sql_file": sql_file
        },
        "data": {
            "name": name,
            "type": data_type,
            "downstream_models": []  # Will be populated later
        }
    }
    
    return json_data

# Function to detect cycles in a graph using DFS
def has_cycle(graph: Dict[str, List[str]]) -> bool:
    visited = set()
    rec_stack = set()
    
    def dfs_visit(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs_visit(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            if dfs_visit(node):
                return True
    
    return False

# Function to create a DAG by assigning topological ranks
def create_dag(unique_names: List[str], max_downstream: int) -> Dict[str, List[str]]:
    # Assign a random rank to each name
    ranks = {name: i for i, name in enumerate(random.sample(unique_names, len(unique_names)))}
    
    # Create a graph where nodes can only depend on nodes with higher ranks
    graph = {}
    
    for name in unique_names:
        # Determine how many downstream models to assign (0 to MAX_DOWNSTREAM)
        num_downstream = random.randint(0, max_downstream)
        
        if num_downstream > 0:
            # Get potential downstream models with higher ranks
            potential_downstream = [n for n in unique_names if ranks[n] > ranks[name]]
            
            # Select random downstream models
            if potential_downstream:
                downstream_models = random.sample(
                    potential_downstream, 
                    min(num_downstream, len(potential_downstream))
                )
                graph[name] = downstream_models
            else:
                graph[name] = []
        else:
            graph[name] = []
    
    return graph

# Main execution
def main():
    print(f"Generating {NUM_FILES} JSON files...")
    
    # Step 1: Generate unique names
    unique_names = generate_unique_names(NUM_FILES)
    
    # Step 2: Generate all JSON files with empty downstream_models
    json_files = {}
    for i, name in enumerate(unique_names):
        json_files[name] = generate_json_file(name, i)
    
    # Step 3: Create a directed acyclic graph (DAG) of dependencies
    dependency_graph = create_dag(unique_names, MAX_DOWNSTREAM)
    
    # Verify that the graph is acyclic
    if has_cycle(dependency_graph):
        print("Error: Cycle detected in the dependency graph!")
        return
    
    # Step 4: Assign downstream models based on the DAG
    for name, json_data in json_files.items():
        json_data["data"]["downstream_models"] = dependency_graph.get(name, [])
    
    # Step 4: Write all JSON files to disk and create empty SQL files
    for i, (name, json_data) in enumerate(json_files.items()):
        # Create JSON file
        json_filename = f"{JSON_OUTPUT_DIR}/{name}.sql_response_1.json"
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Create empty SQL file with the same name
        sql_filename = f"{SQL_OUTPUT_DIR}/{name}.sql"
        with open(sql_filename, 'w') as f:
            pass  # Creates an empty file
        
        # Print progress
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} files...")
    
    print(f"Successfully generated {NUM_FILES} JSON files in '{JSON_OUTPUT_DIR}' directory.")
    print(f"Successfully generated {NUM_FILES} empty SQL files in '{SQL_OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
