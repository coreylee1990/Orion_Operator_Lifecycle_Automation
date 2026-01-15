# 📊 Data Schema Documentation - Real Orion Database Structure

## Overview
This document describes the actual data structure from the Orion database. All field descriptions are based on **real data exports** (168 operators, 4,731 certification records).

---

## 📁 pay_Operators.txt/json

**Description:** Complete operator master records from Orion database

**Record Count:** 81 operators (filtered sample)  
**Format:** JSON array of operator objects  
**File Size:** ~227KB

### Fields (92 total)

#### Core Identity (13 fields)
| Field Name | Type | Description | Example Values |
|---|---|---|---|
| `ID` | GUID | Unique operator identifier (Primary Key) | "4DC7B88F-3402-456C-97D3-835958AC462D" |
| `FirstName` | String | Operator first name | "Courtney", "Mohamed" |
| `MiddleName` | String | Operator middle name | Usually empty |
| `LastName` | String | Operator last name | "Murray", "Noraldin" |
| `Email` | String | Operator email address | "ccmurray72@gmail.com" |
| `Mobile` | String | Operator phone number | "(971) 346-2133" |
| `Birthdate` | DateTime | Date of birth | "2024-09-25 00:00:00.000" |
| `Gender` | String | Gender identifier | "M", "F" |
| `ssan` | String | SSN/Tax ID (usually masked/empty) | Empty for privacy |
| `AspNetUserId` | GUID | ASP.NET identity user ID | Links to authentication |
| `Operator` | String | Legacy operator flag | Usually empty |
| `Suffix` | String | Name suffix | "Jr", "Sr", "III" |
| `ProfilePic` | String | Profile photo path | "orion-dipper-release/Profile/..." |

#### Address & Location (7 fields)
| Field | Type | Description |
|---|---|---|
| `Address1` | String | Primary address line |
| `Address2` | String | Secondary address line |
| `City` | String | City name |
| `State` | String | State code (2 letter) |
| `Zip` | String | ZIP/postal code |
| `DivisionID` | String | Division/branch location | "PA - BROOKES", "10 - OR" |
| `ClientID` | GUID | Client organization ID |

#### Status & Lifecycle (8 fields) **KEY FOR CERTIFICATION ANALYSIS**
| Field | Type | Description | **Connections** |
|---|---|---|---|
| `Status` | String | Legacy status field | Usually empty |
| `StatusID` | GUID | **Current lifecycle status ID** | **→ Links to pay_StatusTypes.Id** |
| `StatusName` | String | **Human-readable status** | "REGISTRATION", "IN-SERVICE" |
| `OrderID` | Integer/String | **Lifecycle order (1-14)** | **→ Defines progression sequence** |
| `StartDate` | DateTime | Operator start date | Usually empty |
| `TermDate` | DateTime | Termination date | Usually empty |
| `LastStatusDate` | DateTime | Last status change date | Timestamp |
| `Reason_One` | String | Status change reason | Usually empty |

#### Driver's License (8 fields)
| Field | Type | Description |
|---|---|---|
| `LicenseNbr` | String | Driver's license number |
| `LicenseState` | String | License issuing state |
| `LicenseExp` | DateTime | License expiration date |
| `LicenseIssueDate` | DateTime | License issue date |
| `LicensePhoto` | String | License photo path |
| `Class` | String | License class |
| `IsDLArtificial` | Boolean | AI-generated license flag |
| `Restrictions` | String | License restrictions |

#### Additional License Details (5 fields)
| Field | Type | Description |
|---|---|---|
| `Endorsements` | String | License endorsements |
| `Height` | String | Operator height |
| `EyeColor` | String | Eye color |
| `Veteran` | Boolean | Veteran status |
| `Branch` | String | Military branch |

#### System Tracking (11 fields)
| Field | Type | Description |
|---|---|---|
| `isDeleted` | Boolean | Soft delete flag (0=active, 1=deleted) |
| `DateCreated` | DateTime | Record creation timestamp |
| `RecordAt` | DateTime | Record timestamp |
| `RecordBy` | GUID | User who created record |
| `UpdateAt` | DateTime | Last update timestamp |
| `UpdateBy` | GUID | User who last updated |
| `LastContactDate` | DateTime | Last contact timestamp |
| `EmailVerified` | Boolean | Email verification status |
| `RegistrationSource` | String | How operator registered | "API-Mobile", "Web" |
| `IsMobile` | Boolean | Registered via mobile app |
| `FirebaseID` | String | Firebase authentication ID |

