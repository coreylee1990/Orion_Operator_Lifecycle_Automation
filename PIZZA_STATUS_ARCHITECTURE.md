# 🍕 Pizza Status Architecture - TRUE SYSTEM DESIGN

## 🎯 Critical Discovery

The Orion system uses **Pizza Statuses** as the mapping layer between operator lifecycle statuses and required certifications.

---

## 📊 Actual Data Architecture

### The Three-Layer System

```
OPERATOR → STATUS → PIZZA STATUS → REQUIRED CERTS
```

### Layer 1: Operator Status
**Table:** `pay_StatusTypes`

```sql
StatusTypeID  | Status        | Division | OrderID | PizzaStatusID
------------- | ------------- | -------- | ------- | -------------
ABC-123       | ONBOARDING    | 7 - MI   | 2       | PIZZA-001
DEF-456       | ONBOARDING    | 10 - OR  | 2       | PIZZA-002
GHI-789       | CREDENTIALING | 7 - MI   | 3       | PIZZA-003
```

**Key Points:**
- Each Status + Division combination has a unique StatusTypeID
- Each has an OrderID (workflow sequence)
- **Each links to a PizzaStatusID**

### Layer 2: Pizza Status
**Table:** `pay_PizzaStatuses`

```sql
PizzaStatusID | Status        | Description     | IsOperator
------------- | ------------- | --------------- | ----------
PIZZA-001     | Onboarding    | Initial docs    | 1
PIZZA-002     | Onboarding    | OR specific     | 1
PIZZA-003     | Credentialing | Safety checks   | 1
```

**Key Points:**
- Pizza Statuses are the **grouping mechanism**
- Same pizza status = same set of requirements
- Different divisions can map to different pizza statuses

### Layer 3: Status Requirements
**Table:** `pay_StatusRequirements`

```sql
StatusTypeID | CertTypeID  | IsRequired | ValidationOrder
------------ | ----------- | ---------- | ---------------
ABC-123      | CERT-001    | 1          | 1
ABC-123      | CERT-002    | 1          | 2
ABC-123      | CERT-003    | 1          | 3
```

**Key Points:**
- Links StatusTypeID → CertTypeID
- Defines which certs are required for each status
- ValidationOrder = sequence for checking

### Layer 4: Certification Types
**Table:** `pay_CertTypes`

```sql
CertTypeID  | Name              | Category  | ExpirationDays
----------- | ----------------- | --------- | --------------
CERT-001    | Driver License    | Identity  | 365
CERT-002    | W9                | Tax       | NULL
CERT-003    | Background Check  | Safety    | 730
```

---

## 🔄 How It Actually Works

### Determining Required Certs for an Operator

1. **Get Operator's Current Status**
   ```sql
   Operator: Willie Quainton
   Division: 10 - OR
   Status: ONBOARDING
   ```

2. **Find StatusTypeID**
   ```sql
   SELECT Id, PizzaStatusID 
   FROM pay_StatusTypes
   WHERE Status = 'ONBOARDING' 
     AND DivisionID = '10 - OR'
   
   Result: StatusTypeID = ABC-123, PizzaStatusID = PIZZA-001
   ```

3. **Get Required Cert Types**
   ```sql
   SELECT CT.Name
   FROM pay_StatusRequirements SR
   JOIN pay_CertTypes CT ON SR.CertTypeID = CT.Id
   WHERE SR.StatusTypeID = 'ABC-123'
     AND SR.IsRequired = 1
   ORDER BY SR.ValidationOrder
   
   Result:
   - Driver License
   - Social Security Card
   - W9
   - TriMet Background Release Form A&B
   ```

4. **Check Operator's Actual Certs**
   ```sql
   SELECT Cert
   FROM pay_Certifications
   WHERE OperatorID = 'Willie-123'
     AND IsDeleted = 0
     AND (IsExpired IS NULL OR IsExpired = 0)
   ```

5. **Calculate Gap**
   ```
   Required - Has = Missing
   ```

---

## 🎨 Why Pizza Status?

### Flexibility & Reusability

