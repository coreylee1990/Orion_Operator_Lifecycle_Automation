USE Orion;

-- Query 1: Get all Statuses that require Certifications (CertFlag = 1)
-- This shows which steps in the 14-step process are gated by certification requirements

SELECT 
    CAST(ST.OrderID AS INT) AS StepNumber,
    ST.Status AS StatusName,
    ST.CertFlag AS RequiresCert,
    COUNT(DISTINCT ST.DivisionID) AS DivisionsWithThisStep,
    STRING_AGG(DISTINCT ST.DivisionID, ', ') AS Divisions
FROM dbo.pay_StatusTypes ST
INNER JOIN dbo.pay_PizzaStatuses PS ON ST.PizzaStatusID = PS.ID
WHERE PS.IsOperator = 1
    AND (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0)
    AND ST.CertFlag = 1
GROUP BY 
    ST.OrderID,
    ST.Status,
    ST.CertFlag
ORDER BY 
    CAST(ST.OrderID AS INT);

---

-- Query 2: Get Certification History for a Specific Operator
-- Shows what certs an operator currently holds

SELECT 
    O.Id AS OperatorID,
    O.FirstName + ' ' + O.LastName AS OperatorName,
    O.DivisionID,
    O.StatusOrderSequence AS CurrentStep,
    O.CurrentStatus,
    C.CertificationTypeID,
    C.IsVerified,
    C.IsExpired,
    C.RecordAt AS CertDate
FROM dbo.pay_Operators O
LEFT JOIN dbo.pay_Certifications C ON O.Id = C.OperatorId
WHERE O.Id = @OperatorID
ORDER BY 
    C.RecordAt DESC;

---

-- Query 3: Gap Analysis - What Certs are Missing for Next Step
-- For an operator at StepN, show what's required for Step N+1

DECLARE @CurrentStep INT = 4; -- Example: Operator is at Step 4
DECLARE @OperatorID NVARCHAR(MAX) = 'ECB643B9-18BB-4DD7-8D16-274E8F456CAD';

SELECT 
    @CurrentStep AS CurrentStep,
    @CurrentStep + 1 AS NextStep,
    ST.Status AS NextStatusName,
    ST.CertFlag AS NextStepRequiresCert,
    O.FirstName + ' ' + O.LastName AS OperatorName,
    O.DivisionID,
    -- Get certs the operator has
    (SELECT STRING_AGG(C.CertificationTypeID, ', ')
     FROM dbo.pay_Certifications C
     WHERE C.OperatorId = O.Id AND C.IsVerified = 1 AND C.IsExpired = 0
    ) AS ValidCertifications,
    -- This indicates whether step N+1 is gated (you'll need to match actual cert types from data)
    CASE 
        WHEN ST.CertFlag = 1 THEN 'Certification Required'
        ELSE 'No Certification Required'
    END AS NextStepRequirement
FROM dbo.pay_Operators O
CROSS JOIN dbo.pay_StatusTypes ST
WHERE O.Id = @OperatorID
    AND CAST(ST.OrderID AS INT) = @CurrentStep + 1
    AND CAST(ST.OrderID AS INT) <= 14;

---

-- Query 4: Division-Level Cert Requirements Overview
-- Show for each division, which steps require certs

SELECT 
    LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS DivisionNumber,
    ST.DivisionID,
    CSELECT 
    LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS DivisionNumber,
    ST.DivisionID,
    CAST(ST.OrderID AS INT) AS StepNumber,
    ST.Status AS StatusName,
    ST.CertFlag AS RequiresCert,
    ST.Id AS StatusID
FROM Orion.dbo.pay_StatusTypes ST
INNER JOIN Orion.dbo.pay_PizzaStatuses PS ON ST.PizzaStatusID = PS.ID
WHERE PS.IsOperator = 1
    AND (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0)
ORDER BY 
    CAST(LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS INT),
    CAST(ST.OrderID AS INT);
AST(ST.OrderID AS INT) AS StepNumber,
    ST.Status AS StatusName,
    ST.CertFlag AS RequiresCert,
    ST.Id AS StatusID
FROM dbo.pay_StatusTypes ST
INNER JOIN dbo.pay_PizzaStatuses PS ON ST.PizzaStatusID = PS.ID
WHERE PS.IsOperator = 1
    AND (ST.isDeleted IS NULL OR ST.isDeleted = 0)
    AND (ST.Fleet IS NULL OR ST.Fleet = 0)
    AND (ST.Providers IS NULL OR ST.Providers = 0)
ORDER BY 
    CAST(LEFT(ST.DivisionID, CHARINDEX(' ', ST.DivisionID) - 1) AS INT),
    CAST(ST.OrderID AS INT);
