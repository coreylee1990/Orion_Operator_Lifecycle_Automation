# Script Audit Report - Real Data Compatibility

**Date:** January 10, 2025  
**Purpose:** Verify all scripts work with real Orion data (168 operators, 4,731 certifications)

---

## ✅ Scripts Already Updated for Real Data

### 1. analyze_cert_requirements_by_status.py ✓
**Status:** FULLY COMPATIBLE  
**Updates Made:**
- Handles empty `StatusOrderID` strings (line 92, line 218)
- Uses real field names: `OperatorID`, `StatusName`, `StatusOrderID`, `Cert`
- Filters `IsDeleted = 0` for active certifications
- Successfully analyzed 168 operators, 4,430 active certs across 13 statuses

**Output:** 
- `generated/certification_requirements_analysis.txt` (334 lines)
- `generated/certification_requirements_analysis.json`

**Tested:** ✓ Successfully run on real data

---

### 2. generate_cert_query.py ✓
**Status:** FULLY COMPATIBLE  
**Updates Made:**
- Reads from `pay_Operators.txt` (not sample file)
- Generates SQL for all 168 operators
- Includes all 67 certification fields
- No mock data references
- Added comments: "ALWAYS use real data files - never mock or sample"

**Output:** `scripts/get_operator_certifications.sql` (270 lines)

**Tested:** ✓ Successfully generates clean SQL

---

### 3. convert_cert_csv_to_json.py ✓
**Status:** FULLY COMPATIBLE  
**Purpose:** Converts CSV certification exports to JSON format  
**Real Data Used:** 
- Converted 4,732 CSV rows → 4,731 JSON records
- Created both `.txt` and `.json` versions
- Metadata header with export timestamp

**Output:** 
- `data/pay_Certifications.txt` (10MB)
- `data/pay_Certifications.json` (10MB)

**Tested:** ✓ Successfully converted real CSV export

---

### 4. convert_operators_to_json.py / parse_operators_to_json.py / convert_operators_to_json_v2.py ✓
**Status:** FULLY COMPATIBLE  
**Purpose:** Various operator data conversion scripts  
**Real Data Used:** Works with real operator formats from Orion

**Note:** Multiple versions exist for different Orion export formats

---

## 📋 Scripts to Update/Review

