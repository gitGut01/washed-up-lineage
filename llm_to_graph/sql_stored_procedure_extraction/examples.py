"""
This module contains example SQL procedures and expected outputs.
These are used for demonstrating the correct format in prompts.
"""
from shared.data_models import StoredProcedure, StoredProcedureSimple, DataModel, Column

# Example stored procedure for demonstration
EXAMPLE_SQL = """
CREATE PROCEDURE finance.UpdateBalances
    @AccountID INT,
    @Amount DECIMAL(10,2),
    @TransactionType VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update account balance
    UPDATE finance.Accounts
    SET Balance = Balance + CASE WHEN @TransactionType = 'CREDIT' THEN @Amount ELSE -@Amount END
    WHERE AccountID = @AccountID;
    
    -- Log transaction
    INSERT INTO finance.Transactions (AccountID, Amount, TransactionType, TransactionDate)
    VALUES (@AccountID, @Amount, @TransactionType, GETDATE());
    
    -- Return updated balance
    SELECT Balance 
    FROM finance.Accounts
    WHERE AccountID = @AccountID;
END;
"""

# Example output for the stored procedure
EXAMPLE_OUTPUT = StoredProcedure(
    name="finance.UpdateBalances",
    source_objects=[
        DataModel(
            name="finance.Accounts",
            columns=[
                Column(name="Balance", type="DECIMAL(10,2)"),  # Used in arithmetic
                Column(name="AccountID", type="INT"),  # Used in WHERE and SELECT
            ]
        )
    ],
    target_objects=[
        DataModel(
            name="finance.Accounts",
            columns=[
                Column(name="Balance", type="DECIMAL(10,2)")  # Being updated
            ]
        ),
        DataModel(
            name="finance.Transactions",
            columns=[
                Column(name="AccountID", type="INT"),
                Column(name="Amount", type="DECIMAL(10,2)"),
                Column(name="TransactionType", type="VARCHAR(20)"),
                Column(name="TransactionDate", type="DATETIME"),
            ]
        )
    ]
)

EXAMPLE_OUTPUT_SIMPLE = StoredProcedureSimple(
    name="finance.UpdateBalances",
    source_objects=["finance.Accounts"],
    target_objects=["finance.Accounts", "finance.Transactions"]
)