#### Integration IDs (10 fields)
| Field | Type | Description |
|---|---|---|
| `AirTableRecordID` | String | Airtable system ID |
| `AirTableSystemID` | String | Airtable system reference |
| `ProviderID` | GUID | Provider organization ID |
| `ProviderFlag` | String | Provider relationship flag |
| `TelematicsID` | String | Telematics device ID |
| `ClickSendID` | String | ClickSend SMS ID |
| `CandidateID` | String | Candidate tracking ID |
| `SVCandidateId` | String | SecondView candidate ID |
| `UberDriverId` | GUID | Uber driver ID |
| `UberEmail` | String | Uber account email |

#### Provider Promotion (5 fields)
| Field | Type | Description |
|---|---|---|
| `IsPromotedToProvider` | Boolean | Promoted to provider flag |
| `PromotedToProviderBy` | GUID | User who promoted |
| `PromotedToProviderAt` | DateTime | Promotion timestamp |
| `PromotedToProviderID` | GUID | Provider ID after promotion |
| `PromotedToProviderEmail` | String | Provider email |

#### Business & Insurance (8 fields)
| Field | Type | Description |
|---|---|---|
| `LeaseAmount` | Decimal | Vehicle lease amount |
| `InsuranceSent` | Boolean | Insurance docs sent |
| `InsuranceDate` | DateTime | Insurance effective date |
| `InsuranceReceived` | Boolean | Insurance received flag |
| `InsuranceReceivedDate` | DateTime | Insurance received date |
| `BusinessFormation` | String | Business entity type |
| `IsBusinessFormation` | Boolean | Has business entity |
| `BusinessFormationProviderID` | GUID | Business formation provider |

#### Onboarding Workflow (7 fields)
| Field | Type | Description |
|---|---|---|
| `isInterviewApproved` | Boolean | Interview approval status |
| `IsQuestionnaireSubmitted` | Boolean | Questionnaire submitted |
| `IsMeetingScheduled` | Boolean | Meeting scheduled flag |
| `isMoveForward` | Boolean | Move forward in process |
| `IsLandingPage` | Boolean | From landing page |
| `IsDeleteRequest` | Boolean | Delete request pending |
| `IsDeleteRequestBy` | String | Delete requested by |

#### Compensation & Payroll (3 fields)
| Field | Type | Description |
|---|---|---|
| `Rate` | Decimal | Pay rate |
| `IsPayroll` | Boolean | On payroll system |
| `UberMobile` | String | Uber mobile number |

#### Miscellaneous (7 fields)
| Field | Type | Description |
|---|---|---|
| `ReferralSource` | String | How operator found company |
| `SAPReferralForm` | String | SAP referral form reference |
| `GeneralAlertTime` | DateTime | Alert/notification time |
| `StatusDivisionRank` | Integer | Rank within status/division |
| `StatusTotal` | Integer | Total in this status |
| `TargetPerStatus` | Integer | Target count per status |

### Critical Connections for Certification Analysis

**Operator → Status:**
- `ID` (operator) → Used in pay_Certifications.OperatorID
- `StatusID` → Links to pay_StatusTypes.Id
- `StatusName` → Human-readable current status
- `OrderID` → Defines lifecycle progression (1-14)

**Status → Certifications:**
- Operators at each `StatusName` have certification patterns
- `OrderID` determines certification requirements by lifecycle stage
- Certification requirements analysis uses `StatusName` grouping
- Empty `OrderID` values must be handled (default to 0)

### Notes
- **Empty fields are common** - many fields contain empty strings
- **`OrderID` can be empty** - always handle: `int(orderID) if orderID and str(orderID).strip() else 0`
- **GUIDs are primary keys** - ID, StatusID, ClientID, ProviderID, etc.
- **DateTime fields** use SQL Server format: "YYYY-MM-DD HH:MM:SS.mmm"
- **Boolean fields** are typically "0", "1", or empty string
- **`StatusID` is the foreign key** to pay_StatusTypes, not `Status` field

---

