CREATE VIEW wash_salat_tomatoes AS
SELECT
    SalatID AS ID,
    SalatName AS Name,
    CASE
        WHEN IsOrganic THEN 'Organic'
        ELSE 'Not Organic'
    END AS Type,
    TRUE AS IsWashed
FROM get_salat

UNION

SELECT
    TomatoID AS ID,
    TomatoName AS Name,
    CASE
        WHEN IsOrganic THEN 'Organic'
        ELSE 'Not Organic'
    END AS Type,
    TRUE AS IsWashed
FROM get_tomatoes;
