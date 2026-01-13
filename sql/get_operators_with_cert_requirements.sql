USE Orion;

/*
  Get All Operators with Actual Certification Data
  
  This query replicates the functionality of parse_operators_to_json.py
  - Retrieves all operator data from pay_Operators table
  - Joins with pay_StatusTypes and pay_PizzaStatus for status information
  - Shows ACTUAL certifications operators have (derived from pay_Certifications)
  - Shows if status requires certs (from CertFlag in pay_StatusTypes)
  
  NOTE: There is NO table in the database that defines WHICH specific certifications
        are required for each status. The database only has:
        - pay_StatusTypes.CertFlag (boolean) - indicates IF certs are needed
        - pay_Certifications - tracks what certs operators currently have
  
  To get actual cert requirements per status, you need to either:
  1. Create a new table: pay_StatusCertRequirements (StatusTypeID, CertTypeID)
  2. Add a StatusTypeID column to pay_CertTypes
  3. Analyze patterns from operators who successfully progressed through statuses
  
  This query shows what certs operators ACTUALLY HAVE at their current status.
*/

-- Step 1: Get top certifications operators have at each status (pattern analysis)
WITH StatusCertPatterns AS (
    SELECT 
        o.StatusName,
        o.OrderID,
        c.Cert,
        COUNT(DISTINCT c.OperatorId) AS OperatorCount
    FROM dbo.pay_Certifications c
    INNER JOIN dbo.pay_Operators o ON c.OperatorId = o.ID
    INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
    WHERE 
        ISNULL(c.IsDeleted, 0) = 0
        AND ISNULL(o.isDeleted, 0) = 0
        AND c.Cert IS NOT NULL
        AND LTRIM(RTRIM(c.Cert)) != ''
    GROUP BY st.Status, c.Cert
),

-- Step 2: Rank certs by frequency within each status (top 5 most common)
TopCertsPerStatus AS (
    SELECT 
        StatusName,
        STRING_AGG(Cert, ', ') WITHIN GROUP (ORDER BY OperatorCount DESC) AS TopCerts,
        COUNT(*) AS UniqueCertTypes
    FROM (
        SELECT 
            StatusName,
            Cert,
            OperatorCount,
            ROW_NUMBER() OVER (PARTITION BY StatusName ORDER BY OperatorCount DESC) AS rn
        FROM StatusCertPatterns
    ) ranked
    WHERE rn <= 5  -- Top 5 most common certs per status
    GROUP BY StatusName
),

-- Step 3: Get all operators with their status information
OperatorData AS (
    SELECT 
        o.ID               AS OperatorID,
        o.FirstName,
        o.LastName,
        o.DivisionID,
        o.Status           AS CurrentStatus,
        st.Status          AS StatusName,
        CAST(st.OrderID AS INT) AS OrderID,
        st.Id              AS StatusTypeID,
        st.PizzaStatusID,
        ps.Status          AS PizzaStatus,
        st.CertFlag        AS StatusRequiresCerts
    FROM dbo.pay_Operators      AS o
    INNER JOIN dbo.pay_StatusTypes AS st
        ON o.StatusID = st.Id
    LEFT JOIN dbo.pay_PizzaStatus AS ps
        ON st.PizzaStatusID = ps.ID
    WHERE 
        ISNULL(o.isDeleted, 0) = 0
        AND ISNULL(st.isDeleted, 0) = 0
        AND ISNULL(st.Fleet, 0) = 0
        AND ISNULL(st.Providers, 0) = 0
        AND ISNULL(ps.IsOperator, 0) = 1
),

-- Step 4: Get actual certs each operator has
OperatorCerts AS (
    SELECT 
        c.OperatorId,
        STRING_AGG(c.Cert, ', ') WITHIN GROUP (ORDER BY c.Cert) AS CertsHeld,
        COUNT(*) AS CertCount
    FROM dbo.pay_Certifications c
    WHERE 
        ISNULL(c.IsDeleted, 0) = 0
        AND c.Cert IS NOT NULL
        AND LTRIM(RTRIM(c.Cert)) != ''
    GROUP BY c.OperatorId
)

-- Final output: Join all data together
SELECT 
    od.OperatorID,
    od.FirstName,
    od.LastName,
    od.DivisionID,
    od.CurrentStatus,
    od.StatusName,
    od.OrderID,
    od.StatusTypeID,
    od.PizzaStatusID,
    od.PizzaStatus,
    od.StatusRequiresCerts,
    ISNULL(oc.CertsHeld, '') AS CertsCurrentlyHeld,
    ISNULL(oc.CertCount, 0) AS CertsHeldCount,
    ISNULL(tcp.TopCerts, '') AS CommonCertsForThisStatus,
    ISNULL(tcp.UniqueCertTypes, 0) AS TotalCertTypesForStatus
FROM OperatorData od
LEFT JOIN OperatorCerts oc
    ON od.OperatorID = oc.OperatorId
LEFT JOIN TopCertsPerStatus tcp
    ON od.StatusName = tcp.StatusName
ORDER BY 
    od.StatusName,
    od.OrderID,
    od.DivisionID,
    od.OperatorID;

/*
  OUTPUT EXPLANATION:
  
  - StatusRequiresCerts: Boolean from pay_StatusTypes.CertFlag
  - CertsCurrentlyHeld: Actual certifications this specific operator has
  - CertsHeldCount: Number of certs this operator has
  - CommonCertsForThisStatus: Top 5 most common certs that operators at this status have
  - TotalCertTypesForStatus: How many different cert types exist for this status
  
  IMPORTANT: 
  - CommonCertsForThisStatus shows patterns, NOT requirements
  - To establish actual requirements, business rules must be defined
  - Consider creating pay_StatusCertRequirements table with explicit mappings
*/