## 📁 pay_Certifications.txt/json

**Description:** Complete certification records for all operators

**Record Count:** 4,731 certification records (4,430 after filtering IsDeleted=0)  
**Format:** JSON array with metadata header  
**File Size:** ~10MB

### Fields (75 total)

#### Operator Context (8 fields)
| Field | Type | Description | Notes |
|---|---|---|---|
| `OperatorID` | Integer | Links to operator | Foreign key to pay_Operators |
| `FirstName` | String | Operator first name | Denormalized from operators table |
| `LastName` | String | Operator last name | Denormalized from operators table |
| `DivisionID` | Integer | Operator's division | Division/location ID |
| `CurrentOperatorStatus` | Integer | Operator's current status ID | Links to StatusTypes |
| `StatusName` | String | Current status name | "ONBOARDING", "IN-SERVICE", etc. |
| `StatusOrderID` | Integer/String | Lifecycle order position | **Can be empty string!** |
| `StatusRequiresCerts` | Boolean | Whether status requires certs | 0 or 1 |

#### Certification Core (10 fields)
| Field | Type | Description | Critical |
|---|---|---|---|
| `CertificationID` | Integer | Unique cert record ID | Primary key |
| `CertTypeID` | Integer | Type of certification | FK to pay_CertTypes |
| `FleetID` | Integer | Fleet identifier | May be null |
| `Cert` | String | Certification name | **Key field** (e.g., "W9", "DOT Physical Card") |
| `Date` | DateTime | Certification date | ISO format |
| `Attachments` | String | File attachment references | Pipe-delimited |
| `IsDeleted` | Boolean | Soft delete flag | 0=active, 1=deleted |
| `ProviderID` | Integer | Provider who issued cert | May be null |
| `isApproved` | Boolean | Approval status | 0 or 1 |
| `ApprovedBy` | Integer | User who approved | User ID or null |

#### Approval & Review (8 fields)
| Field | Type | Description |
|---|---|---|
| `Comments` | String | Admin comments |
| `RecordAt` | DateTime | Record creation timestamp |
| `RecordBy` | Integer | User who created record |
| `UpdateAt` | DateTime | Last update timestamp |
| `UpdateBy` | Integer | User who last updated |
| `isReviewed` | Boolean | Review flag |
| `AIReviewed` | Boolean | AI review completed |
| `AINotes` | String | AI-generated notes |

#### Electronic Signature (11 fields)
| Field | Type | Description |
|---|---|---|
| `EsignStatus` | Integer | E-signature status code |
| `DocumentID` | String | Document identifier |
| `FolderID` | String | Folder/category ID |
| `SignerID` | Integer | Person who signed |
| `Sent` | Boolean | E-sign request sent |
| `ESignSendBy` | Integer | User who sent e-sign |
| `ESignSendAt` | DateTime | E-sign sent timestamp |
| `ESignUpdatedAt` | DateTime | E-sign update timestamp |
| `ESignUpdatedBy` | Integer | User who updated |
| `eSignInvitationExpiryDate` | DateTime | Invitation expiry |
| `SignNowInviteID` | String | SignNow system invite ID |

#### Dates & Scheduling (3 fields)
| Field | Type | Description |
|---|---|---|
| `CompletionDate` | DateTime | Cert completion date |
| `ApprovedDate` | DateTime | Approval date |
| `ScheduledAppt` | DateTime | Scheduled appointment |

#### Communication & Tracking (5 fields)
| Field | Type | Description |
|---|---|---|
| `SmsCount` | Integer | SMS notifications sent |
| `isMobile` | Boolean | Submitted via mobile |
| `isOperatorPortal` | Boolean | Submitted via operator portal |
| `isProviderPortal` | Boolean | Submitted via provider portal |
| `isBackOffice` | Boolean | Submitted via back office |

#### Special Cases (11 fields)
| Field | Type | Description |
|---|---|---|
| `Passport` | String | Passport reference |
| `CloneID` | Integer | Cloned from cert ID |
| `isDisapproved` | Boolean | Disapproval flag |
| `DisapprovedBy` | Integer | User who disapproved |
| `DisapprovedAt` | DateTime | Disapproval timestamp |
| `RejectedAt` | DateTime | Rejection timestamp |
| `RejectedBy` | Integer | User who rejected |
| `IsRejected` | Boolean | Rejection flag |
| `DisapprovalReason` | String | Reason for disapproval |
| `RejectReason` | String | Reason for rejection |
| `IsDisqualified` | Boolean | Disqualification flag |

