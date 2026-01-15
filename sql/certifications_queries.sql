-- =====================================================
-- SQL Server Queries for Certifications Analysis
-- =====================================================

-- =====================================================
-- 1. GET ALL CERTIFICATIONS WITH OPERATOR DETAILS
-- =====================================================
SELECT 
    c.ID AS CertificationID,
    c.Cert AS CertificationName,
    c.CertTypeID,
    o.OperatorID,
    o.FirstName,
    o.LastName,
    o.DivisionID,
    o.CurrentStatus,
    o.StatusName,
    c.Date AS CertificationDate,
    c.CompletionDate,
    c.ApprovedDate,
    c.isApproved,
    c.ApprovedBy,
    c.IsDeleted,
    c.RecordAt AS CreatedAt,
    c.UpdateAt AS LastUpdated
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
WHERE c.IsDeleted = 0
ORDER BY o.LastName, o.FirstName, c.CompletionDate DESC;

-- =====================================================
-- 2. GET CERTIFICATIONS BY OPERATOR
-- =====================================================
SELECT 
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    o.DivisionID,
    o.CurrentStatus,
    COUNT(c.ID) AS TotalCertifications,
    SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) AS ApprovedCount,
    SUM(CASE WHEN c.IsRejected = 1 THEN 1 ELSE 0 END) AS RejectedCount,
    SUM(CASE WHEN c.isDisapproved = 1 THEN 1 ELSE 0 END) AS DisapprovedCount,
    SUM(CASE WHEN c.isApproved = 0 AND c.IsRejected = 0 AND c.isDisapproved = 0 THEN 1 ELSE 0 END) AS PendingCount
FROM pay_Operators o
LEFT JOIN pay_Certifications c ON o.OperatorID = c.OperatorID AND c.IsDeleted = 0
GROUP BY o.OperatorID, o.FirstName, o.LastName, o.DivisionID, o.CurrentStatus
ORDER BY o.LastName, o.FirstName;

-- =====================================================
-- 3. GET PENDING CERTIFICATIONS REQUIRING APPROVAL
-- =====================================================
SELECT 
    c.ID AS CertificationID,
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    o.DivisionID,
    o.CurrentStatus,
    c.Cert AS CertificationName,
    c.CompletionDate,
    c.RecordAt AS SubmittedAt,
    DATEDIFF(DAY, c.RecordAt, GETDATE()) AS DaysPending,
    c.Comments
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
WHERE c.IsDeleted = 0
  AND c.isApproved = 0
  AND c.IsRejected = 0
  AND c.isDisapproved = 0
ORDER BY c.RecordAt ASC;

-- =====================================================
-- 4. CERTIFICATION COUNTS BY DIVISION
-- =====================================================
SELECT 
    o.DivisionID,
    COUNT(DISTINCT o.OperatorID) AS TotalOperators,
    COUNT(c.ID) AS TotalCertifications,
    AVG(CASE WHEN c.ID IS NOT NULL THEN 1.0 ELSE 0 END) AS AvgCertsPerOperator,
    SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) AS ApprovedCerts,
    SUM(CASE WHEN c.isApproved = 0 AND c.IsDeleted = 0 THEN 1 ELSE 0 END) AS PendingCerts
FROM pay_Operators o
LEFT JOIN pay_Certifications c ON o.OperatorID = c.OperatorID AND c.IsDeleted = 0
GROUP BY o.DivisionID
ORDER BY o.DivisionID;

-- =====================================================
-- 5. CERTIFICATION TYPES BY FREQUENCY
-- =====================================================
SELECT 
    c.Cert AS CertificationType,
    COUNT(*) AS TotalIssued,
    SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) AS ApprovedCount,
    SUM(CASE WHEN c.IsRejected = 1 THEN 1 ELSE 0 END) AS RejectedCount,
    AVG(DATEDIFF(DAY, c.RecordAt, c.ApprovedDate)) AS AvgDaysToApproval
FROM pay_Certifications c
WHERE c.IsDeleted = 0
GROUP BY c.Cert
HAVING COUNT(*) > 10  -- Only show certifications with more than 10 instances
ORDER BY TotalIssued DESC;

