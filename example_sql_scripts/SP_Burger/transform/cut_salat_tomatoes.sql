CREATE VIEW cut_salat_tomatoes AS
SELECT
    ID,
    Name,
    Type,
    IsWashed,
    TRUE AS IsCut
FROM wash_salat_tomatoes;
