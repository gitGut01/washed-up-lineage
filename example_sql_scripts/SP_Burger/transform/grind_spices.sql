CREATE VIEW grind_spices AS
SELECT
    SpiceID,
    'WellGrinded' AS isGrinded,
    CASE
        WHEN Scollville > 100 THEN TRUE
        ELSE FALSE
    END AS IsSpicey
FROM get_spices;
