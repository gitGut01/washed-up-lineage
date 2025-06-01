CREATE VIEW mix_dough AS
SELECT
    m.MeatID,
    m.MeatType,
    m.IsMinced,
    s.SpiceID,
    s.isGrinded,
    s.IsSpicey,
    e.EggID,
    e.EggFarmName,
    e.PartsOfShellInTheYoke,
    
    -- Additional combined properties
    CASE
        WHEN m.IsMinced AND s.isGrinded = 'WellGrinded' THEN 'Well Mixed'
        ELSE 'Poorly Mixed'
    END AS MixQuality,
    
    -- Flag if there are shell parts in the mixture
    e.PartsOfShellInTheYoke AS HasShellParts
FROM 
    grind_meat m
CROSS JOIN 
    grind_spices s
CROSS JOIN 
    use_egg e;