-- =====================================================
-- 6. OPERATORS WITH MISSING REQUIRED CERTIFICATIONS
-- =====================================================
-- Note: Adjust the required certification list based on your business rules
-- Top certification types from actual data:
--   1. Defensive Driving (105)
--   2. Social Security Card (103)
--   3. Orientation-Big Star Safety and Service (98)
--   4. CTAA Passenger Assistance (98)
--   5. Drivers License (92)
WITH RequiredCerts AS (
    SELECT 'Defensive Driving' AS RequiredCert
    UNION ALL SELECT 'BackgroundCheck'
    UNION ALL SELECT 'DOT Physical Card'
    UNION ALL SELECT 'Motor Vehicle Report (MVR)'
    UNION ALL SELECT 'Drivers License'
),
OperatorCerts AS (
    SELECT DISTINCT
        o.OperatorID,
        o.FirstName + ' ' + o.LastName AS OperatorName,
        o.DivisionID,
        o.CurrentStatus,
        c.Cert
    FROM pay_Operators o
    LEFT JOIN pay_Certifications c ON o.OperatorID = c.OperatorID 
        AND c.IsDeleted = 0 
        AND c.isApproved = 1
)
SELECT 
    oc.OperatorID,
    oc.OperatorName,
    oc.DivisionID,
    oc.CurrentStatus,
    rc.RequiredCert AS MissingCertification
FROM OperatorCerts oc
CROSS JOIN RequiredCerts rc
WHERE NOT EXISTS (
    SELECT 1 
    FROM OperatorCerts oc2 
    WHERE oc2.OperatorID = oc.OperatorID 
      AND oc2.Cert LIKE '%' + rc.RequiredCert + '%'
)
ORDER BY oc.OperatorName, rc.RequiredCert;

-- =====================================================
-- 7. CERTIFICATION APPROVAL TIMELINE
-- =====================================================
SELECT 
    c.ID AS CertificationID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    c.Cert AS CertificationName,
    c.RecordAt AS SubmittedDate,
    c.ApprovedDate,
    DATEDIFF(DAY, c.RecordAt, c.ApprovedDate) AS DaysToApproval,
    DATEDIFF(HOUR, c.RecordAt, c.ApprovedDate) AS HoursToApproval,
    approver.FirstName + ' ' + approver.LastName AS ApprovedByName
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
LEFT JOIN pay_Operators approver ON c.ApprovedBy = approver.OperatorID
WHERE c.IsDeleted = 0
  AND c.isApproved = 1
  AND c.ApprovedDate IS NOT NULL
ORDER BY c.ApprovedDate DESC;

-- =====================================================
-- 8. REJECTED/DISAPPROVED CERTIFICATIONS WITH REASONS
-- =====================================================
SELECT 
    c.ID AS CertificationID,
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    o.DivisionID,
    c.Cert AS CertificationName,
    CASE 
        WHEN c.IsRejected = 1 THEN 'Rejected'
        WHEN c.isDisapproved = 1 THEN 'Disapproved'
        ELSE 'Unknown'
    END AS Status,
    COALESCE(c.RejectReason, c.DisapprovalReason) AS Reason,
    COALESCE(c.RejectedAt, c.DisapprovedAt) AS ActionDate,
    c.Comments
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
WHERE c.IsDeleted = 0
  AND (c.IsRejected = 1 OR c.isDisapproved = 1)
ORDER BY COALESCE(c.RejectedAt, c.DisapprovedAt) DESC;