**Without Pizza Status (Our Old Approach):**
```
Status + Division → Hardcoded Cert List
Problem: 50 divisions × 10 statuses = 500 definitions
```

**With Pizza Status (Actual System):**
```
Status + Division → Pizza Status → Cert List
Benefit: Multiple status/div combos can share same pizza status
Result: ~16 pizza statuses cover all divisions
```

### Example:

```
ONBOARDING (7 - MI)  ────┐
ONBOARDING (8 - OH)  ────┼──→ Pizza: "Standard Onboarding" → [Driver License, SSN, W9]
ONBOARDING (11 - GA) ────┘

ONBOARDING (10 - OR) ────→ Pizza: "TriMet Onboarding" → [Driver License, SSN, W9, TriMet Forms]
ONBOARDING (5 - CA)  ────→ Pizza: "CA Onboarding" → [Driver License, SSN, W9, CA Background]
```

**Result:** Instead of defining requirements 50 times, define 3 pizza statuses and map statuses to them!

---

## ⚠️ What This Means for Our System

### Our OLD Approach (WRONG)
```
master_cert_requirements.json
└── global_requirements
    └── ONBOARDING
        ├── required_certs: [...]
        └── order: 2
└── division_overrides
    └── 10 - OR
        └── ONBOARDING
            └── add_required_certs: [...]
```

**Problem:** We were creating our own mapping system when one already exists in the database!

### CORRECT Approach (NEW)
```
1. Export pay_StatusRequirements → data/pay_StatusRequirements.json
2. Build mapping:
   - Status + Division → StatusTypeID
   - StatusTypeID → List of CertTypeIDs
   - CertTypeID → Cert Name
3. Use THIS as source of truth
4. HTML editor modifies StatusRequirements records
5. Generate SQL to UPDATE pay_StatusRequirements table
```

---

## 🔧 Required Changes

### 1. Data Export
**New SQL Query:**
```sql
-- See: sql/get_status_requirements_with_pizza.sql
-- Exports complete mapping: Status → Pizza → Certs
```

**New Data File:**
```
data/pay_StatusRequirements.json
```

### 2. Compliance Report Script
**Current:** Uses `config/master_cert_requirements.json`  
**Change To:** Uses `data/pay_StatusRequirements.json`

```python
# Load status requirements
with open('data/pay_StatusRequirements.json') as f:
    status_requirements = json.load(f)

# Build mapping: StatusTypeID → Required Certs
def get_required_certs(status, division):
    # Find StatusTypeID for this status+division
    status_type = find_status_type(status, division)
    
    # Get all cert requirements for this StatusTypeID
    required = [r for r in status_requirements 
                if r['StatusTypeID'] == status_type['Id']
                and r['IsRequired'] == 1]
    
    return [r['CertificationName'] for r in required]
```

### 3. HTML Editor
**Current:** Edits master_cert_requirements.json  
**Change To:** Edits StatusRequirements mapping

**New Features:**
- Show pizza status for each status+division
- Group statuses by pizza status (visual grouping)
- Edit requirements by pizza status (affects all statuses with that pizza)
- Or edit by specific status+division
- Generate SQL: INSERT/UPDATE/DELETE on pay_StatusRequirements

### 4. Save Function
**Current:** Downloads JSON file  
**Change To:** Generates SQL statements

```sql
-- When adding a cert to ONBOARDING (7 - MI):

INSERT INTO pay_StatusRequirements (
    Id,
    StatusTypeID,
    CertTypeID,
    IsRequired,
    ValidationOrder
) VALUES (
    NEWID(),
    'ABC-123',  -- StatusTypeID for ONBOARDING (7 - MI)
    'CERT-004', -- CertTypeID for new cert
    1,
    4  -- Next in sequence
);
```

---

## 📋 Migration Plan

### Phase 1: Export Real Data ✅
1. Run SQL query: `sql/get_status_requirements_with_pizza.sql`
2. Export to: `data/pay_StatusRequirements.json`
3. Verify data structure

### Phase 2: Update Compliance Script
1. Modify `scripts/reports/generate_compliance_gap_report.py`
2. Change data source from master_cert_requirements.json
3. Use pay_StatusRequirements.json
4. Update logic to use StatusTypeID → CertTypeID mapping
5. Test with known operators

