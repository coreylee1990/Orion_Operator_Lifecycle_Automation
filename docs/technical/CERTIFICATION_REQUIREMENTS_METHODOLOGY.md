# Certification Requirements Methodology

## 🎯 Core Question: How Are Required Certifications Determined?

**Answer:** Certification requirements are **inferred from actual operator data** in the database, not from predefined business rules or procedures.

---

## 📊 Data-Driven Requirements Discovery

### Current Methodology

The system analyzes **which certifications operators actually have** at each status level and division, then infers that those certifications are "required" for that status/division combination.

#### Process Flow:

```
Database (pay_Operators + pay_Certifications)
    ↓
analyze_cert_requirements_by_status_division.py
    ↓
Analyzes: "What certs do operators at status X in division Y have?"
    ↓
Infers: "Those certs must be required for status X in division Y"
    ↓
Output: cert_requirements_by_status_division.json
```

### Analysis Script Logic

**File:** `scripts/analyze_cert_requirements_by_status_division.py`

```python
# For each status and division combination:
# 1. Find all operators at that status in that division
# 2. Count how many have each certification type
# 3. Calculate percentage: (operators_with_cert / total_operators) * 100
# 4. Classify as:
#    - Required: >75% have it
#    - Common: 50-75% have it
#    - Optional: <50% have it
```

**Example Output Structure:**
```json
{
  "CREDENTIALING": {
    "divisions": {
      "7 - MI": {
        "required": [
          {"cert": "BACKGROUND CHECK", "count": 5, "total": 6, "percentage": 83.3},
          {"cert": "Social Security Card", "count": 6, "total": 6, "percentage": 100.0}
        ]
      },
      "3 - TX": {
        "required": [
          {"cert": "Background Check", "count": 3, "total": 4, "percentage": 75.0}
        ]
      }
    }
  }
}
```

---

## 🔍 Real Example Analysis

### Mildred Flowers vs Christopher Adams

Both at **CREDENTIALING** status, but different certification counts:

| Operator | Division | Cumulative Required | Why Different? |
|----------|----------|---------------------|----------------|
| Mildred Flowers | 3 - TX | 6 certs | Texas operators typically have fewer requirements |
| Christopher Adams | 7 - MI | 12 certs | Michigan has more strict requirements and uses ALL CAPS naming |

### Breakdown by Status (Cumulative)

**Division 3 - TX:**
```
REGISTRATION:      2 certs
ONBOARDING:        +0 certs (same as REGISTRATION)
CREDENTIALING:     +4 certs (6 total cumulative)
```

**Division 7 - MI:**
```
REGISTRATION:      4 certs
ONBOARDING:        +2 certs (6 total)
CREDENTIALING:     +6 certs (12 total cumulative)
```

### Why Division 7 (MI) Has More Requirements

From database analysis, Michigan operators have:
- Stricter certification standards
- More background check variations
- Additional local/state requirements
- Different naming conventions (ALL CAPS)

---

## 🔄 How Requirements Are Applied in HTML

### Cumulative Logic

The workflow builder uses **cumulative requirements**:

```javascript
// Find operator's current step
const currentStepIndex = idealFlow.findIndex(s => s.status === opStatus);

// Get ALL statuses up to and including current
const relevantStatuses = idealFlow.slice(0, currentStepIndex + 1);

// Accumulate requirements from all those statuses
relevantStatuses.forEach(statusName => {
    const statusData = certRequirements[statusName];
    const divisions = statusData.divisions || {};
    
    // Only get requirements for operator's specific division
    if (opDivision && divisions[opDivision]) {
        divisions[opDivision].required.forEach(cert => {
            allCertsNeeded.add(cert.cert);
        });
    }
});
```

### Example: Operator at IN-SERVICE

An operator at IN-SERVICE needs **all certs from**:
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

Total requirements = sum of unique certs from all these statuses (for their specific division).

---

## 📋 Current Standard vs Actual Practice

