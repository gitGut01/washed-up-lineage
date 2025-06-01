CREATE VIEW cook_patties AS
SELECT
    fp.PattyID,
    fp.MeatType,
    fp.SpiceLevel,
    fp.PattyQuality,
    fp.PattyWeightGrams,
    
    -- Cooking process determines final attributes
    CASE
        WHEN fp.PattyQuality = 'Premium' THEN 'Medium-Rare'
        WHEN fp.PattyQuality = 'Standard' THEN 'Medium-Well'
        ELSE 'Well-Done'
    END AS CookLevel,
    
    -- Calculate cooking time based on patty weight and quality
    CASE
        WHEN fp.PattyQuality = 'Premium' THEN fp.PattyWeightGrams * 0.008
        WHEN fp.PattyQuality = 'Standard' THEN fp.PattyWeightGrams * 0.01
        ELSE fp.PattyWeightGrams * 0.012
    END AS CookTimeMinutes,
    
    -- Determine internal temperature based on cook level
    CASE
        WHEN fp.PattyQuality = 'Premium' THEN 145
        WHEN fp.PattyQuality = 'Standard' THEN 155
        ELSE 165
    END AS InternalTempF,
    
    -- Flag for quality assurance
    CASE
        WHEN fp.HasShellParts = true THEN 'Requires Inspection'
        ELSE 'Passed QA'
    END AS QAStatus,
    
    -- Tracking data for preparation time
    DATEDIFF(minute, fp.FormTimestamp, CURRENT_TIMESTAMP) AS MinutesSinceFormed,
    
    -- Additional metadata
    CURRENT_TIMESTAMP AS CookTimestamp,
    
    -- Core metadata to maintain lineage
    fp.MeatID,
    fp.SpiceID,
    fp.MixQuality,
    fp.IsSpicey
FROM 
    patties fp
WHERE
    -- Only cook patties that meet minimum quality standards
    fp.PattyQuality IN ('Premium', 'Standard', 'Budget');
