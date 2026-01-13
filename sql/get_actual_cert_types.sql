USE Orion;

-- Query 1: Get all actual certification types in the system
-- This shows what certifications exist and can be assigned to operators

SELECT 
    CT.Id AS CertTypeID,
    CT.Name AS CertificationName,
    CT.Description,
    CT.Category,
    CT.IsRequired,
    CT.ExpirationDays,
    CT.IsActive
FROM dbo.pay_CertTypes CT
WHERE (CT.IsDeleted IS NULL OR CT.IsDeleted = 0)
    AND (CT.IsActive IS NULL OR CT.IsActive = 1)
ORDER BY 
    CT.Category,
    CT.Name;

---

-- Query 2: Get certification requirements by status
-- This links specific cert types to specific status steps

SELECT 
    SR.StatusTypeID,
    ST.OrderID AS StepNumber,
    ST.Status AS StatusName,
    ST.DivisionID,
    SR.CertTypeID,
    CT.Name AS CertificationName,
    CT.Description AS CertDescription,
    SR.IsRequired,
    SR.ValidationOrder
FROM dbo.pay_StatusRequirements SR
INNER JOIN dbo.pay_StatusTypes ST ON SR.StatusTypeID = ST.Id
INNER JOIN dbo.pay_CertTypes CT ON SR.CertTypeID = CT.Id
INNER JOIN dbo.pay_PizzaStatuses PS ON ST.PizzaStatusID = PS.ID
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
    CAST(ST.OrderID AS INT),
    SR.ValidationOrder;

---

-- Query 3: Alternative - Get all certs for operators at specific status
-- If there's no StatusRequirements table, this finds patterns

SELECT 
    ST.OrderID AS StepNumber,
    ST.Status AS StatusName,
    ST.DivisionID,
    C.CertificationTypeID,
    COUNT(DISTINCT O.Id) AS OperatorCount
FROM dbo.pay_Operators O
INNER JOIN dbo.pay_StatusTypes ST ON O.CurrentStatus = ST.Status AND O.DivisionID = ST.DivisionID
INNER JOIN dbo.pay_Certifications C ON O.Id = C.OperatorId
WHERE (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0)
    AND C.IsVerified = 1
    AND C.IsExpired = 0
    AND (ST.DivisionID LIKE '2 - IL%' 
        OR ST.DivisionID LIKE '3 - TX%' 
        OR ST.DivisionID LIKE '5 - CA%' 
        OR ST.DivisionID LIKE '6 - FL%' 
        OR ST.DivisionID LIKE '7 - MI%' 
        OR ST.DivisionID LIKE '8 - OH%' 
        OR ST.DivisionID LIKE '10 - OR%' 
        OR ST.DivisionID LIKE '11 - GA%' 
        OR ST.DivisionID LIKE '12 - PA%')
GROUP BY 
    ST.OrderID,
    ST.Status,
    ST.DivisionID,
    C.CertificationTypeID
HAVING COUNT(DISTINCT O.Id) >= 3  -- Only show certs held by multiple operators
ORDER BY 
    CAST(LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS INT),
    CAST(ST.OrderID AS INT),
    COUNT(DISTINCT O.Id) DESC;

---

-- Query 4: Get all unique certification type IDs currently in use
-- This helps identify what cert types are actually being tracked

SELECT DISTINCT
    C.CertificationTypeID,
    COUNT(DISTINCT C.OperatorId) AS TotalOperators,
    COUNT(CASE WHEN C.IsVerified = 1 THEN 1 END) AS VerifiedCount,
    COUNT(CASE WHEN C.IsExpired = 0 THEN 1 END) AS ActiveCount
FROM dbo.pay_Certifications C
GROUP BY C.CertificationTypeID
ORDER BY COUNT(DISTINCT C.OperatorId) DESC;