-- =====================================================
-- 9. CERTIFICATION SOURCE CHANNEL ANALYSIS
-- =====================================================
SELECT 
    CASE 
        WHEN c.isMobile = 1 THEN 'Mobile App'
        WHEN c.isProviderPortal = 1 THEN 'Provider Portal'
        WHEN c.isOperatorPortal = 1 THEN 'Operator Portal'
        WHEN c.isBackOffice = 1 THEN 'Back Office'
        ELSE 'Unknown'
    END AS SubmissionChannel,
    COUNT(*) AS TotalSubmissions,
    SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) AS ApprovedCount,
    CAST(SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS ApprovalRate,
    AVG(DATEDIFF(HOUR, c.RecordAt, c.ApprovedDate)) AS AvgHoursToApproval
FROM pay_Certifications c
WHERE c.IsDeleted = 0
GROUP BY 
    CASE 
        WHEN c.isMobile = 1 THEN 'Mobile App'
        WHEN c.isProviderPortal = 1 THEN 'Provider Portal'
        WHEN c.isOperatorPortal = 1 THEN 'Operator Portal'
        WHEN c.isBackOffice = 1 THEN 'Back Office'
        ELSE 'Unknown'
    END
ORDER BY TotalSubmissions DESC;

-- =====================================================
-- 10. OPERATORS BY STATUS WITH CERTIFICATION COUNTS
-- =====================================================
SELECT 
    o.CurrentStatus,
    o.StatusName,
    COUNT(DISTINCT o.OperatorID) AS OperatorCount,
    COUNT(c.ID) AS TotalCertifications,
    SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) AS ApprovedCertifications,
    SUM(CASE WHEN c.isApproved = 0 AND c.IsDeleted = 0 THEN 1 ELSE 0 END) AS PendingCertifications,
    CAST(SUM(CASE WHEN c.isApproved = 1 THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(c.ID), 0) AS DECIMAL(5,2)) AS ApprovalRate
FROM pay_Operators o
LEFT JOIN pay_Certifications c ON o.OperatorID = c.OperatorID AND c.IsDeleted = 0
GROUP BY o.CurrentStatus, o.StatusName
ORDER BY o.StatusName;

-- =====================================================
-- 11. GET SPECIFIC OPERATOR'S CERTIFICATION HISTORY
-- =====================================================
DECLARE @OperatorID UNIQUEIDENTIFIER = 'EA9942C7-540F-4443-9743-D1B2B58DD050'; -- Example

SELECT 
    c.ID AS CertificationID,
    c.Cert AS CertificationName,
    c.Date AS CertificationDate,
    c.CompletionDate,
    c.RecordAt AS SubmittedAt,
    c.ApprovedDate,
    c.isApproved,
    CASE 
        WHEN c.IsRejected = 1 THEN 'Rejected'
        WHEN c.isDisapproved = 1 THEN 'Disapproved'
        WHEN c.isApproved = 1 THEN 'Approved'
        ELSE 'Pending'
    END AS Status,
    c.Comments,
    c.Attachments,
    c.IsDeleted
FROM pay_Certifications c
WHERE c.OperatorID = @OperatorID
ORDER BY c.CompletionDate DESC, c.RecordAt DESC;

-- =====================================================
-- 12. EXPIRING CERTIFICATIONS (Assuming expiry logic)
-- =====================================================
-- Note: Adjust the expiry period based on certification type
SELECT 
    c.ID AS CertificationID,
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    o.DivisionID,
    c.Cert AS CertificationName,
    c.CompletionDate,
    DATEADD(YEAR, 1, c.CompletionDate) AS ExpiryDate, -- Assuming 1-year validity
    DATEDIFF(DAY, GETDATE(), DATEADD(YEAR, 1, c.CompletionDate)) AS DaysUntilExpiry
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
WHERE c.IsDeleted = 0
  AND c.isApproved = 1
  AND c.CompletionDate IS NOT NULL
  AND DATEADD(YEAR, 1, c.CompletionDate) BETWEEN GETDATE() AND DATEADD(DAY, 90, GETDATE())
ORDER BY ExpiryDate ASC;

-- =====================================================
-- 13. CERTIFICATION COMPLETENESS BY OPERATOR STATUS
-- =====================================================
-- Analyze certification completion rates by operator lifecycle status
SELECT 
    o.CurrentStatus,
    o.StatusName,
    COUNT(DISTINCT o.OperatorID) AS TotalOperators,
    SUM(CASE WHEN cert_counts.cert_count > 0 THEN 1 ELSE 0 END) AS OperatorsWithCerts,
    AVG(COALESCE(cert_counts.cert_count, 0)) AS AvgCertsPerOperator,
    AVG(COALESCE(cert_counts.approved_count, 0)) AS AvgApprovedPerOperator,
    CAST(SUM(CASE WHEN cert_counts.cert_count > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT o.OperatorID) AS DECIMAL(5,1)) AS PctWithCerts
