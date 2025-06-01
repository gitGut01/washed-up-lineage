CREATE VIEW form_patties AS
SELECT
    md.MeatID,
    md.MeatType,
    md.SpiceID,
    md.IsSpicey,
    md.MixQuality,
    
    -- Generate a unique PattyID based on meat and spice combination
    CONCAT('P', md.MeatID, '-', md.SpiceID) AS PattyID,
    
    -- Patty quality is determined by mix quality and absence of shell parts
    CASE
        WHEN md.MixQuality = 'Well Mixed' AND md.HasShellParts = false THEN 'Premium'
        WHEN md.MixQuality = 'Well Mixed' AND md.HasShellParts = true THEN 'Standard'
        ELSE 'Budget'
    END AS PattyQuality,
    
    -- Calculate weight based on meat type
    CASE
        WHEN md.MeatType = 'Beef' THEN 200
        WHEN md.MeatType = 'Chicken' THEN 150
        ELSE 180
    END AS PattyWeightGrams,
    
    -- Spice level indicator
    CASE
        WHEN md.IsSpicey = true THEN 'Spicy'
        ELSE 'Mild'
    END AS SpiceLevel,
    
    -- Tracking egg information for quality control
    md.EggFarmName,
    md.EggType,
    md.HasShellParts,
    
    -- Timestamp for tracking
    CURRENT_TIMESTAMP AS FormTimestamp
FROM 
    mix_dough md
WHERE
    md.MixQuality IS NOT NULL;
