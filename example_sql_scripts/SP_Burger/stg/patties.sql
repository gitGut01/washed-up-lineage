CREATE TABLE patties (
    MeatID INT,
    MeatType VARCHAR(50),
    SpiceID INT,
    IsSpicey BOOLEAN,
    MixQuality VARCHAR(50),
    PattyID VARCHAR(100) PRIMARY KEY,
    PattyQuality VARCHAR(50),
    PattyWeightGrams INT,
    SpiceLevel VARCHAR(20),
    EggFarmName VARCHAR(100),
    HasShellParts BOOLEAN,
    FormTimestamp TIMESTAMP
);
