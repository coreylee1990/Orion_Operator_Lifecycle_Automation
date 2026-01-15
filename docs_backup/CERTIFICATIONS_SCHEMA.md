# Certifications Schema Documentation

## Overview
The certification system tracks all certifications and credentials for operators throughout their lifecycle.

## Data Files
- **pay_Certifications.txt** - **2,838 certification records** (actual count from data)
- **pay_CertTypes.txt** - 802 certification type records (operator-specific data)

## Top Certification Types
1. Defensive Driving (108)
2. Social Security Card (106)
3. CTAA Passenger Assistance (101)
4. Orientation-Big Star Safety and Service (98)
5. Drivers License (94)
6. DOT Chain of Custody Form (87)
7. COMPLIANCE REVIEW (86)
8. BackgroundCheck (81)
9. Worker's Comp Coverage Waiver (79)
10. Motor Vehicle Report (MVR) (76)

## Tables

### pay_Certifications
Main table storing all operator certifications with tracking and approval workflow.

#### Schema Fields

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| **ID** | UNIQUEIDENTIFIER | Primary key for the certification record |
| **CertTypeID** | UNIQUEIDENTIFIER | Foreign key to certification type |
| **OperatorID** | UNIQUEIDENTIFIER | Foreign key to operator |
| **FleetID** | UNIQUEIDENTIFIER | Foreign key to fleet (nullable) |
| **Cert** | NVARCHAR | Certification name/title |
| **Date** | DATETIME | Original certification date |
| **Attachments** | NVARCHAR | Path or reference to attached documents |
| **IsDeleted** | BIT | Soft delete flag |
| **ProviderID** | UNIQUEIDENTIFIER | Third-party provider ID (nullable) |
| **isApproved** | BIT | Approval status flag |
| **ApprovedBy** | UNIQUEIDENTIFIER | User ID who approved |
| **Comments** | NVARCHAR | Additional notes or comments |
| **RecordAt** | DATETIME | Record creation timestamp |
| **RecordBy** | UNIQUEIDENTIFIER | User ID who created record |
| **UpdateAt** | DATETIME | Last update timestamp |
| **UpdateBy** | UNIQUEIDENTIFIER | User ID who last updated |
| **EsignStatus** | NVARCHAR | Electronic signature status |
| **DocumentID** | UNIQUEIDENTIFIER | Associated document ID |
| **FolderID** | UNIQUEIDENTIFIER | Document folder ID |
| **CompletionDate** | DATETIME | Date certification was completed |
| **ApprovedDate** | DATETIME | Date certification was approved |
| **SmsCount** | INT | Number of SMS notifications sent |
| **isMobile** | BIT | Created via mobile app |
| **isProviderPortal** | BIT | Created via provider portal |
| **isOperatorPortal** | BIT | Created via operator portal |
| **isBackOffice** | BIT | Created via back office system |
| **SignerID** | UNIQUEIDENTIFIER | ID of person who signed |
| **isReviewed** | BIT | Review status flag |
| **Sent** | DATETIME | Date notification was sent |
| **ESignSendBy** | UNIQUEIDENTIFIER | User who sent e-sign request |
| **ESignSendAt** | DATETIME | E-sign request sent timestamp |
| **ESignUpdatedAt** | DATETIME | E-sign last updated timestamp |
| **ESignUpdatedBy** | UNIQUEIDENTIFIER | User who updated e-sign |
| **ScheduledAppt** | DATETIME | Scheduled appointment date |
| **eSignInvitationExpiryDate** | DATETIME | E-sign invitation expiry |
| **Passport** | NVARCHAR | Passport information |
| **CloneID** | UNIQUEIDENTIFIER | Reference to cloned certification |
| **isDisapproved** | BIT | Disapproval flag |
| **DisapprovedBy** | UNIQUEIDENTIFIER | User who disapproved |
| **DisapprovedAt** | DATETIME | Disapproval timestamp |
| **RejectedAt** | DATETIME | Rejection timestamp |
| **RejectedBy** | UNIQUEIDENTIFIER | User who rejected |
| **IsRejected** | BIT | Rejection flag |
| **DisapprovalReason** | NVARCHAR | Reason for disapproval |
| **RejectReason** | NVARCHAR | Reason for rejection |
| **SignNowInviteID** | NVARCHAR | SignNow integration ID |
| **DeletedBy** | UNIQUEIDENTIFIER | User who deleted record |
| **UnDeletedBy** | UNIQUEIDENTIFIER | User who restored record |
| **DeletedAt** | DATETIME | Deletion timestamp |
| **UnDeletedAt** | DATETIME | Restoration timestamp |
| **StripeAccountID** | NVARCHAR | Stripe payment account ID |
| **IsUploadByProvider** | BIT | Uploaded by provider flag |
| **BatchID** | UNIQUEIDENTIFIER | Batch processing ID |
| **BatchRemoveID** | UNIQUEIDENTIFIER | Batch removal ID |
| **IsPaid** | BIT | Payment status flag |
| **IsPaymentDate** | DATETIME | Payment date |
| **PaymentReferenceID** | NVARCHAR | Payment reference number |
| **I3ReferenceNumber** | NVARCHAR | I3 system reference number |
| **DonorPass** | NVARCHAR | Donor pass information for drug testing |
| **IsSensitive** | BIT | Sensitive certification flag |
| **IsRandom** | BIT | Random testing flag |
| **SignedAttachments** | NVARCHAR | Path to signed attachment documents |
| **IsDisqualified** | BIT | Disqualification flag |
| **AIReviewed** | BIT | AI review completion flag |
| **AINotes** | NVARCHAR | AI-generated notes |
| **AIRecommendation** | NVARCHAR | AI recommendation |
| **DocumentReasonID** | UNIQUEIDENTIFIER | Document reason reference ID |
| **BETransactionHeaderID** | UNIQUEIDENTIFIER | Backend transaction header ID |

