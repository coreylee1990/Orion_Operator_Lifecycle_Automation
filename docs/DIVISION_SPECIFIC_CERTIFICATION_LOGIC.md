# ⚠️ CRITICAL: Division-Specific Certification Logic

## 🎯 Core Concept

**Certifications are DIVISION-SPECIFIC.** An operator in Division 7 (MI) has different certification requirements than an operator in Division 10 (OR), even if they are at the same status level.

---

## 📋 How Certification Filtering Works

### 1. **Data Structure**

```
cert_requirements_by_status_division.json
└── STATUS_NAME (e.g., "ORIENTATION-BIG STAR SAFETY & SERVICE")
    └── divisions
        ├── "7 - MI"
        │   ├── required: [list of required certs for MI]
        │   ├── common: [list of common certs for MI]
        │   └── optional: [list of optional certs for MI]
        ├── "10 - OR"
        │   ├── required: [list of required certs for OR]
        │   └── ...
        └── "12 - PA"
            └── ...
```

### 2. **Division ID Format**

**CRITICAL:** Division IDs are stored as a **FULL STRING** with spaces:
- ✅ Correct: `"7 - MI"`, `"10 - OR"`, `"12 - PA"`
- ❌ Wrong: `"7"`, `"10"`, `"12"` (number only)
- ❌ Wrong: `"7-MI"` (no spaces)

### 3. **Lookup Logic in HTML**

```javascript
// Get operator's FULL division ID
const opDivision = op.DivisionID || '';  // "7 - MI"

// Get requirements for THIS division only
Object.entries(certRequirements).forEach(([statusName, statusData]) => {
    const divisions = statusData.divisions || {};
    
    // CRITICAL: Use full division string as key
    if (opDivision && divisions[opDivision]) {
        // Get required certs for THIS specific division
        (divisions[opDivision].required || []).forEach(cert => {
            allCertsNeeded.add(cert.cert);
        });
    }
});
```

---

## 🔄 Data Flow

### **Step 1: Source Data**
- `data/pay_Operators.json` - 81 operators with basic info (NO certifications)
- `data/pay_Certifications.json` - 4,430 certification records with `OperatorID` foreign key

### **Step 2: Merge Process** (`scripts/merge_operators_with_certs.py`)

```python
# 1. Load certifications
certifications = load('pay_Certifications.json')['certifications']

# 2. Group by OperatorID
certs_by_operator = defaultdict(list)
for cert in certifications:
    operator_id = cert['OperatorID']
    certs_by_operator[operator_id].append({
        'CertType': cert['Cert'],           # Certification name
        'IssueDate': cert['Date'],          # Issue date
        'ExpireDate': cert['CompletionDate'], # Expiration date
        'Status': cert['isApproved'],       # Approval status (0 or 1)
        'CertificationID': cert['CertificationID']
    })

# 3. Merge into operators
for operator in operators:
    operator['certifications'] = certs_by_operator[operator['ID']]

# 4. Save to generated/pay_Operators.json
```

**Result:** `generated/pay_Operators.json` with embedded certifications
- 81 total operators
- 56 operators with certifications
- 25 operators without certifications
- 1,553 total certification records attached

### **Step 3: HTML Workflow Builder**

```javascript
// Load merged operator data with certifications embedded
operators = await fetch('pay_Operators.json').then(r => r.json());

// Load division-specific requirements
certRequirements = await fetch('cert_requirements_by_status_division.json').then(r => r.json());

// For each operator, filter requirements by their division
const opDivision = operator.DivisionID;  // "7 - MI"
const requiredCerts = certRequirements[statusName].divisions[opDivision].required;

// Match operator's certs against division-specific requirements
const cert = findMatchingCert(requiredCertName, operator.certifications);
```

---

## ⚠️ Critical Points

### 1. **NEVER Split Division ID**
```javascript
❌ WRONG:
const opDivision = (op.DivisionID || '').split(' ')[0];  // "7"
if (divisions[opDivision]) { ... }  // FAILS - key is "7 - MI", not "7"

✅ CORRECT:
const opDivision = op.DivisionID || '';  // "7 - MI"
if (divisions[opDivision]) { ... }  // WORKS - exact match
```

### 2. **Case-Insensitive Matching Required**

Division 7 (MI) uses ALL CAPS for some certifications:
- `"BACKGROUND CHECK"` (MI)
- `"Background Check"` (other divisions)

**Solution:** Normalization function
```javascript
function normalizeCertName(name) {
    return name.toLowerCase().trim().replace(/\s+/g, ' ');
}

function certNamesMatch(cert1, cert2) {
    return normalizeCertName(cert1) === normalizeCertName(cert2);
}
```

### 3. **Data Refresh Process**

When certification data changes in the database:

```bash
# 1. Export fresh data from SQL Server
# Run SQL queries to export to JSON files

# 2. Merge operators with certifications
cd /path/to/project
python3 scripts/merge_operators_with_certs.py

# 3. Refresh browser (hard refresh to clear cache)
# Ctrl+Shift+R or Ctrl+F5
```

