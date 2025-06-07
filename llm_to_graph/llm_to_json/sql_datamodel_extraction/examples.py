"""
This module contains example SQL data models and expected outputs.
These are used for demonstrating the correct format in prompts.
"""
from data_models import DataModel, DataModelSimple, Column, Transformation

# Define examples using the actual models
EXAMPLE_SQL = """
CREATE VIEW active_employees AS
SELECT 
    e.emp_id AS employee_id,
    UPPER(emp_name) AS name,
    salary * 1.1 AS adjusted_salary
FROM employees e
WHERE hire_date > '2020-01-01';
"""

# Construct example output using the models
# This represents ONE Create statement, either a table or a view
# Since the example SQL has two statements, we choose the view as it's more complex
EXAMPLE_OUTPUT = DataModel(
    name="active_employees",
    type="view",
    columns=[
        Column(
            name="employee_id",
            downstream_columns=[
                Transformation(
                    name="emp_id",
                    datamodel="employees",
                    transformations=["rename"]
                )
            ]
        ),
        Column(
            name="name",
            downstream_columns=[
                Transformation(
                    name="emp_name",
                    datamodel="employees",
                    transformations=["UPPER"]
                )
            ]
        ),
        Column(
            name="adjusted_salary",
            downstream_columns=[
                Transformation(
                    name="salary",
                    datamodel="employees",
                    transformations=["multiply 1.1"]
                )
            ]
        )
    ],
    downstream_models=["employees"]
)


EXAMPLE_OUTPUT_SIMPLE = DataModelSimple(
    name="active_employees",
    type="view",
    downstream_models=["employees"]
)
