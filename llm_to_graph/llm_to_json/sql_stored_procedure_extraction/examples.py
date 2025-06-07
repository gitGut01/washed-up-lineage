"""
This module contains example SQL procedures and expected outputs.
These are used for demonstrating the correct format in prompts.
"""
from data_models import StoredProcedure, StoredProcedureSimple

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

EXAMPLE_OUTPUT = StoredProcedure(
    name="finance.UpdateBalances",
    source_objects=["finance.Accounts"],
    target_objects=["finance.Accounts", "finance.Transactions"]
)


EXAMPLE_OUTPUT_SIMPLE = StoredProcedureSimple(
    name="finance.UpdateBalances",
    source_objects=["finance.Accounts"],
    target_objects=["finance.Accounts", "finance.Transactions"]
)