---

## 📊 Example: Willie Quainton (Division 7 - MI)

### Operator Data:
```json
{
  "ID": "E98ECB6B-C801-4FD2-BB42-F2EB942C7FF3",
  "FirstName": "Willie",
  "LastName": "Quainton",
  "DivisionID": "7 - MI",
  "StatusName": "ORIENTATION-BIG STAR SAFETY & SERVICE",
  "certifications": [
    {
      "CertType": "BACKGROUND CHECK",
      "IssueDate": "2027-01-06 00:00:00.000",
      "ExpireDate": "2026-01-06 00:00:00.000",
      "Status": "1",
      "CertificationID": "7DE235BA-8C78-42BC-B45A-301DD707D2C0"
    },
    {
      "CertType": "CTAA PASSENGER ASSISTANCE",
      "IssueDate": "",
      "ExpireDate": "",
      "Status": "0",
      "CertificationID": "623E6EAC-5940-4110-B9CA-4C21D36165E6"
    }
    // ... 25 more certs
  ]
}
```

### Requirements for Division 7 - MI:
```json
{
  "ORIENTATION-BIG STAR SAFETY & SERVICE": {
    "divisions": {
      "7 - MI": {
        "required": [
          {"cert": "BACKGROUND CHECK"},
          {"cert": "CTAA PASSENGER ASSISTANCE"},
          {"cert": "SOCIAL SECURITY CARD"}
          // ... more
        ]
      }
    }
  }
}
```

### Matching Process:
1. Get Willie's division: `"7 - MI"`
2. Get Willie's status: `"ORIENTATION-BIG STAR SAFETY & SERVICE"`
3. Look up: `certRequirements["ORIENTATION-BIG STAR SAFETY & SERVICE"].divisions["7 - MI"].required`
4. For each required cert, check if Willie has it (using normalized matching)
5. Calculate: valid, expired, missing counts

---

## 🔧 SQL Query Reference

**File:** `sql_queries/get_operator_certifications_by_division.sql`

**Key Query:**
```sql
SELECT 
    o.ID AS OperatorID,
    o.FirstName,
    o.LastName,
    o.DivisionID,        -- "7 - MI" format
    o.StatusName,
    c.Cert AS CertType,  -- Certification name
    c.isApproved AS Status
FROM dbo.pay_Operators AS o
LEFT JOIN dbo.pay_Certifications AS c 
    ON o.ID = c.OperatorID
    AND c.IsDeleted = '0'
WHERE 
    o.isDeleted = '0'
ORDER BY 
    o.DivisionID,
    o.StatusName;
```

---

## 🎓 Why This Matters

### Problem Without Division Filtering:
- Operator in Division 7 (MI) shows requirements for ALL divisions
- Progress bar shows 100% needed certifications (all divisions combined)
- Operator appears to need hundreds of certs when they only need 15-20

### Solution With Division Filtering:
- Operator in Division 7 (MI) only sees MI requirements
- Progress bar shows accurate percentage for their division
- Operator sees correct certification gap analysis

### Example Impact:
```
WITHOUT DIVISION FILTER:
- Requirements checked: 150 certs (all divisions)
- Willie has: 27 certs
- Progress: 18% (27/150)

WITH DIVISION FILTER:
- Requirements checked: 22 certs (Division 7 only)
- Willie has: 18 matching
- Progress: 82% (18/22) ✅
```

---

## 📝 Maintenance Notes

### When to Regenerate Data:
1. New operators added to database
2. Certifications updated in database
3. Operator changes division
4. Certification requirements change

### How to Regenerate:
```bash
# Run merge script
python3 scripts/merge_operators_with_certs.py

# Output: generated/pay_Operators.json updated
# Result: 81 operators, 56 with certs, 1553 total cert records
```

### How to Verify:
```bash
# Check operator cert count
curl -s http://127.0.0.1:8083/pay_Operators.json | \
  python3 -c "import sys,json; data=json.load(sys.stdin); \
  print(f'Operators: {len(data)}'); \
  print(f'With certs: {sum(1 for op in data if op.get(\"certifications\"))}')"
```

---

## 🚨 Common Issues & Solutions

### Issue 1: All operators show 0 certifications
**Cause:** `generated/pay_Operators.json` is stale or missing certifications
**Solution:** Run `python3 scripts/merge_operators_with_certs.py`

### Issue 2: Division lookup fails (divisions[opDivision] is undefined)
**Cause:** Division ID being split incorrectly
**Solution:** Use full division string: `const opDivision = op.DivisionID;`

### Issue 3: Certifications don't match (has cert but shows missing)
**Cause:** Case/spacing differences in cert names
**Solution:** Use normalized matching with `certNamesMatch()` function

### Issue 4: Browser shows old data
**Cause:** Browser cache
**Solution:** Hard refresh (Ctrl+Shift+R) or add cache buster parameter

---

**Last Updated:** January 12, 2026  
**Critical for:** Operator lifecycle workflow, certification tracking, division-specific requirements
