CREATE OR REPLACE VIEW grind_meat AS
SELECT
    MeatID,
    MeatType,
    MeatOrigin,
    CASE
        WHEN MeatQuality = 'Premium' THEN false
        ELSE true
    END AS IsMinced,
    MeatPrice
FROM get_meat
WHERE MeatBestBefore > CURRENT_DATE;