### Phase 3: Document True Architecture
1. Create PIZZA_STATUS_ARCHITECTURE.md (this file)
2. Update README.md
3. Archive old master_cert_requirements.json approach
4. Update all technical docs

### Phase 4: Enhance HTML Editor (Future)
1. Add pizza status visualization
2. Group editing by pizza status
3. Show which statuses share same pizza status
4. Generate proper SQL for StatusRequirements table
5. Add validation against actual CertTypes table

---

## 🎯 Benefits of Correct Approach

### 1. **Data Accuracy**
- ✅ Uses actual database structure
- ✅ No manual maintenance of master file
- ✅ Changes reflected immediately

### 2. **Consistency**
- ✅ Same source of truth as production system
- ✅ No drift between our JSON and database
- ✅ SQL generation matches actual schema

### 3. **Flexibility**
- ✅ Pizza status grouping reduces duplication
- ✅ Easy to apply same requirements to multiple divisions
- ✅ Can override at status+division level if needed

### 4. **Maintainability**
- ✅ Follows existing system design
- ✅ Leverages built-in database relationships
- ✅ SQL changes are straightforward

---

## 🗂️ File Organization (Updated)

```
Orion_Operator_Lifecycle_Automation/
├── data/
│   ├── pay_Operators.json              # Operators with current status
│   ├── pay_Certifications.json         # What certs each operator has
│   ├── pay_StatusTypes.json            # Status definitions with PizzaStatusID
│   ├── pay_PizzaStatuses.json          # Pizza status definitions
│   ├── pay_CertTypes.json              # Certification type definitions
│   └── pay_StatusRequirements.json     # ⭐ NEW: Status → Required Certs mapping
├── sql/
│   └── get_status_requirements_with_pizza.sql  # ⭐ NEW: Export query
├── scripts/reports/
│   └── generate_compliance_gap_report.py       # ⚠️ NEEDS UPDATE
├── tools/
│   └── lifecycle-workflow-builder.html         # ⚠️ NEEDS UPDATE (Phase 4)
└── docs/
    └── PIZZA_STATUS_ARCHITECTURE.md            # ⭐ This file
```

---

## 🚦 Current Status

### ✅ Completed
- [x] Discovered pizza status architecture
- [x] Documented true system design
- [x] Created SQL export query
- [x] Identified required changes

### 🔄 In Progress
- [ ] Export pay_StatusRequirements data
- [ ] Update compliance report script
- [ ] Test with real data

### 📅 Future
- [ ] Update HTML editor for pizza status
- [ ] Add pizza status grouping visualization
- [ ] Generate SQL for StatusRequirements table
- [ ] Archive old master_cert_requirements.json approach

---

## 💡 Key Takeaways

1. **Pizza Status = Grouping Layer**
   - Reduces duplication
   - Allows requirements sharing across divisions
   - Built into original system design

2. **StatusRequirements Table = Source of Truth**
   - Don't create our own JSON mapping
   - Use what's in the database
   - Generate SQL to update database, not JSON files

3. **Our Old Approach Was Wrong**
   - We created master_cert_requirements.json thinking we needed it
   - The database already has pay_StatusRequirements
   - We should work WITH the system, not around it

4. **Path Forward is Clear**
   - Export StatusRequirements
   - Update compliance script
   - Eventually enhance editor
   - Stay aligned with database schema

---

## 📞 Questions?

**Q: Why did we miss this initially?**  
A: We didn't have visibility into the full database schema. We inferred structure from exported data rather than understanding the full relationship model.

**Q: Is our work wasted?**  
A: No! The HTML editor, compliance logic, and workflow concepts are still valid. We just need to connect to the right data source.

**Q: What about master_cert_requirements.json?**  
A: Archive it as `archive/master_cert_requirements_OLD_APPROACH.json`. Document as "learning artifact."

**Q: When do we update HTML editor?**  
A: Phase 4 (future). For now, focus on getting compliance reports accurate with real data.

---

**Last Updated:** January 13, 2026  
**Status:** Architecture Documented - Ready for Implementation
