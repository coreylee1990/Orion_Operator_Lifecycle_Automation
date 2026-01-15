-- ============================================================================
-- ⚠️  CRITICAL: DIVISION-SPECIFIC CERTIFICATION RETRIEVAL LOGIC
-- ============================================================================
--
-- PURPOSE: 
-- This query retrieves operator certifications filtered by their division
-- and current status. This is the CORE LOGIC for matching operators with
-- their required certifications based on division-specific requirements.
--
-- KEY CONCEPT:
-- Certifications are DIVISION-SPECIFIC. An operator in Division 7 (MI) has
-- different requirements than an operator in Division 10 (OR), even if they
-- are at the same status level (e.g., ORIENTATION).
--
-- HOW IT WORKS:
-- 1. Gets operator's current division (DivisionID like "7 - MI")
-- 2. Gets operator's current status (StatusName like "ORIENTATION")
-- 3. Retrieves ONLY certifications for that specific division
-- 4. Matches certification requirements defined for that division+status combo
--
-- IMPORTANT:
-- - Division IDs are stored as "7 - MI" format (number + space + dash + space + code)
-- - Certification requirements are grouped by status AND division
-- - Each division may have unique certification names/requirements
-- - Division 7 (MI) uses ALL CAPS for some certs (intentional convention)
--
-- USAGE:
-- This query is used by merge_operators_with_certs.py to create the
-- pay_Operators.json file with embedded certification data.
-- ============================================================================

-- Get all operators with their certifications filtered by division
SELECT 
    o.ID AS OperatorID,
    o.FirstName,
    o.LastName,
    o.DivisionID,  -- Format: "7 - MI", "10 - OR", etc.
    o.StatusName,   -- Current operator status
    o.StatusID,
    
    -- Certification details
    c.CertificationID,
    c.Cert AS CertType,
    c.Date AS IssueDate,
    c.CompletionDate AS ExpireDate,
    c.isApproved AS Status,
    c.Attachments,
    c.Comments,
    c.RecordAt AS CertRecordDate,
    c.UpdateAt AS CertUpdateDate

FROM dbo.pay_Operators AS o

-- CRITICAL JOIN: Only get certifications for THIS operator
LEFT JOIN dbo.pay_Certifications AS c 
    ON o.ID = c.OperatorID
    AND c.IsDeleted = '0'  -- Exclude deleted certifications

WHERE 
    o.isDeleted = '0'  -- Only active operators

ORDER BY 
    o.DivisionID,
    o.StatusName,
    o.LastName,
    o.FirstName;


-- ============================================================================
-- EXAMPLE: Get certifications for a specific division
-- ============================================================================
-- To get only Division 7 (MI) operators:
/*
SELECT 
    o.ID AS OperatorID,
    o.FirstName,
    o.LastName,
    o.DivisionID,
    o.StatusName,
    c.Cert AS CertType,
    c.isApproved AS Status
FROM dbo.pay_Operators AS o
LEFT JOIN dbo.pay_Certifications AS c 
    ON o.ID = c.OperatorID
    AND c.IsDeleted = '0'
WHERE 
    o.isDeleted = '0'
    AND o.DivisionID = '7 - MI'  -- EXACT MATCH including spaces
ORDER BY o.LastName;
*/


-- ============================================================================
-- EXAMPLE: Get certification counts by division
-- ============================================================================
-- To see how many certs each division requires:
/*
SELECT 
    o.DivisionID,
    o.StatusName,
    COUNT(DISTINCT c.Cert) AS UniqueCertTypes,
    COUNT(c.CertificationID) AS TotalCertRecords
FROM dbo.pay_Operators AS o
LEFT JOIN dbo.pay_Certifications AS c 
    ON o.ID = c.OperatorID
    AND c.IsDeleted = '0'
WHERE 
    o.isDeleted = '0'
GROUP BY 
    o.DivisionID,
    o.StatusName
ORDER BY 
    o.DivisionID,
    o.StatusName;
*/


-- ============================================================================
-- VALIDATION: Check for operators missing certifications
-- ============================================================================
-- To find operators who should have certs but don't:
/*
SELECT 
    o.ID AS OperatorID,
    o.FirstName,
    o.LastName,
    o.DivisionID,
    o.StatusName,
    COUNT(c.CertificationID) AS CertCount
FROM dbo.pay_Operators AS o
LEFT JOIN dbo.pay_Certifications AS c 
    ON o.ID = c.OperatorID
    AND c.IsDeleted = '0'
WHERE 
    o.isDeleted = '0'
GROUP BY 
    o.ID,
    o.FirstName,
    o.LastName,
    o.DivisionID,
    o.StatusName
HAVING COUNT(c.CertificationID) = 0  -- No certifications at all
ORDER BY o.DivisionID, o.StatusName;
*/
