from neo4j_integration.base_connector import driver

def propagate_column_types():
    visited = set()
    queue = []

    # Step 1: Initialize queue with all columns that have a type
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Column)
            WHERE c.type IS NOT NULL
            RETURN c.name AS name, c.type AS type
            """
        )

        queue = [{"name": record["name"], "type": record["type"]} for record in result]

    # Step 2: BFS-like propagation of types
    while queue:
        current = queue.pop(0)
        current_name = current["name"]
        current_type = current["type"]

        if current_name in visited:
            continue
        visited.add(current_name)

        with driver.session() as session:
            # Find upstream columns that don't have a type
            result = session.run(
                """
                MATCH (start:Column {name: $current_name})
                MATCH path = (start)-[:UPSTREAM_COLUMN]->(upstream)
                WHERE upstream.type is null
                RETURN upstream.name AS name         
                """, 
                {
                    "current_name": current_name
                }
            )

            upstream_columns = [record["name"] for record in result]

            # Update upstream column types and add them to queue
            for upstream_name in upstream_columns:
                try:
                    session.run(
                        """
                        MATCH (c:Column {name: $name})
                        SET c.type = $type,
                            c.is_type_guessed = true,
                            c.is_type_updated = true
                        """, 
                        {
                            "name": upstream_name, 
                            "type": current_type
                        }
                    )
                    queue.append({"name": upstream_name, "type": current_type})
                except Exception as e:
                    # If there's an error, mark the column as not updated
                    try:
                        session.run(
                            """
                            MATCH (c:Column {name: $name})
                            SET c.is_type_updated = false
                            """, 
                            {
                                "name": upstream_name
                            }
                        )
                    except Exception:
                        # If even setting the error flag fails, just continue
                        pass