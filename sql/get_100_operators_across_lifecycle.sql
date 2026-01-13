-- Get ~100 operators spread across lifecycle statuses and divisions
-- Focuses on the 14 key lifecycle statuses
-- Distributes operators across divisions for better analysis coverage

WITH StatusList AS (
  -- Define the lifecycle statuses we want to analyze
  SELECT 'REGISTRATION' AS StatusName, 1 AS StepOrder
  UNION ALL SELECT 'ONBOARDING', 2
  UNION ALL SELECT 'CREDENTIALING', 3
  UNION ALL SELECT 'DOT SCREENING', 4
  UNION ALL SELECT 'ORIENTATION-BIG STAR SAFETY & SERVICE', 5
  UNION ALL SELECT 'ORIENTATION-CLIENT HOSTED', 6
  UNION ALL SELECT 'APPROVED FOR CHO (CLIENT HOSTED)', 7
  UNION ALL SELECT 'APPROVED-ORIENTATION BTW', 8
  UNION ALL SELECT 'COMPLIANCE REVIEW', 9
  UNION ALL SELECT 'SBPC APPROVED FOR SERVICE', 10
  UNION ALL SELECT 'APPROVED FOR SERVICE', 11
  UNION ALL SELECT 'APPROVED FOR CONTRACTING', 12
  UNION ALL SELECT 'APPROVED FOR LEASING', 13
  UNION ALL SELECT 'IN-SERVICE', 14
),
OperatorsWithStatus AS (
  SELECT 
    o.*,
    st.Status AS StatusName,
    st.OrderID,
    -- Create a ranking to spread operators across divisions within each status
    ROW_NUMBER() OVER (
      PARTITION BY st.Status 
      ORDER BY o.DivisionID, o.ID
    ) AS StatusDivisionRank,
    -- Count how many operators are in this status
    COUNT(*) OVER (PARTITION BY st.Status) AS StatusTotal
  FROM dbo.pay_Operators o
  INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
  INNER JOIN StatusList sl ON st.Status = sl.StatusName
  WHERE ISNULL(o.isDeleted, 0) = 0
),
BalancedSelection AS (
  SELECT 
    *,
    -- Calculate how many from each status (aim for ~7 per status for 100 total)
    -- But adjust based on availability
    CASE 
      WHEN StatusTotal >= 10 THEN 10  -- If lots available, take 10
      WHEN StatusTotal >= 5 THEN 7    -- If decent amount, take 7
      ELSE StatusTotal                 -- Otherwise take all
    END AS TargetPerStatus
  FROM OperatorsWithStatus
)
SELECT 
  -- Core Identity
  ID,
  FirstName,
  LastName,
  Email,
  Mobile,
  Birthdate,
  -- Location
  Address1,
  Address2,
  City,
  State,
  Zip,
  DivisionID,
  -- Status & Lifecycle (CRITICAL)
  Status,
  StatusID,
  StatusName,
  OrderID,
  StartDate,
  TermDate,
  LastStatusDate,
  -- License Information
  LicenseNbr,
  LicenseState,
  LicenseExp,
  Class,
  -- System Tracking
  isDeleted,
  DateCreated,
  RecordAt,
  RecordBy,
  UpdateAt,
  UpdateBy,
  -- Analysis Fields
  StatusDivisionRank,
  StatusTotal,
  TargetPerStatus
FROM BalancedSelection
WHERE StatusDivisionRank <= TargetPerStatus
ORDER BY OrderID, DivisionID, ID;
