# AI Database Analysis Prompt

## Context
You are analyzing a SQL Server database for an operator lifecycle management system. The system tracks operators (drivers) as they progress through various certification and training stages.

## Database Schema Overview

### Core Tables

**pay_Operators** (81 records)
- `ID` (UNIQUEIDENTIFIER) - Primary key
- `FirstName`, `LastName` - Operator name
- `DivisionID` (NVARCHAR) - Format: "7 - MI", "10 - OR", "3 - TX", etc.
- `StatusID` (UNIQUEIDENTIFIER) - Foreign key to pay_StatusTypes
- `StatusName` (NVARCHAR) - Current status like "REGISTRATION", "CREDENTIALING", "IN-SERVICE"
- `isDeleted` (BIT) - Soft delete flag

**pay_Certifications** (4,430 records)
- `CertificationID` (UNIQUEIDENTIFIER) - Primary key
- `OperatorID` (UNIQUEIDENTIFIER) - Foreign key to pay_Operators
- `Cert` (NVARCHAR) - Certification name (e.g., "Background Check", "BACKGROUND CHECK", "Social Security Card")
- `Date` (DATETIME) - **Expiration date** (NOT issue date)
- `CompletionDate` (DATETIME) - **Issue/completion date**
- `isApproved` (BIT) - Approval status (0 = pending, 1 = approved)
- `IsDeleted` (BIT) - Soft delete flag

**pay_StatusTypes**
- `ID` (UNIQUEIDENTIFIER) - Primary key
- `StatusName` (NVARCHAR) - Status name
- `OrderID` (INT) - Sequential order in lifecycle

**pay_CertTypes**
- `ID` (UNIQUEIDENTIFIER) - Primary key
- `CertTypeName` (NVARCHAR) - Standardized cert type name

## Business Context

### Operator Lifecycle
Operators progress through these stages:
1. REGISTRATION
2. ONBOARDING
3. CREDENTIALING
4. REVIEW-CREDENTIALING
5. ORIENTATION-BIG STAR SAFETY & SERVICE
6. ORIENTATION-BEHIND THE WHEEL
7. APPROVED FOR BIG STAR SERVICE
8. COMPLIANCE REVIEW
9. SBPC APPROVED FOR SERVICE
10. APPROVED FOR CONTRACTING
11. IN-SERVICE

### Division-Specific Requirements
Different divisions (geographic/business units) have different certification requirements:
- Division 7 (MI - Michigan): Stricter requirements, uses ALL CAPS for some cert names
- Division 3 (TX - Texas): Fewer requirements
- Division 10 (OR - Oregon): Moderate requirements
- Division 12 (PA - Pennsylvania): Least strict

### Current Problem
**There is NO formal requirements standard in the database.** Requirements are currently INFERRED by analyzing:
- What certifications do operators at status X in division Y actually have?
- If >75% of operators have a cert, it's considered "required"
- If 50-75% have it, it's "common"
- If <50% have it, it's "optional"

## What We Need You to Analyze

### Primary Questions

1. **Consistency Analysis**
   - Are certification requirements consistent within each division?
   - Do operators at the same status/division have similar certifications?
   - What's the variance in cert counts for operators at same status/division?

2. **Certification Naming Issues**
   - How many variations exist for the same logical certification?
   - Examples: "Background Check" vs "BACKGROUND CHECK" vs "BackgroundCheck"
   - Which divisions use which naming conventions?

3. **Data Quality Issues**
   - Operators with certifications but no approval (isApproved = 0)
   - Certifications with missing/invalid dates
   - Expired certifications (Date < current date) for certs that shouldn't expire
   - Orphaned certifications (OperatorID not in pay_Operators)

4. **Requirements Pattern Discovery**
   - For each status + division combination:
     - What certs do >75% of operators have? (Required)
     - What certs do 50-75% have? (Common)
     - What certs do <50% have? (Optional)
   - Are there certs that are universal across all divisions?
   - Are there division-specific certs?

5. **Lifecycle Progression Logic**
   - Should requirements be cumulative? (Each status includes all previous certs?)
   - Or status-specific? (Each status has unique new certs?)
   - Current system uses cumulative - is this reflected in actual data?

