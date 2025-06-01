CREATE VIEW use_egg AS
SELECT
    EggID,
    EggFarmName,
    EggDistributer,
    CASE
        WHEN EggDistributer = 'First Price' THEN TRUE
        ELSE FALSE
    END AS PartsOfShellInTheYoke
FROM get_eggs;
