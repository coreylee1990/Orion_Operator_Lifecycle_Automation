USE Orion;

/*
  Get ALL Certifications with ALL Fields for Operators in pay_Operators.json
  
  Returns every certification record for the 168 operators, including all 67 fields
  from the pay_Certifications table, plus operator context information.
*/

WITH OperatorList AS (
    -- Operators from pay_Operators with relevant fields for cert analysis
    SELECT 
        o.ID,
        o.FirstName,
        o.LastName,
        o.Email,
        o.Mobile,
        o.DivisionID,
        o.Status,
        o.StatusID,
        o.StatusName,
        o.OrderID,
        o.StartDate,
        o.LastStatusDate,
        o.DateCreated,
        o.RecordAt,
        o.UpdateAt
    FROM dbo.pay_Operators o
    INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
    LEFT JOIN dbo.pay_PizzaStatus ps ON st.PizzaStatusID = ps.ID
    WHERE 
        ISNULL(o.isDeleted, 0) = 0
        AND ISNULL(st.isDeleted, 0) = 0
        AND ISNULL(st.Fleet, 0) = 0
        AND ISNULL(st.Providers, 0) = 0
        AND ISNULL(ps.IsOperator, 0) = 1
)

-- Get ALL certification fields for these operators
SELECT 
    -- Operator context
    ol.OperatorID,
    ol.FirstName,
    ol.LastName,
    ol.DivisionID,
    ol.CurrentStatus,
    ol.StatusName,
    ol.OrderID,
    ol.StatusRequiresCerts,
    
    -- ALL Certification fields (67 fields from pay_Certifications)
    c.ID AS CertificationID,
    c.CertTypeID,
    c.FleetID,
    c.Cert,
    c.Date,
    c.Attachments,
    c.IsDeleted,
    c.ProviderID,
    c.isApproved,
    c.ApprovedBy,
    c.Comments,
    c.RecordAt,
    c.RecordBy,
    c.UpdateAt,
    c.UpdateBy,
    c.EsignStatus,
    c.DocumentID,
    c.FolderID,
    c.CompletionDate,
    c.ApprovedDate,
    c.SmsCount,
    c.isMobile,
    c.isProviderPortal,
    c.isOperatorPortal,
    c.isBackOffice,
    c.SignerID,
    c.isReviewed,
    c.Sent,
    c.ESignSendBy,
    c.ESignSendAt,
    c.ESignUpdatedAt,
    c.ESignUpdatedBy,
    c.ScheduledAppt,
    c.eSignInvitationExpiryDate,
    c.Passport,
    c.CloneID,
    c.isDisapproved,
    c.DisapprovedBy,
    c.DisapprovedAt,
    c.RejectedAt,
    c.RejectedBy,
    c.IsRejected,
    c.DisapprovalReason,
    c.RejectReason,
    c.SignNowInviteID,
    c.DeletedBy,
    c.UnDeletedBy,
    c.DeletedAt,
    c.UnDeletedAt,
    c.StripeAccountID,
    c.IsUploadByProvider,
    c.BatchID,
    c.BatchRemoveID,
    c.IsPaid,
    c.IsPaymentDate,
    c.PaymentReferenceID,
    c.I3ReferenceNumber,
    c.DonorPass,
    c.IsSensitive,
    c.IsRandom,
    c.SignedAttachments,
    c.IsDisqualified,
    c.AIReviewed,
    c.AINotes,
    c.AIRecommendation,
    c.DocumentReasonID,
    c.BETransactionHeaderID
    
FROM OperatorList ol
LEFT JOIN dbo.pay_Certifications c ON ol.OperatorID = c.OperatorId
ORDER BY 
    ol.StatusName,
    ol.OrderID,
    ol.LastName,
    ol.FirstName,
    c.Cert;

-- Summary counts
SELECT 
    'Total Operators' AS Metric,
    COUNT(DISTINCT o.ID) AS Count
FROM dbo.pay_Operators o
INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
LEFT JOIN dbo.pay_PizzaStatus ps ON st.PizzaStatusID = ps.ID
WHERE 
    ISNULL(o.isDeleted, 0) = 0
    AND ISNULL(st.isDeleted, 0) = 0
    AND ISNULL(st.Fleet, 0) = 0
    AND ISNULL(st.Providers, 0) = 0
    AND ISNULL(ps.IsOperator, 0) = 1

UNION ALL

SELECT 
    'Operators With Certifications',
    COUNT(DISTINCT c.OperatorId)
FROM dbo.pay_Certifications c
INNER JOIN dbo.pay_Operators o ON c.OperatorId = o.ID
INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
LEFT JOIN dbo.pay_PizzaStatus ps ON st.PizzaStatusID = ps.ID
WHERE 
    ISNULL(o.isDeleted, 0) = 0
    AND ISNULL(st.isDeleted, 0) = 0
    AND ISNULL(st.Fleet, 0) = 0
    AND ISNULL(st.Providers, 0) = 0
    AND ISNULL(ps.IsOperator, 0) = 1
    AND ISNULL(c.IsDeleted, 0) = 0

UNION ALL

SELECT 
    'Total Certifications',
    COUNT(*)
FROM dbo.pay_Certifications c
INNER JOIN dbo.pay_Operators o ON c.OperatorId = o.ID
INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.Id
LEFT JOIN dbo.pay_PizzaStatus ps ON st.PizzaStatusID = ps.ID
WHERE 
    ISNULL(o.isDeleted, 0) = 0
    AND ISNULL(st.isDeleted, 0) = 0
    AND ISNULL(st.Fleet, 0) = 0
    AND ISNULL(st.Providers, 0) = 0
    AND ISNULL(ps.IsOperator, 0) = 1
    AND ISNULL(c.IsDeleted, 0) = 0;
