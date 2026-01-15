USE Orion;

-- Get up to 4 operators from each operator lifecycle status
-- Filters: operator-only statuses (IsOperator=1), non-deleted, non-Fleet, non-Providers

WITH op_statuses AS (
  SELECT 
    o.ID,
    o.FirstName,
    o.LastName,
    o.Email,
    o.Mobile,
    o.Birthdate,
    o.Address1,
    o.Address2,
    o.City,
    o.State,
    o.Zip,
    o.DivisionID,
    o.Status,
    o.StatusID,
    o.StartDate,
    o.TermDate,
    o.LastStatusDate,
    o.LicenseNbr,
    o.LicenseState,
    o.LicenseExp,
    o.Class,
    o.isDeleted,
    o.DateCreated,
    o.RecordAt,
    o.RecordBy,
    o.UpdateAt,
    o.UpdateBy,
    st.Status          AS StatusName,
    st.OrderID,
    ROW_NUMBER() OVER (PARTITION BY st.Status ORDER BY o.ID) AS rn
  FROM dbo.pay_Operators      AS o
  INNER JOIN dbo.pay_StatusTypes AS st
    ON o.StatusID = st.Id
  LEFT JOIN dbo.pay_PizzaStatus AS ps
    ON st.PizzaStatusID = ps.ID
  WHERE 
    o.DivisionID IN ('2 - IL', '3 - TX', '5 - CA', '6 - FL', '7 - MI', '8 - OH', '10 - OR', '11 - GA', '12 - PA')
    AND ISNULL(o.isDeleted, 0) = 0
    AND ISNULL(st.isDeleted, 0) = 0
    AND ISNULL(st.Fleet, 0) = 0
    AND ISNULL(st.Providers, 0) = 0
    AND ISNULL(ps.IsOperator, 0) = 1
)
SELECT 
  OperatorID,
  FirstName,
  LastName,
  DivisionID,
  CurrentStatus,
  StatusName,
  OrderID,
  StatusTypeID,
  PizzaStatusID,
  PizzaStatus
FROM op_statuses
WHERE rn <= 4
ORDER BY StatusName, OrderID, DivisionID, OperatorID;
