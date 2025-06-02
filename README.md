# WashedUp Lineage

**A half-decent, LLM-powered cartographer that maps your data warehouse mess—tracking both upstream and downstream dependencies.**

---

## What is WashedUp Lineage?

WashedUp Lineage is a tool designed to help you understand and visualize the complex web of dependencies in your data warehouse. It uses a Large Language Model (LLM) to parse your SQL `CREATE` statements, extracting both upstream and downstream relationships at the table and column level.

---

## Features

- **LLM-powered parsing** of SQL DDL to extract dependencies  
- Tracks **both upstream and downstream** lineage  
- Captures **table-level and column-level** dependencies, including column transformations  
- Stores extracted data for each DDL into `json` files
- Uses **Neo4j graph database** to store the lineage data that can be queried
- Provides a frontend to **visualize data lineage maps** for easier understanding and debugging

## Frontend 
### View Dependencies
Select a datamodel to view its upstream and downstream dependencies.
![Select Datamodel](resources/zoom_lineage.gif)

### Show Datamodel Lineage
Isolate the lineage to only display the datamodels upstream and downstream dependencies.
![Show Datamodel Lineage](resources/datamodel_lineage.gif)

### Search
Search for a datamodel by name.
![Search Datamodel](resources/search.gif)

### Show Column Lineage
Select a column to view the columns upstream and downstream dependencies and transformations.
![Show Column Lineage](resources/column_lineage.gif)

---

## Why “WashedUp Lineage”?

Data warehouses often become messy, complex, and hard to navigate — basically, “washed up.” This tool aims to be a **half-decent**, practical way to bring some clarity and order by mapping out all those tangled dependencies with the help of AI.

---

## Getting Started

### Prerequisites

- Python 3.12+  
- Neo4j database instance  
- Access to your data warehouse DDL SQL scripts  

### Setup

#### 1. Neo4j Setup

1. Install and start Neo4j on your system
   - You can download Neo4j from [https://neo4j.com/deployment-center/?desktop-gdb](https://neo4j.com/deployment-center/?desktop-gdb)
   - After installation, start the Neo4j service
   - Neo4j Browser interface is typically available at: `http://localhost:7474/browser/`

2. Configure Neo4j credentials
   - Make note of your Neo4j URL, username and password
   - You'll need to update these in the `.env` file in both the `llm_to_graph` and `backend` modules

#### 2. LLM to Graph Module

1. Navigate to the `llm_to_graph` directory:
   ```
   cd llm_to_graph
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: Using a virtual environment is recommended but optional

3. Configure the module:
   - Refer to `llm_to_graph/README.md` for detailed configuration instructions
   - Make sure to update the `.env` file with your Neo4j credentials

4. Run the module:
   ```
   python main.py
   ```

#### 3. Backend Module

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Update the `.env` file with your Neo4j credentials

4. Run the backend server:
   ```
   python app.py
   ```
   - The API documentation will be available at: `http://localhost:8000/docs`

#### 4. Frontend Module

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   ng serve
   ```
   - The frontend will be available at: `http://localhost:4200/`
