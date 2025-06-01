CREATE VIEW mix_salat AS
SELECT
    t.Name,
    t.IsWashed,
    t.IsCut,
    TRUE AS isMixed,
    s.IsSpicey
FROM 
    cut_salat_tomatoes t
CROSS JOIN 
    grind_spices s
WHERE 
    s.isGrinded = 'WellGrinded'
    AND t.IsWashed = TRUE
    AND s.IsSpicey = FALSE;