#### Payment & Integration (8 fields)
| Field | Type | Description |
|---|---|---|
| `StripeAccountID` | String | Stripe payment account |
| `IsPaid` | Boolean | Payment received |
| `IsPaymentDate` | DateTime | Payment date |
| `PaymentReferenceID` | String | Payment reference |
| `I3ReferenceNumber` | String | I3 system reference |
| `BatchID` | Integer | Batch processing ID |
| `BatchRemoveID` | Integer | Batch removal ID |
| `IsUploadByProvider` | Boolean | Provider uploaded |

#### Deletion Management (4 fields)
| Field | Type | Description |
|---|---|---|
| `DeletedBy` | Integer | User who deleted |
| `UnDeletedBy` | Integer | User who restored |
| `DeletedAt` | DateTime | Deletion timestamp |
| `UnDeletedAt` | DateTime | Restoration timestamp |

#### Miscellaneous (7 fields)
| Field | Type | Description |
|---|---|---|
| `DonorPass` | String | Donor pass identifier |
| `IsSensitive` | Boolean | Contains sensitive data |
| `IsRandom` | Boolean | Random testing flag |
| `SignedAttachments` | String | Signed document references |
| `AIRecommendation` | String | AI system recommendation |
| `DocumentReasonID` | Integer | Document reason code |
| `BETransactionHeaderID` | Integer | Backend transaction header |

### Critical Implementation Notes

1. **Empty String Handling:** `StatusOrderID` can be empty string - always handle:
   ```python
   order_str = cert.get('StatusOrderID', '0')
   order_id = int(order_str) if order_str and order_str.strip() else 0
   ```

2. **Filtering:** Use `IsDeleted = 0` to get active certifications only

3. **Key Analysis Fields:**
   - `Cert` - certification name (100 unique types found)
   - `StatusName` - for grouping by lifecycle stage
   - `StatusOrderID` - for lifecycle ordering (handle empties!)
   - `isApproved` - filter by approval status

4. **Dates:** All DateTime fields are in ISO format, may be null

---

## 📁 pay_StatusTypes.txt/json

**Description:** Lifecycle status definitions

**Record Count:** Status type definitions (full schema)  
**Format:** JSON array  
**File Size:** ~783KB

### Key Fields
| Field | Description |
|---|---|
| `StatusTypeID` | Unique status identifier |
| `Status` | Status name |
| `OrderID` | Lifecycle order position |
| `RequiresCerts` | Whether certifications required |
| `Description` | Status description |

### Real Status Values Found
From actual data analysis:
- **REGISTRATION** (Order: 1)
- **ONBOARDING** (Order: 2)
- **CREDENTIALING** (Order: 3)
- **DOT SCREENING** (Order: 4)
- **ORIENTATION-BIG STAR SAFETY & SERVICE** (Order: 5)
- **APPROVED-ORIENTATION BTW** (Order: 7)
- **COMPLIANCE REVIEW** (Order: 8)
- **SBPC APPROVED FOR SERVICE** (Order: 9/10)
- **APPROVED FOR CONTRACTING** (Order: 11)
- **APPROVED FOR LEASING** (Order: 13)
- **IN-SERVICE** (Order: 14) ← Target state
- **OUT OF SERVICE** (Order: unknown)
- **TERMINATED** (Order: 19)

---

## 📁 pay_CertTypes.txt/json

**Description:** Certification type definitions and requirements

**Record Count:** Certification type metadata  
**Format:** JSON array  
**File Size:** ~24KB

### Key Fields
| Field | Description |
|---|---|
| `CertTypeID` | Unique cert type identifier |
| `CertTypeName` | Certification name |
| `RequiredForStatus` | Which status requires it |
| `ValidityPeriod` | How long cert is valid |
| `Description` | Cert description |