### Current State: **NO FORMAL STANDARD**

Requirements are **discovered**, not **defined**. This means:

#### ✅ Advantages:
- Reflects actual business practices
- Automatically adapts to division-specific needs
- No need to maintain separate requirements documentation
- Shows real-world compliance patterns

#### ⚠️ Disadvantages:
- No single source of truth for "what SHOULD be required"
- Requirements can vary based on data quality
- Missing certifications might not be caught if no operators at that level have them
- Inconsistent enforcement across divisions

### What the Data Shows:

**Example: CREDENTIALING status**

| Division | Required Certs | Pattern |
|----------|----------------|---------|
| 3 - TX | 6 | More lenient, fewer requirements |
| 7 - MI | 11 | Stricter, more comprehensive |
| 11 - GA | 7 | Moderate requirements |
| 12 - PA | 4 | Least strict at this stage |

These differences arise from:
1. **State/Local Regulations**: Michigan may have stricter state requirements
2. **Business Unit Practices**: Different divisions enforce different standards
3. **Historical Patterns**: How certifications were historically collected
4. **Data Quality**: Some divisions may have incomplete certification records

---

## 🔧 Improvement Options

### Option 1: Formalize Requirements (Define Standard)

**Create a master requirements table:**

```sql
CREATE TABLE dbo.pay_CertificationRequirements (
    RequirementID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    StatusID UNIQUEIDENTIFIER NOT NULL, -- Links to pay_StatusTypes
    DivisionID NVARCHAR(50) NOT NULL,   -- "7 - MI", etc.
    CertTypeID UNIQUEIDENTIFIER NOT NULL, -- Links to pay_CertTypes
    IsRequired BIT NOT NULL DEFAULT 1,   -- vs Optional
    DisplayOrder INT,
    EffectiveDate DATETIME,
    CreatedBy UNIQUEIDENTIFIER,
    CreatedAt DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (StatusID) REFERENCES dbo.pay_StatusTypes(ID),
    FOREIGN KEY (CertTypeID) REFERENCES dbo.pay_CertTypes(ID)
);
```

**Benefits:**
- Single source of truth
- Can be edited without changing operator data
- Audit trail of changes
- Consistent enforcement

**Drawbacks:**
- Requires initial data population
- Needs maintenance when requirements change
- Must handle exceptions

### Option 2: Create Requirements View (Current + Overrides)

**Hybrid approach:** Use current data-driven method, but allow overrides

```sql
CREATE VIEW dbo.vw_CertificationRequirements AS
SELECT 
    s.StatusName,
    o.DivisionID,
    ct.CertTypeName,
    -- Use override if exists, otherwise use inferred
    COALESCE(cr.IsRequired, 
             CASE WHEN COUNT(c.CertificationID) * 1.0 / COUNT(DISTINCT o.ID) > 0.75 
                  THEN 1 ELSE 0 END) AS IsRequired,
    COUNT(DISTINCT o.ID) AS TotalOperators,
    COUNT(c.CertificationID) AS OperatorsWithCert,
    CAST(COUNT(c.CertificationID) * 100.0 / COUNT(DISTINCT o.ID) AS DECIMAL(5,2)) AS Percentage
FROM dbo.pay_Operators o
CROSS JOIN dbo.pay_CertTypes ct
LEFT JOIN dbo.pay_Certifications c 
    ON o.ID = c.OperatorID 
    AND ct.CertTypeName = c.Cert
LEFT JOIN dbo.pay_StatusTypes s 
    ON o.StatusID = s.ID
LEFT JOIN dbo.pay_CertificationRequirements cr 
    ON s.ID = cr.StatusID 
    AND o.DivisionID = cr.DivisionID 
    AND ct.ID = cr.CertTypeID
WHERE o.isDeleted = '0'
GROUP BY s.StatusName, o.DivisionID, ct.CertTypeName, cr.IsRequired;
```

