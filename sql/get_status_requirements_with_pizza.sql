-- ============================================================================
-- Export Status Requirements with Pizza Status Mapping
-- ============================================================================
-- This query exports the definitive mapping:
--   Status + Division → Pizza Status → Required Cert Types
-- ============================================================================

USE Orion;

SELECT 
    ST.Id AS StatusTypeID,
    ST.Status AS StatusName,
    ST.OrderID AS StatusOrder,
    ST.DivisionID,
    ST.PizzaStatusID,
    PS.Status AS PizzaStatusName,
    PS.Description AS PizzaStatusDescription,
    SR.CertTypeID,
    CT.Name AS CertificationName,
    CT.Description AS CertDescription,
    SR.IsRequired,
    SR.ValidationOrder,
    CT.Category AS CertCategory,
    CT.ExpirationDays,
    CT.IsActive AS CertIsActive
FROM dbo.pay_StatusTypes ST
LEFT JOIN dbo.pay_PizzaStatuses PS 
    ON ST.PizzaStatusID = PS.ID
LEFT JOIN dbo.pay_StatusRequirements SR 
    ON ST.Id = SR.StatusTypeID
LEFT JOIN dbo.pay_CertTypes CT 
    ON SR.CertTypeID = CT.Id
WHERE 
    -- Only operator statuses
    (PS.IsOperator = 1 OR PS.IsOperator IS NULL)
    -- Only active, non-deleted statuses
    AND (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0 OR ST.Providers = 1)
    -- Only our actual divisions (exclude test/inactive)
    AND (ST.DivisionID LIKE '2 - IL%' 
        OR ST.DivisionID LIKE '3 - TX%' 
        OR ST.DivisionID LIKE '5 - CA%' 
        OR ST.DivisionID LIKE '6 - FL%' 
        OR ST.DivisionID LIKE '7 - MI%' 
        OR ST.DivisionID LIKE '8 - OH%' 
        OR ST.DivisionID LIKE '9 - AZ%' 
        OR ST.DivisionID LIKE '10 - OR%' 
        OR ST.DivisionID LIKE '11 - GA%' 
        OR ST.DivisionID LIKE '12 - PA%')
ORDER BY 
    -- Sort by division number
    CAST(LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS INT),
    -- Then by status order
    CAST(ST.OrderID AS INT),
    -- Then by validation order within status
    SR.ValidationOrder,
    -- Finally by cert name
    CT.Name;

-- ============================================================================
-- USAGE:
-- 1. Run this query in SQL Server Management Studio
-- 2. Export results as JSON: 
--    - Results → Save As → JSON
-- 3. Save to: data/pay_StatusRequirements.json
-- 4. This becomes the authoritative source for: Status → Required Certs
-- ============================================================================