### pay_CertTypes
Appears to store operator-specific certification type information (based on current data structure).

#### Schema Fields

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| **Id** | UNIQUEIDENTIFIER | Primary key |
| **FirstName** | NVARCHAR | Operator first name |
| **LastName** | NVARCHAR | Operator last name |
| **DivisionID** | NVARCHAR | Division identifier |
| **StatusOrderSequence** | INT | Status order in workflow |
| **CurrentStatus** | NVARCHAR | Current operator status |

## Key Relationships

```
pay_Operators (OperatorID) ──< pay_Certifications
pay_Certifications >── pay_CertTypes (CertTypeID)
```

## Business Rules

1. **Approval Workflow**: Certifications go through approval process (isApproved, ApprovedBy, ApprovedDate)
2. **Rejection/Disapproval**: Separate tracks for rejection vs disapproval with reasons
3. **Soft Deletes**: Records use IsDeleted flag with audit trail (DeletedBy, DeletedAt)
4. **E-Signature Support**: Full e-signature workflow tracking
5. **Multi-Channel Creation**: Tracks source (mobile, provider portal, operator portal, back office)
6. **Payment Integration**: Stripe payment tracking for paid certifications
7. **Batch Processing**: Support for batch operations

## Data Quality Notes

- Many nullable fields indicate optional workflow steps
- Extensive audit trail fields for compliance
- Multiple date fields track different lifecycle events
- Integration fields for third-party systems (SignNow, Stripe, I3)

## Actual Data Statistics

**From Analysis Report:**
- **Total Active Certifications:** 2,610 (2,838 total with deleted)
- **Operators with Certifications:** 100 out of 168 (59.5%)
- **Operators without Certifications:** 68 (40.5%)

**Approval Status:**
- Approved: ~10% of active certifications
- Pending: ~90% of active certifications
- Very low rejection rate

**Submission Channels:**
- Unknown/Not Set: 81.5%
- Mobile App: 11.5%
- Provider Portal: 5.0%
- Back Office: 1.9%
- Operator Portal: 0.2%

**Average Certifications per Operator (with certs):**
- Range: 23-34 per operator depending on division
- Overall average: ~26 certifications per operator

**Division Coverage:**
- Only 5 divisions represented in current sample (11-GA, 12-PA, 2-IL, 6-FL, 7-MI)
- Division 11-GA: 27 certs/operator
- Division 6-FL: 34 certs/operator (highest)
