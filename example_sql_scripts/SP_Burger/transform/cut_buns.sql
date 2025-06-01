CREATE VIEW cut_buns AS
SELECT
    BunID,
    BunType,
    
    -- Add a cut status
    CASE
        WHEN BunType IN ('Sesame', 'Brioche') THEN 'Horizontal Cut'
        WHEN BunType = 'Potato' THEN 'Diamond Cut'
        ELSE 'Standard Cut'
    END AS CutStyle,
    
    -- Determine if the bun was cut evenly
    CASE
        WHEN BunSize = 'Regular' THEN TRUE
        WHEN BunSize = 'Large' THEN FALSE
        ELSE CASE WHEN RAND() > 0.7 THEN FALSE ELSE TRUE END
    END AS IsEvenCut,
    
    -- Calculate top and bottom weights
    CASE
        WHEN BunType = 'Brioche' THEN 45
        WHEN BunType = 'Sesame' THEN 40
        WHEN BunType = 'Potato' THEN 50
        ELSE 35
    END AS TopHalfWeight,
    
    CASE
        WHEN BunType = 'Brioche' THEN 35
        WHEN BunType = 'Sesame' THEN 40
        WHEN BunType = 'Potato' THEN 30
        ELSE 35
    END AS BottomHalfWeight,
    
    -- Add timestamp
    CURRENT_TIMESTAMP AS CutTimestamp
FROM 
    get_buns
WHERE
    -- Only cut buns that aren't already sliced
    PreSliced = FALSE;