### Real Certification Types Found
100 unique certification types identified in actual data. Top 5 critical path:
1. **W9** - 80% adoption at DOT SCREENING (Order 4)
2. **DOT Drug & Alcohol Policy** - 80% at SBPC APPROVED FOR SERVICE (Order 10)
3. **DOT Pre-Contracting Drug/Alc Screen** - 80% at SBPC (Order 10)
4. **Vehicle Lease Agreement** - 100% at APPROVED FOR LEASING (Order 13)
5. **Social Security Card** - 83.3% at IN-SERVICE (Order 14)

See [certification_requirements_analysis.txt](generated/certification_requirements_analysis.txt) for complete list.

---

## 📁 pay_PizzaStatuses.txt/json

**Description:** Pizza workflow status definitions

**Record Count:** Pizza status workflow states  
**Format:** JSON array  
**File Size:** ~24KB

### Key Fields
| Field | Description |
|---|---|
| `PizzaStatusID` | Unique pizza status identifier |
| `PizzaStatus` | Pizza status name |
| `Description` | Status description |
| `WorkflowOrder` | Order in workflow |

---

## 🔍 Data Analysis Results

### Certification Requirements by Status
Based on real data patterns (4,731 records analyzed):

**Threshold Definitions:**
- **REQUIRED:** 80%+ of operators at this status have this cert
- **COMMON:** 50-79% of operators have this cert
- **OPTIONAL:** <50% of operators have this cert

**Critical Path Certifications (Early Lifecycle):**
1. W9 (Order 4, 80% adoption)
2. DOT Drug & Alcohol Policy (Order 10, 80%)
3. DOT Pre-Contracting Drug/Alc Screen (Order 10, 80%)
4. Vehicle Lease Agreement (Order 13, 100%)
5. Social Security Card (Order 14, 83.3%)

**Most Common Across All Statuses:**
- Social Security Card (appears in 10 of 13 statuses as required/common)
- Drivers License (appears in 9 statuses)
- W9 (appears in 8 statuses)
- DOT Drug & Alcohol Orientation (appears in 8 statuses)
- CTAA Passenger Assistance (appears in 8 statuses)

### Status Distribution (168 Operators)
- **IN-SERVICE:** 36 (21.4%) - Target state
- **ONBOARDING:** 31 (18.5%)
- **DOT SCREENING:** 25 (14.9%)
- **COMPLIANCE REVIEW:** 15 (8.9%)
- **CREDENTIALING:** 6 (3.6%)
- **Others:** 55 (32.7%) across 8 other statuses

---

## 🛠️ Using This Data

### Loading Data in Python
```python
import json
from pathlib import Path

# Load operators
with open('data/pay_Operators.txt', 'r') as f:
    operators = json.load(f)

# Load certifications
with open('data/pay_Certifications.txt', 'r') as f:
    certifications = json.load(f)

# Load status types
with open('data/pay_StatusTypes.txt', 'r') as f:
    status_types = json.load(f)
```

### Handling Empty StatusOrderID
```python
# ALWAYS use this pattern when working with StatusOrderID
def safe_order_id(value):
    """Safely convert StatusOrderID to int, handling empty strings"""
    if not value or not str(value).strip():
        return 0
    return int(value)

# Usage
order_id = safe_order_id(cert.get('StatusOrderID', '0'))
```

### Filtering Active Certifications
```python
# Get active (non-deleted) certifications only
active_certs = [c for c in certifications if c.get('IsDeleted', 0) == 0]
```

### Grouping by Status
```python
from collections import defaultdict

# Group certifications by status
certs_by_status = defaultdict(list)
for cert in certifications:
    if cert.get('IsDeleted', 0) == 0:
        status = cert.get('StatusName', 'Unknown')
        certs_by_status[status].append(cert)
```

---

## 📝 Notes

1. **Data Freshness:** Based on export from January 2025
2. **Empty Values:** Many fields can be null or empty strings - always validate
3. **StatusOrderID Issue:** This field commonly contains empty strings - see safe handling above
4. **File Formats:** All data exists in both .txt and .json formats (identical content)
5. **Analysis Tools:** Use `analyze_cert_requirements_by_status.py` for automated analysis

---

## 🔗 Related Documentation

- [README.md](README.md) - Main project overview
- [certification_requirements_analysis.txt](generated/certification_requirements_analysis.txt) - Full certification analysis
- [COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md) - Analysis findings
- [ANALYSIS_SUITE_README.md](ANALYSIS_SUITE_README.md) - Analysis tools guide
