CREATE VIEW Assemble_burger AS
SELECT
    -- Create a unique burger ID
    CONCAT('B-', ac.CheesePattyID, '-', tb.BunID) AS BurgerID,
    
    -- Burger name based on components
    CONCAT(
        ac.MeatType, ' ', 
        ac.CheeseType, ' ', 
        CASE WHEN s.SennepID IS NOT NULL THEN 'Bergbys ' ELSE '' END,
        'Burger'
    ) AS BurgerName,
    
    -- Core components
    ac.CheesePattyID,
    ac.PattyID,
    ac.CheeseID,
    tb.BunID,
    ct.ID AS VeggieID,
    s.SennepID,
    
    -- Assembly properties
    'Bottom Bun -> Patty -> Cheese -> Veggies -> ' + 
    CASE WHEN s.SennepID IS NOT NULL THEN 'Sennep -> ' ELSE '' END +
    'Top Bun' AS StackOrder,
    
    -- Burger attributes
    CASE
        WHEN ac.PattyQuality = 'Premium' AND tb.ToastLevel IN ('Medium Toast', 'Light Toast') 
            AND ct.IsCut = TRUE THEN 'Gourmet'
        WHEN ac.FlavorProfile = 'Bold' THEN 'Specialty'
        WHEN ac.FlavorProfile = 'Classic' THEN 'Classic'
        ELSE 'Standard'
    END AS BurgerCategory,
    
    -- Total weight calculation
    (ac.PattyWeightGrams + 
     tb.TopHalfWeight + tb.BottomHalfWeight +
     CASE WHEN ct.IsCut = TRUE THEN 25 ELSE 0 END +
     CASE WHEN s.SennepID IS NOT NULL THEN 10 ELSE 0 END
    ) AS TotalWeightGrams,
    
    -- Burger temperature
    CASE
        WHEN tb.ToastTimeSeconds < 40 THEN 'Warm'
        ELSE 'Hot'
    END AS ServingTemperature,
    
    -- Sauce information
    CASE
        WHEN s.SennepID IS NOT NULL THEN s.SennepType
        ELSE 'No Sennep'
    END AS SauceType,
    
    CASE
        WHEN s.SennepID IS NOT NULL AND s.OriginCountry = 'Norway' THEN TRUE
        ELSE FALSE
    END AS IsAuthentic,
    
    -- Key component attributes to maintain lineage
    ac.MeatType,
    ac.SpiceLevel,
    ac.CheeseType,
    ac.MeltLevel,
    ac.CookLevel,
    tb.BunType,
    tb.ToastLevel,
    tb.IsButtered,
    ct.IsWashed,
    ct.IsCut,
    
    -- Assembly timestamp
    CURRENT_TIMESTAMP AS AssemblyTimestamp
FROM 
    add_cheese ac
JOIN 
    toast_buns tb ON 1=1  -- Cross join for all combinations
JOIN 
    cut_salat_tomatoes ct ON 1=1  -- Cross join for all combinations
LEFT JOIN  -- Left join for optional sennep
    get_bergbys_sennep s ON s.Manufacturer = 'Bergbys'  -- Only Bergbys brand
WHERE
    -- Quality control filters
    ac.QAStatus = 'Passed QA'
    AND tb.InnerSurfaceStatus != 'Unevenly Toasted'
    AND ct.IsCut = TRUE
    AND (tb.ToastTimestamp > DATEADD(minute, -10, CURRENT_TIMESTAMP))  -- Only use freshly toasted buns
    AND (DATEDIFF(minute, ac.CheeseAddedTimestamp, CURRENT_TIMESTAMP) < 5);  -- Only use freshly cheesed patties