**Benefits:**
- Keeps current data-driven approach
- Allows manual overrides where needed
- Shows both actual and intended requirements
- Gradual transition path

### Option 3: Stored Procedure for Dynamic Requirements

**Create procedure to get requirements with business logic:**

```sql
CREATE PROCEDURE dbo.sp_GetCertificationRequirements
    @StatusName NVARCHAR(255),
    @DivisionID NVARCHAR(50),
    @IncludeCumulative BIT = 1
AS
BEGIN
    -- Get status order
    DECLARE @StatusOrder INT;
    SELECT @StatusOrder = OrderID 
    FROM dbo.pay_StatusTypes 
    WHERE StatusName = @StatusName;
    
    -- Get all statuses up to current (if cumulative)
    WITH StatusHierarchy AS (
        SELECT ID, StatusName, OrderID
        FROM dbo.pay_StatusTypes
        WHERE (@IncludeCumulative = 0 AND StatusName = @StatusName)
           OR (@IncludeCumulative = 1 AND OrderID <= @StatusOrder)
    ),
    CertCounts AS (
        SELECT 
            c.Cert AS CertTypeName,
            COUNT(DISTINCT c.OperatorID) AS OperatorCount,
            COUNT(DISTINCT o.ID) AS TotalOperators
        FROM dbo.pay_Operators o
        INNER JOIN StatusHierarchy sh ON o.StatusID = sh.ID
        LEFT JOIN dbo.pay_Certifications c ON o.ID = c.OperatorID
        WHERE o.DivisionID = @DivisionID
          AND o.isDeleted = '0'
        GROUP BY c.Cert
    )
    SELECT 
        CertTypeName,
        OperatorCount,
        TotalOperators,
        CAST(OperatorCount * 100.0 / NULLIF(TotalOperators, 0) AS DECIMAL(5,2)) AS Percentage,
        CASE 
            WHEN CAST(OperatorCount * 100.0 / NULLIF(TotalOperators, 0) AS DECIMAL(5,2)) > 75 THEN 'Required'
            WHEN CAST(OperatorCount * 100.0 / NULLIF(TotalOperators, 0) AS DECIMAL(5,2)) > 50 THEN 'Common'
            ELSE 'Optional'
        END AS RequirementLevel
    FROM CertCounts
    ORDER BY Percentage DESC;
END;
```

**Benefits:**
- Encapsulates business logic
- Easy to modify thresholds
- Can add complex rules (state-specific, date-based, etc.)
- Consistent across applications

### Option 4: Requirements Configuration Table

**Lightweight approach:** Simple config table for overrides

```sql
CREATE TABLE dbo.pay_CertificationRules (
    RuleID INT IDENTITY(1,1) PRIMARY KEY,
    DivisionID NVARCHAR(50),
    StatusName NVARCHAR(255),
    CertTypeName NVARCHAR(255),
    MinPercentageRequired DECIMAL(5,2) DEFAULT 75.0,
    IsActive BIT DEFAULT 1,
    Notes NVARCHAR(MAX),
    UpdatedBy UNIQUEIDENTIFIER,
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- Example: Lower threshold for certain divisions
INSERT INTO dbo.pay_CertificationRules (DivisionID, StatusName, CertTypeName, MinPercentageRequired)
VALUES ('12 - PA', 'CREDENTIALING', 'Background Check', 60.0);
```

---

## 🎓 Recommendations

### Immediate Term (Current System)
1. **Document Current State**: Continue using data-driven approach
2. **Add Validation**: Create alerts when requirements drop below threshold
3. **Monitor Trends**: Track requirement changes over time
4. **Fix Data Issues**: Clean up certification naming inconsistencies

### Short Term (3-6 months)
1. **Implement Option 2**: Create requirements view with overrides
2. **Add Audit Logging**: Track when operators meet/miss requirements
3. **Create Reports**: Division-by-division compliance reports
4. **Standardize Naming**: Ensure consistent certification names

