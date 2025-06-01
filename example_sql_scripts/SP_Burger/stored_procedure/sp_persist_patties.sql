CREATE PROCEDURE sp_persist_patties()
BEGIN
    INSERT INTO patties (
        MeatID,
        MeatType,
        SpiceID,
        IsSpicey,
        MixQuality,
        PattyID,
        PattyQuality,
        PattyWeightGrams,
        SpiceLevel,
        EggFarmName,
        HasShellParts,
        FormTimestamp
    )
    SELECT
        MeatID,
        MeatType,
        SpiceID,
        IsSpicey,
        MixQuality,
        PattyID,
        PattyQuality,
        PattyWeightGrams,
        SpiceLevel,
        EggFarmName,
        HasShellParts,
        FormTimestamp
    FROM form_patties;
END
