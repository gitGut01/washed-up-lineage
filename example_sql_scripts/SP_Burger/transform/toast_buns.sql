CREATE VIEW toast_buns AS
SELECT
    BunID,
    BunType,
    CutStyle,
    IsEvenCut,
    TopHalfWeight,
    BottomHalfWeight,
    
    -- Toasting status based on bun type and freshness
    CASE
        WHEN BunType = 'Brioche' THEN 'Light Toast'
        WHEN BunType = 'Sesame' THEN 'Medium Toast'
        WHEN BunType = 'Potato' THEN 'Crispy Toast'
        ELSE 'Heavy Toast' -- For older or regular buns, toast more heavily
    END AS ToastLevel,
    
    -- Inner surface status
    CASE
        WHEN CutStyle = 'Diamond Cut' THEN 'Cross-Hatched'
        WHEN IsEvenCut = TRUE THEN 'Even Golden Brown'
        ELSE 'Unevenly Toasted'
    END AS InnerSurfaceStatus,
    
    -- Toasting time in seconds
    CASE
        WHEN BunType = 'Brioche' THEN 30
        WHEN BunType = 'Sesame' THEN 45
        WHEN BunType = 'Potato' THEN 60
        ELSE 40
    END AS ToastTimeSeconds,
    
    -- Determine if buttered during toasting
    CASE
        WHEN BunType IN ('Brioche', 'Potato') THEN TRUE
        ELSE FALSE
    END AS IsButtered,
    
    -- Outer crust status
    CASE
        WHEN BunType = 'Sesame' THEN 'Sesame Enhanced'
        WHEN BunType = 'Brioche' THEN 'Glossy Finish'
        ELSE 'Standard Finish'
    END AS OuterFinish,
    
    -- Add timestamps for lineage
    CutTimestamp,
    CURRENT_TIMESTAMP AS ToastTimestamp,
    
    -- Time between cutting and toasting in seconds
    DATEDIFF(second, CutTimestamp, CURRENT_TIMESTAMP) AS SecondsBetweenCutAndToast
FROM 
    cut_buns
WHERE
    -- Only toast fresh buns
    DATEDIFF(day, CURRENT_TIMESTAMP, ExpiryDate) > 2;