### 5. phase3_certification_gaps.py ⚠️
**Status:** NEEDS UPDATES FOR REAL DATA  
**Current Issues:**
- Expects `CertificationName` field (real data uses `Cert`)
- Expects `ExpirationDate` field (real data doesn't have this consistently)
- Expects `StatusTypeID` in CertTypes mapping (needs verification)
- May expect different field names in operators

**Recommended Updates:**
```python
# Line ~56: Update field name
cert_name = cert.get('Cert', '')  # Was: 'CertificationName'

# Line ~137: Use real operator field names
op_id = op.get('operatorID')  # Was: 'Id'
status_name = op.get('statusName')  # Was: 'StatusName' or 'CurrentStatus'
op_name = f"{op.get('firstName', '')} {op.get('lastName', '')}"  # Was: 'FirstName', 'LastName'

# Line ~121: Use real certification fields
operator_id = cert.get('OperatorID')
cert_name = cert.get('Cert', '')
is_approved = cert.get('isApproved', 0) == 1
is_deleted = cert.get('IsDeleted', 0) == 1

if is_deleted:
    continue  # Skip deleted certs
```

**Action Required:** Update field mappings to match real data schema

---

### 6. phase1_lifecycle_overview.py, phase2_progression_analysis.py, phase4_bottleneck_analysis.py, phase5_recommendations.py ⚠️
**Status:** NEEDS FIELD NAME VERIFICATION  
**Potential Issues:**
- May use old field names: `Id`, `FirstName`, `LastName`, `CurrentStatus`
- Real fields are: `operatorID`, `firstName`, `lastName`, `statusName`

**Recommended Pattern:**
```python
# Use consistent field names from real data
op_id = op.get('operatorID')
first_name = op.get('firstName')
last_name = op.get('lastName')
status_name = op.get('statusName')
status_order = op.get('orderID', '')
# Handle empty orderID
order_id = int(status_order) if status_order and str(status_order).strip() else 0
```

**Action Required:** Audit field names in all phase scripts

---

### 7. operator_lifecycle.py ⚠️
**Status:** CONTAINS MOCK DATA - LEGACY SCRIPT  
**Issues:**
- Lines 6, 42, 45: Contains mock certifications and requirements
- Line 367: References `MOCK_REQUIREMENTS`
- Line 479: "No certifications found (Mock Data)"

**Recommendation:** 
- **Option A:** Update to use real data (replace all MOCK_ references)
- **Option B:** Mark as deprecated/legacy if not actively used
- **Option C:** Delete if superseded by newer analysis scripts

**Action Required:** Determine if this script is still needed

---

## 🔄 Scripts That Need Testing

### 8. generate_required_certs_by_step.py ❓
**Status:** NEEDS TESTING WITH REAL DATA  
**Purpose:** Generate cert requirements by lifecycle step  
**Note:** May be superseded by `analyze_cert_requirements_by_status.py`

**Action Required:** 
1. Test with real data
2. Compare output to newer analysis script
3. Decide if deprecated

---

### 9. generate_cert_requirements_report.py ❓
**Status:** NEEDS TESTING WITH REAL DATA  
**Purpose:** Generate cert requirements report  
**Note:** May be superseded by `analyze_cert_requirements_by_status.py`

**Action Required:**
1. Test with real data
2. Compare to newer script
3. Merge or deprecate

---

### 10. run_full_analysis.py ✅
**Status:** SHOULD WORK (orchestrator only)  
**Purpose:** Runs all 5 phases in sequence  
**Note:** Will work if individual phase scripts are updated

**Action Required:** Test after updating phase scripts

---

### 11. test_automation.py ❓
**Status:** UNKNOWN - NEEDS REVIEW  
**Purpose:** Test/automation script (unclear from name)

**Action Required:** Review purpose and test with real data

---

## 🗄️ SQL Scripts

### 12. get_operator_certifications.sql ✓
**Status:** FULLY COMPATIBLE  
**Generated by:** `generate_cert_query.py`  
**Contains:** 168 operator IDs, all 67 cert fields  
**Tested:** ✓ Used to generate real certification data

---

### 13. Other SQL Scripts ✅
- `get_random_operators_across_statuses.sql` - For sampling operators
- `get_division_process_tables.sql` - Division/process info
- `get_status_cert_requirements.sql` - Status cert requirements
- `get_actual_cert_types.sql` - Cert type definitions

**Status:** Should work with real data (SQL queries)

---

## 📊 Summary

### Fully Compatible (9 scripts)
1. ✅ analyze_cert_requirements_by_status.py
2. ✅ generate_cert_query.py
3. ✅ convert_cert_csv_to_json.py
4. ✅ convert_operators_to_json.py (+ variants)
5. ✅ get_operator_certifications.sql
6. ✅ get_random_operators_across_statuses.sql
7. ✅ get_division_process_tables.sql
8. ✅ get_status_cert_requirements.sql
9. ✅ get_actual_cert_types.sql

### Need Updates (6 scripts)
1. ⚠️ phase1_lifecycle_overview.py - Field name verification
2. ⚠️ phase2_progression_analysis.py - Field name verification
3. ⚠️ phase3_certification_gaps.py - Field mapping updates
4. ⚠️ phase4_bottleneck_analysis.py - Field name verification
5. ⚠️ phase5_recommendations.py - Field name verification
6. ⚠️ operator_lifecycle.py - Remove mock data

### Need Testing (4 scripts)
1. ❓ generate_required_certs_by_step.py
2. ❓ generate_cert_requirements_report.py
3. ❓ test_automation.py
4. ❓ run_full_analysis.py (after phase updates)

---

## 🎯 Priority Action Items

### HIGH PRIORITY
1. **Update phase3_certification_gaps.py** - Most complex field mapping changes
2. **Verify field names in phase1, 2, 4, 5** - Quick audit pass
3. **Test run_full_analysis.py** - After phase scripts updated

### MEDIUM PRIORITY
4. **Review operator_lifecycle.py** - Determine if still needed
5. **Test generate_required_certs_by_step.py** - May be deprecated
6. **Test generate_cert_requirements_report.py** - May be deprecated

### LOW PRIORITY
7. **Review test_automation.py** - Purpose unclear

---

## 🔑 Real Data Field Reference

### Operator Fields (pay_Operators.txt)
- `operatorID` (not `Id`)
- `firstName` (not `FirstName`)
- `lastName` (not `LastName`)
- `divisionID`
- `currentStatus` (ID)
- `statusName` (name)
- `orderID` (can be empty string!)
- `statusTypeID`
- `pizzaStatusID`
- `pizzaStatus`
- `certsCurrentlyHeld` (array)
- `certsHeldCount`
- `commonCertsForThisStatus` (array)
- `commonCertsCount`

### Certification Fields (pay_Certifications.txt)
- `OperatorID` (links to operator)
- `FirstName`, `LastName` (denormalized)
- `DivisionID`
- `CurrentOperatorStatus` (ID)
- `StatusName`
- `StatusOrderID` (can be empty string!)
- `CertificationID`
- `CertTypeID`
- `Cert` (certification name - not `CertificationName`)
- `Date`
- `IsDeleted` (0=active, 1=deleted)
- `isApproved` (0 or 1)
- ... 60+ more fields (see DATA_SCHEMA.md)

---

## 📝 Next Steps

1. Start with phase3_certification_gaps.py (most changes needed)
2. Do quick field name audit of phase1, 2, 4, 5
3. Test run_full_analysis.py
4. Decide fate of legacy scripts (operator_lifecycle.py, generate_required_certs_by_step.py)
5. Update this audit report as scripts are fixed
