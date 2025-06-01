CREATE PROCEDURE sp_set_slice_date()
BEGIN
    INSERT INTO get_cheese (
        CheeseID,
        CheeseName,
        CheeseType,
        IsSliced,
        SliceDate
    )
    SELECT
        CheeseID,
        CheeseName,
        CheeseType,
        IsSliced,
        UTC_TIMESTAMP()
    FROM get_cheese;
END