### Long Term (6-12 months)
1. **Implement Option 1**: Formal requirements table
2. **Build Admin UI**: Allow managers to set/update requirements
3. **Automated Compliance**: Flag operators missing required certs
4. **Integration**: Connect to HR/onboarding systems

---

## 📊 Query Examples for Analysis

### Find Divisions with Inconsistent Requirements

```sql
-- Compare same status across divisions
SELECT 
    st.StatusName,
    o.DivisionID,
    c.Cert,
    COUNT(DISTINCT o.ID) AS TotalOps,
    COUNT(c.CertificationID) AS OpsWithCert,
    CAST(COUNT(c.CertificationID) * 100.0 / COUNT(DISTINCT o.ID) AS DECIMAL(5,2)) AS Percentage
FROM dbo.pay_Operators o
LEFT JOIN dbo.pay_StatusTypes st ON o.StatusID = st.ID
LEFT JOIN dbo.pay_Certifications c ON o.ID = c.OperatorID
WHERE o.isDeleted = '0'
  AND st.StatusName = 'CREDENTIALING'
GROUP BY st.StatusName, o.DivisionID, c.Cert
HAVING COUNT(DISTINCT o.ID) > 3  -- Only divisions with enough operators
ORDER BY c.Cert, o.DivisionID;
```

### Identify Certification Gaps

```sql
-- Find operators missing commonly required certs
WITH RequiredCerts AS (
    SELECT 
        StatusID,
        DivisionID,
        Cert,
        COUNT(*) AS RequiredCount
    FROM (
        SELECT 
            o.StatusID,
            o.DivisionID,
            c.Cert,
            COUNT(DISTINCT o.ID) AS Total
        FROM dbo.pay_Operators o
        LEFT JOIN dbo.pay_Certifications c ON o.ID = c.OperatorID
        WHERE o.isDeleted = '0'
        GROUP BY o.StatusID, o.DivisionID, c.Cert
        HAVING COUNT(c.CertificationID) * 1.0 / COUNT(DISTINCT o.ID) > 0.75
    ) x
    GROUP BY StatusID, DivisionID, Cert
)
SELECT 
    o.ID,
    o.FirstName,
    o.LastName,
    o.DivisionID,
    st.StatusName,
    rc.Cert AS MissingCert
FROM dbo.pay_Operators o
INNER JOIN RequiredCerts rc 
    ON o.StatusID = rc.StatusID 
    AND o.DivisionID = rc.DivisionID
INNER JOIN dbo.pay_StatusTypes st ON o.StatusID = st.ID
LEFT JOIN dbo.pay_Certifications c 
    ON o.ID = c.OperatorID 
    AND rc.Cert = c.Cert
WHERE c.CertificationID IS NULL
  AND o.isDeleted = '0'
ORDER BY o.DivisionID, st.StatusName, o.LastName;
```

### Track Requirement Changes Over Time

```sql
-- See how requirements have changed (if tracking snapshots)
SELECT 
    SnapshotDate,
    StatusName,
    DivisionID,
    COUNT(DISTINCT CertTypeName) AS RequiredCertCount
FROM dbo.pay_RequirementsHistory  -- Would need to create this
WHERE RequirementLevel = 'Required'
GROUP BY SnapshotDate, StatusName, DivisionID
ORDER BY StatusName, DivisionID, SnapshotDate;
```

---

## ✅ Current Best Practices

Until formal requirements are implemented:

1. **Run Analysis Weekly**: Regenerate requirements to catch changes
2. **Review Anomalies**: Check for sudden requirement changes
3. **Document Decisions**: Record why certain certs are required
4. **Validate Data**: Ensure operators at same status/division have consistent certs
5. **Fix Naming**: Standardize certification names (see CERTIFICATION_STANDARDIZATION_COMPLETE_SOLUTION.md)

---

**Last Updated:** January 12, 2026  
**Status:** Data-driven approach (no formal requirements standard)  
**Next Steps:** Evaluate Options 1-4 for implementing formal requirements
