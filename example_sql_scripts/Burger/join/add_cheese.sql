CREATE VIEW add_cheese AS
SELECT
    cp.PattyID,
    cp.MeatType,
    cp.SpiceLevel,
    cp.CookLevel,
    cp.QAStatus,
    
    -- Cheese information
    c.CheeseID,
    c.CheeseType,
    
    -- Create a unique identifier for the cheese patty
    CONCAT(cp.PattyID, '-C', c.CheeseID) AS CheesePattyID,
    
    -- Add cheese melting properties based on patty temperature
    CASE
        WHEN cp.InternalTempF >= 155 AND c.CheeseType IN ('American', 'Cheddar', 'Swiss') THEN 'Well Melted'
        WHEN cp.InternalTempF >= 145 AND c.CheeseType IN ('American', 'Cheddar') THEN 'Partially Melted'
        ELSE 'Barely Melted'
    END AS MeltLevel,
    
    -- Flavor combinations
    CASE
        WHEN c.CheeseType = 'Blue' AND cp.SpiceLevel = 'Spicy' THEN 'Bold'
        WHEN c.CheeseType IN ('Swiss', 'Gouda') AND cp.CookLevel = 'Medium-Rare' THEN 'Gourmet'
        WHEN c.CheeseType = 'American' THEN 'Classic'
        ELSE 'Standard'
    END AS FlavorProfile,
    
    -- Determine cheese thickness based on patty quality
    CASE
        WHEN cp.PattyQuality = 'Premium' THEN 'Thick Slice'
        WHEN cp.PattyQuality = 'Standard' THEN 'Standard Slice'
        ELSE 'Thin Slice'
    END AS CheeseThickness,
    
    -- Additional patty properties to maintain lineage
    cp.PattyQuality,
    cp.PattyWeightGrams,
    cp.CookTimeMinutes,
    cp.InternalTempF,
    
    -- Timing information
    cp.CookTimestamp,
    CURRENT_TIMESTAMP AS CheeseAddedTimestamp
FROM 
    cook_patties cp
CROSS JOIN
    get_cheese c
WHERE
    -- Only add cheese to properly cooked patties
    cp.QAStatus = 'Passed QA';
