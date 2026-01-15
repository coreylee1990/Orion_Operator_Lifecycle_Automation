SELECT 
    ST.DivisionID,
    CAST(ST.OrderID AS INT) AS SequenceOrder,
    ST.Status AS StatusName,
    ST.Id AS StatusID,
    ST.CertFlag
FROM pay_StatusTypes ST
INNER JOIN pay_PizzaStatus PS ON ST.PizzaStatusID = PS.ID
WHERE PS.IsOperator = 1
    AND (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0)
    AND (ST.DivisionID LIKE '2 - IL%' 
        OR ST.DivisionID LIKE '3 - TX%' 
        OR ST.DivisionID LIKE '5 - CA%' 
        OR ST.DivisionID LIKE '6 - FL%' 
        OR ST.DivisionID LIKE '7 - MI%' 
        OR ST.DivisionID LIKE '8 - OH%' 
        OR ST.DivisionID LIKE '10 - OR%' 
        OR ST.DivisionID LIKE '11 - GA%' 
        OR ST.DivisionID LIKE '12 - PA%')
ORDER BY 
    CAST(LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS INT),
    CAST(ST.OrderID AS INT);
