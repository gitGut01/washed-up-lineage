CREATE VIEW cheese_sandwich AS
SELECT    
    c.CheeseID,
    c.CheeseType,
    b.BunID,
    b.BunType,
    b.CutStyle
FROM 
    get_cheese c
CROSS JOIN 
    cut_buns b;