6. **Certification Expiration Analysis**
   - Which cert types have expiration dates? (Date field populated)
   - Which cert types should NEVER expire? (Social Security Card, Driver's License, Badge Photo, W9)
   - Are expiration dates being properly enforced?

### Specific SQL Queries to Run

#### Query 1: Cert Count Variance by Status/Division
```sql
SELECT 
    st.StatusName,
    o.DivisionID,
    COUNT(DISTINCT o.ID) AS TotalOperators,
    MIN(cert_counts.CertCount) AS MinCerts,
    MAX(cert_counts.CertCount) AS MaxCerts,
    AVG(cert_counts.CertCount) AS AvgCerts,
    STDEV(cert_counts.CertCount) AS StdDevCerts
FROM dbo.pay_Operators o
INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.ID
LEFT JOIN (
    SELECT OperatorID, COUNT(*) AS CertCount
    FROM dbo.pay_Certifications
    WHERE IsDeleted = '0' AND isApproved = '1'
    GROUP BY OperatorID
) cert_counts ON o.ID = cert_counts.OperatorID
WHERE o.isDeleted = '0'
GROUP BY st.StatusName, o.DivisionID
HAVING COUNT(DISTINCT o.ID) >= 3  -- Only where we have enough data
ORDER BY st.OrderID, o.DivisionID;
```

#### Query 2: Certification Name Variations
```sql
SELECT 
    LOWER(LTRIM(RTRIM(REPLACE(Cert, '  ', ' ')))) AS NormalizedName,
    COUNT(DISTINCT Cert) AS Variations,
    STRING_AGG(Cert, ' | ') AS AllVariations,
    COUNT(*) AS TotalRecords
FROM dbo.pay_Certifications
WHERE IsDeleted = '0'
GROUP BY LOWER(LTRIM(RTRIM(REPLACE(Cert, '  ', ' '))))
HAVING COUNT(DISTINCT Cert) > 1
ORDER BY Variations DESC;
```

#### Query 3: Inferred Requirements by Status/Division
```sql
WITH OperatorCertCounts AS (
    SELECT 
        o.StatusID,
        st.StatusName,
        o.DivisionID,
        c.Cert,
        COUNT(DISTINCT o.ID) AS TotalOperators,
        COUNT(DISTINCT c.OperatorID) AS OperatorsWithCert
    FROM dbo.pay_Operators o
    INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.ID
    LEFT JOIN dbo.pay_Certifications c 
        ON o.ID = c.OperatorID 
        AND c.IsDeleted = '0' 
        AND c.isApproved = '1'
    WHERE o.isDeleted = '0'
    GROUP BY o.StatusID, st.StatusName, o.DivisionID, c.Cert
)
SELECT 
    StatusName,
    DivisionID,
    Cert,
    TotalOperators,
    OperatorsWithCert,
    CAST(OperatorsWithCert * 100.0 / TotalOperators AS DECIMAL(5,2)) AS Percentage,
    CASE 
        WHEN OperatorsWithCert * 100.0 / TotalOperators > 75 THEN 'Required'
        WHEN OperatorsWithCert * 100.0 / TotalOperators > 50 THEN 'Common'
        ELSE 'Optional'
    END AS RequirementLevel
FROM OperatorCertCounts
WHERE Cert IS NOT NULL
  AND TotalOperators >= 3  -- Minimum sample size
ORDER BY StatusName, DivisionID, Percentage DESC;
```

#### Query 4: Data Quality Issues
```sql
-- Missing/Invalid Dates
SELECT 'Missing Dates' AS Issue, COUNT(*) AS Count
FROM dbo.pay_Certifications
WHERE IsDeleted = '0' 
  AND (Date IS NULL OR CompletionDate IS NULL)

UNION ALL

-- Expired certifications for non-expiring types
SELECT 'Expired Non-Expiring Certs' AS Issue, COUNT(*) AS Count
FROM dbo.pay_Certifications
WHERE IsDeleted = '0'
  AND isApproved = '1'
  AND Date < GETDATE()
  AND Cert IN ('Social Security Card', 'SOCIAL SECURITY CARD', 'Badge Photo', 'W9', 'W-9')

UNION ALL

-- Unapproved certifications
SELECT 'Unapproved Certs' AS Issue, COUNT(*) AS Count
FROM dbo.pay_Certifications
WHERE IsDeleted = '0'
  AND isApproved = '0'

UNION ALL

-- Orphaned certifications
SELECT 'Orphaned Certs' AS Issue, COUNT(*) AS Count
FROM dbo.pay_Certifications c
LEFT JOIN dbo.pay_Operators o ON c.OperatorID = o.ID
WHERE c.IsDeleted = '0'
  AND o.ID IS NULL;
```

#### Query 5: Universal vs Division-Specific Certs
```sql
WITH CertByDivision AS (
    SELECT 
        c.Cert,
        o.DivisionID,
        COUNT(DISTINCT o.ID) AS OperatorCount
    FROM dbo.pay_Certifications c
    INNER JOIN dbo.pay_Operators o ON c.OperatorID = o.ID
    WHERE c.IsDeleted = '0' 
      AND c.isApproved = '1'
      AND o.isDeleted = '0'
    GROUP BY c.Cert, o.DivisionID
)
SELECT 
    Cert,
    COUNT(DISTINCT DivisionID) AS DivisionCount,
    SUM(OperatorCount) AS TotalOperators,
    CASE 
        WHEN COUNT(DISTINCT DivisionID) >= 6 THEN 'Universal'
        WHEN COUNT(DISTINCT DivisionID) >= 3 THEN 'Common'
        ELSE 'Division-Specific'
    END AS CertScope
FROM CertByDivision
GROUP BY Cert
ORDER BY DivisionCount DESC, TotalOperators DESC;
```

## Expected Output Format

### 1. Executive Summary
- Total operators, certifications, divisions analyzed
- Key findings (3-5 bullet points)
- Data quality score (1-10)
- Recommendation: Continue data-driven approach or implement formal requirements?

### 2. Consistency Analysis
- Table showing variance in cert counts by status/division
- Flag combinations with high variance (StdDev > 3)
- Identify outlier operators

### 3. Naming Issues Report
- List of cert names with variations
- Recommended canonical name for each
- SQL UPDATE statements to standardize

### 4. Requirements Matrix
- Table format:
  - Rows: Certification names (normalized)
  - Columns: Status + Division combinations
  - Values: Percentage of operators with cert + Required/Common/Optional label

### 5. Data Quality Report
- Count of each issue type
- Examples of problematic records (top 10 for each issue)
- Suggested SQL fixes

### 6. Recommendations
- Should requirements be formalized? (Yes/No with reasoning)
- Which SQL approach to use? (Options 1-4 from methodology doc)
- Priority fixes (ordered list)
- Estimated impact on operators

## Additional Context

### Known Issues Already Identified
1. **Division 7 (MI) ALL CAPS convention**: Intentional, not an error
   - "BACKGROUND CHECK" vs "Background Check"
   - "CTAA PASSENGER ASSISTANCE" vs "CTAA Passenger Assistance"
   - "SOCIAL SECURITY CARD" vs "Social Security Card"

2. **Date field confusion**: Recently fixed
   - `Date` = Expiration date (NOT issue date)
   - `CompletionDate` = Issue date (NOT expiration)
   - Non-expiring certs have far-future dates (2053, 2066, 2107)

3. **No formal requirements table**: Design choice, not oversight
   - Requirements are inferred from actual operator data
   - Reflects real business practices vs documented policy

### Questions to Answer
1. Is the >75% threshold appropriate for "required"?
2. Should cumulative requirements be enforced or just recommended?
3. Are there status transitions where operators lose certifications? (they shouldn't)
4. Should there be a grace period for expired certs?
5. What happens when an operator changes divisions? (do requirements change?)

## Deliverables Requested

1. **Analysis Report** (Markdown format)
   - All sections above filled in with query results
   - Visualizations (tables, percentages)
   - Clear recommendations

2. **SQL Script Package**
   - All queries above, tested and working
   - Data quality fix scripts
   - Requirements view/procedure (recommend which option)
   - Standardization UPDATE statements

3. **Requirements Matrix** (JSON format)
   - Structure matching current cert_requirements_by_status_division.json
   - Based on your analysis + recommendations
   - Includes confidence scores

4. **Migration Plan** (if recommending formal requirements)
   - Steps to implement chosen approach
   - Data migration scripts
   - Rollback procedures
   - Testing checklist

## Success Criteria

Your analysis is successful if it:
- ✅ Identifies all certification naming variations
- ✅ Provides clear requirements for each status/division combo
- ✅ Quantifies data quality issues with specific counts
- ✅ Recommends concrete next steps with implementation details
- ✅ Includes working SQL scripts that can be run immediately
- ✅ Explains WHY recommendations are made (not just WHAT)

## Getting Started

1. Connect to SQL Server database
2. Run schema inspection queries to confirm table structure
3. Execute the 5 analysis queries above
4. Review results and identify patterns
5. Generate recommendations based on data, not assumptions
6. Create SQL scripts for fixes and improvements
7. Write comprehensive analysis report

## Notes
- Focus on data-driven insights, not theoretical best practices
- Identify what IS happening, not what SHOULD happen
- Provide specific examples (operator names, cert IDs) when illustrating issues
- Calculate confidence levels based on sample sizes
- Consider division-specific business needs (state regulations, etc.)