FROM pay_Operators o
LEFT JOIN (
    SELECT 
        OperatorID,
        COUNT(*) AS cert_count,
        SUM(CASE WHEN isApproved = 1 THEN 1 ELSE 0 END) AS approved_count
    FROM pay_Certifications
    WHERE IsDeleted = 0
    GROUP BY OperatorID
) cert_counts ON o.OperatorID = cert_counts.OperatorID
GROUP BY o.CurrentStatus, o.StatusName
ORDER BY o.StatusName;

-- =====================================================
-- 14. AI-REVIEWED CERTIFICATIONS
-- =====================================================
-- Track certifications that have been processed by AI review
SELECT 
    c.ID AS CertificationID,
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    c.Cert AS CertificationName,
    c.AIReviewed,
    c.AIRecommendation,
    c.AINotes,
    c.isApproved,
    c.ApprovedDate,
    c.RecordAt AS SubmittedDate
FROM pay_Certifications c
INNER JOIN pay_Operators o ON c.OperatorID = o.OperatorID
WHERE c.IsDeleted = 0
  AND c.AIReviewed = 1
ORDER BY c.RecordAt DESC;

-- =====================================================
-- 15. CERTIFICATION WORKFLOW EFFICIENCY
-- =====================================================
-- Analyze time taken at each stage of certification workflow
WITH CertTimeline AS (
    SELECT 
        c.ID,
        c.Cert AS CertificationType,
        c.RecordAt AS SubmittedDate,
        c.ESignSendAt,
        c.ESignUpdatedAt,
        c.ApprovedDate,
        c.RejectedAt,
        c.DisapprovedAt,
        DATEDIFF(HOUR, c.RecordAt, c.ESignSendAt) AS HoursToESignSend,
        DATEDIFF(HOUR, c.ESignSendAt, c.ESignUpdatedAt) AS HoursToESignComplete,
        DATEDIFF(HOUR, c.RecordAt, c.ApprovedDate) AS HoursToApproval,
        CASE 
            WHEN c.isApproved = 1 THEN 'Approved'
            WHEN c.IsRejected = 1 THEN 'Rejected'
            WHEN c.isDisapproved = 1 THEN 'Disapproved'
            ELSE 'Pending'
        END AS FinalStatus
    FROM pay_Certifications c
    WHERE c.IsDeleted = 0
      AND c.RecordAt IS NOT NULL
)
SELECT 
    CertificationType,
    FinalStatus,
    COUNT(*) AS TotalCertifications,
    AVG(HoursToApproval) AS AvgHoursToApproval,
    MIN(HoursToApproval) AS MinHoursToApproval,
    MAX(HoursToApproval) AS MaxHoursToApproval,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY HoursToApproval) OVER (PARTITION BY CertificationType, FinalStatus) AS MedianHoursToApproval
FROM CertTimeline
WHERE HoursToApproval IS NOT NULL
GROUP BY CertificationType, FinalStatus
HAVING COUNT(*) >= 5  -- Only show types with at least 5 certifications
ORDER BY CertificationType, FinalStatus;

-- =====================================================
-- 16. OPERATORS MISSING CRITICAL CERTIFICATIONS
-- =====================================================
-- Find operators in active statuses who are missing high-frequency certifications
WITH TopCerts AS (
    -- Get the most common certification types
    SELECT TOP 10
        Cert AS CertName,
        COUNT(*) AS Frequency
    FROM pay_Certifications
    WHERE IsDeleted = 0 AND Cert IS NOT NULL
    GROUP BY Cert
    ORDER BY COUNT(*) DESC
)
SELECT DISTINCT
    o.OperatorID,
    o.FirstName + ' ' + o.LastName AS OperatorName,
    o.DivisionID,
    o.CurrentStatus,
    tc.CertName AS MissingCertification,
    tc.Frequency AS CertFrequency
FROM pay_Operators o
CROSS JOIN TopCerts tc
WHERE o.CurrentStatus IN ('REGISTRATION', 'ONBOARDING', 'CREDENTIALING', 'DOT SCREENING')
  AND NOT EXISTS (
    SELECT 1 
    FROM pay_Certifications c
    WHERE c.OperatorID = o.OperatorID 
      AND c.Cert = tc.CertName
      AND c.IsDeleted = 0
      AND c.isApproved = 1
  )
ORDER BY o.OperatorName, tc.Frequency DESC;
