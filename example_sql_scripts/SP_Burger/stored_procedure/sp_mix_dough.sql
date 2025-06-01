DELIMITER $$

CREATE PROCEDURE sp_mix_dough()
BEGIN
    INSERT INTO dough (
        MeatID,
        MeatType,
        IsMinced,
        SpiceID,
        isGrinded,
        IsSpicey,
        EggID,
        EggFarmName,
        PartsOfShellInTheYoke,
        MixQuality,
        HasShellParts
    )
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
        CASE
            WHEN m.IsMinced AND s.isGrinded = 'WellGrinded' THEN 'Well Mixed'
            ELSE 'Poorly Mixed'
        END AS MixQuality,
        e.PartsOfShellInTheYoke AS HasShellParts
    FROM 
        grind_meat m
    CROSS JOIN 
        grind_spices s
    CROSS JOIN 
        use_egg e;
END$$

DELIMITER ;
