# Certification Naming Discrepancies Report

**Generated**: January 12, 2026  
**Purpose**: Document all certification naming inconsistencies across divisions and statuses  
**Source**: cert_requirements_by_status_division.json

---

## Executive Summary

This document catalogs all certification types that have multiple name variations across different divisions and statuses. These inconsistencies cause:
- False mismatches in operator certification validation
- Duplicate cert requirements appearing in different formats
- Confusion in automated matching systems

**Total Certification Types with Variations**: 8  
**Affected Divisions**: 9 (all divisions)  
**Affected Statuses**: 13 (all statuses)

---

## Detailed Naming Discrepancies

### 1. CTAA Passenger Assistance

**Variations Found**: 2
- `CTAA PASSENGER ASSISTANCE` (ALL CAPS)
- `CTAA Passenger Assistance` (Title Case)

**Distribution**:
- Found in: 8 divisions
- Found in: 12 statuses
- Divisions: 2 - IL, 3 - TX, 5 - CA, 6 - FL, 7 - MI, 8 - OH, 10 - OR, 11 - GA, 12 - PA

**Impact**: Medium
- Different capitalization may cause matching failures
- Both formats appear in operator certification records

**Recommended Fix**: Standardize to `CTAA Passenger Assistance` (Title Case)

---

### 2. Defensive Driving

**Variations Found**: 2
- `Defensive Driving` (no trailing space)
- `Defensive Driving ` (trailing space)

**Distribution**:
- Found in: 8 divisions
- Found in: 12 statuses
- Divisions: 2 - IL, 3 - TX, 5 - CA, 6 - FL, 7 - MI, 8 - OH, 10 - OR, 11 - GA, 12 - PA

**Impact**: HIGH
- Trailing space is invisible but breaks exact string matching
- Operators may appear non-compliant when they actually have the cert
- Both formats exist in requirements AND operator records

**Recommended Fix**: Remove trailing space from all instances → `Defensive Driving`

---

### 3. Driver's License_BACKSIDE

**Variations Found**: 2
- `Driver's License_BACKSIDE` (no trailing space)
- `Driver's License_BACKSIDE ` (trailing space)

**Distribution**:
- Found in: 7 divisions
- Found in: 12 statuses
- Divisions: 2 - IL, 3 - TX, 5 - CA, 6 - FL, 7 - MI, 8 - OH, 10 - OR, 11 - GA, 12 - PA

**Impact**: HIGH
- Same trailing space issue as Defensive Driving
- Critical document for onboarding validation

**Recommended Fix**: Remove trailing space → `Driver's License_BACKSIDE`

**Note**: Consider standardizing format to `Drivers License - Backside` for consistency with `Driver License` (no apostrophe)

---

### 4. Social Security Card

**Variations Found**: 2
- `SOCIAL SECURITY CARD` (ALL CAPS)
- `Social Security Card` (Title Case)

**Distribution**:
- Found in: 9 divisions (ALL divisions)
- Found in: 13 statuses (ALL statuses)
- Most widely distributed certification

**Impact**: CRITICAL
- Present in every status and division
- Capitalization mismatch affects all operators
- Core identification document

**Recommended Fix**: Standardize to `Social Security Card` (Title Case)

---

### 5. Background Check

**Variations Found**: 2
- `BACKGROUND CHECK` (ALL CAPS)
- `Background Check` (Title Case)

**Distribution**:
- Found in: 3 divisions
- Found in: 6 statuses
- Divisions: 3 - TX, 10 - OR, 11 - GA

**Impact**: Medium
- Critical compliance document
- Case sensitivity may cause validation issues

**Recommended Fix**: Standardize to `Background Check` (Title Case)

**Related**: Also appears as `BackgroundCheck` (no space) in operator records - this is a third variation!

---

### 6. Service Agreement

**Variations Found**: 2
- `SERVICE AGREEMENT` (ALL CAPS)
- `Service Agreement` (Title Case)

**Distribution**:
- Found in: 3 divisions
- Found in: 2 statuses (IN-SERVICE, APPROVED FOR CONTRACTING)
- Divisions: 7 - MI, 10 - OR, 11 - GA

**Impact**: Medium
- Critical contracting document
- Operators have both variations plus `Service Agreement-Schedule A`

**Recommended Fix**: Standardize to `Service Agreement` (Title Case)

---

### 7. DOT Pre-Contracting Drug/Alc Screen

**Variations Found**: 2
- `DOT Pre-Contracting Drug/Alc Screen` (no trailing space)
- `DOT Pre-Contracting Drug/Alc Screen ` (trailing space)

**Distribution**:
- Found in: 2 divisions
- Found in: 5 statuses
- Divisions: 3 - TX, 6 - FL

**Impact**: HIGH
- DOT compliance requirement
- Trailing space breaks matching

**Recommended Fix**: Remove trailing space → `DOT Pre-Contracting Drug/Alc Screen`

**Related Issues**: 
- Also exists as `DOT Pre-Contract Drug/Alc Screen` (no "ing")
- Also exists as `DOT Pre-Contract Drug/Alc DOT` (different ending)
- Multiple variations of same requirement!

---

### 8. DOT Driver Questionnaire

**Variations Found**: 2
- `DOT Driver Questionnaire` (no trailing space)
- `DOT Driver Questionnaire ` (trailing space)

**Distribution**:
- Found in: 7 divisions
- Found in: 9 statuses
- Divisions: 2 - IL, 3 - TX, 6 - FL, 7 - MI, 8 - OH, 10 - OR, 11 - GA

**Impact**: HIGH
- DOT compliance requirement
- Widespread distribution
- Trailing space issue

**Recommended Fix**: Remove trailing space → `DOT Driver Questionnaire`

---

## Additional Naming Issues Found in Operator Records

### Typos in Operator Certifications

1. **Lease Inpsection** → Should be `Lease Inspection`
   - Typo: "Inpsection" instead of "Inspection"
   - Found in operator records
   - Not in requirements (likely because of typo)

2. **Business Formation ** → Trailing space
   - Found in operator records
   - Not in requirements for Division 10

### Inconsistent Field Names

1. **Driver License vs Drivers License**
   - Requirements use: `Driver License ` (with trailing space, no 's')
   - Some references use: `Drivers License` (with 's', no space)
   - Operator records have both variations

2. **DOT Drug & Alcohol Policy vs DOT Drug and Alcohol Policy**
   - `DOT Drug & Alcohol Policy ` (ampersand, trailing space)
   - `DOT Drug and Alcohol Policy ` (spelled out "and", trailing space)
   - `DOT Drug/Alcohol Policy` (forward slash)
   - THREE different formats for same certification!

---

## Certification Types Needing Consolidation

### Multiple Names for Same Concept

1. **Drug/Alcohol Screening Variations**:
   - `DOT Pre-Contract Drug/Alc Screen`
   - `DOT Pre-Contracting Drug/Alc Screen` (with "ing")
   - `DOT Pre-Contract Drug/Alc DOT`
   - `NON-DOT Pre-Contract Drug/Alc Screen`
   - **Issue**: Should there be separate DOT and NON-DOT versions, or consolidate?

2. **Drug/Alcohol Policy Variations**:
   - `DOT Drug & Alcohol Policy `
   - `DOT Drug and Alcohol Policy `
   - `Drug and Alcohol Policy `
   - `DOT Drug/Alcohol Policy`

3. **Service Agreement Variations**:
   - `SERVICE AGREEMENT` (all caps)
   - `Service Agreement` (title case)
   - `Service Agreement-Schedule A` (with schedule designation)
   - **Question**: Is Schedule A a separate cert or part of Service Agreement?

4. **Vehicle Lease Variations**:
   - `Vehicle Lease Agreement`
   - `VEHICLE LEASE INSPECTION`
   - `Lease Inpsection` (typo)
   - **Issue**: Are these different certs or should be consolidated?

---

## Impact Analysis

### By Severity

#### CRITICAL Issues (Affect All Operators)
1. Social Security Card - case variations across all divisions/statuses
2. DOT Drug/Alcohol naming inconsistencies - compliance risk

#### HIGH Priority (Invisible Errors)
1. Trailing spaces on 4+ certification types - breaks exact matching
2. Driver License variations - core document inconsistency

#### MEDIUM Priority (Selective Impact)
1. Case sensitivity on Background Check, CTAA, Service Agreement
2. Typos in operator records

### By Division Impact

**Most Affected Divisions**:
1. Division 10 - OR: Missing REGISTRATION requirements + naming issues
2. Division 7 - MI: Most statuses defined, most naming variations
3. Division 3 - TX: Drug/Alcohol policy variations

**Least Affected**:
1. Division 2 - IL: Limited statuses defined
2. Division 5 - CA: Only appears in IN-SERVICE and ONBOARDING

---

## Recommendations

### Immediate Actions (High Priority)

1. **Remove ALL trailing spaces from certification names**
   - Run find/replace: `" ` → (nothing) in cert_requirements file
   - Affects: Defensive Driving, Driver's License_BACKSIDE, DOT Driver Questionnaire, DOT Pre-Contracting Drug/Alc Screen

2. **Standardize capitalization**
   - Choose: Title Case (recommended) or ALL CAPS
   - Update all instances to match chosen standard
   - Affects: Social Security Card, Background Check, Service Agreement, CTAA Passenger Assistance

3. **Fix typos in operator records**
   - `Lease Inpsection` → `Lease Inspection`
   - Review all operator cert records for similar issues

4. **Add missing REGISTRATION requirements for Division 10 - OR**
   - Currently has 0 requirements for REGISTRATION status
   - Blocks proper operator validation

### Medium-Term Actions

1. **Consolidate DOT Drug/Alcohol certifications**
   - Create master list of distinct cert types
   - Clarify difference between Policy vs Screen vs Orientation
   - Standardize naming: `DOT [Type] Drug and Alcohol [Purpose]`

2. **Standardize Driver License naming**
   - Choose: `Driver License` or `Drivers License` (recommend no apostrophe)
   - Decide: `_BACKSIDE` suffix or ` - Backside`
   - Update all references

3. **Service Agreement consolidation**
   - Clarify if Schedule A is separate or included
   - Document when each version is required

### Long-Term Actions

1. **Create certification master reference table**
   - One canonical name per cert type
   - Map all variations to canonical name
   - Include description, purpose, frequency

2. **Implement fuzzy matching in validation**
   - Use normalized names (lowercase, trimmed, no special chars)
   - Calculate similarity scores
   - Flag for manual review if 85%+ match but not exact

3. **Add validation rules to data entry**
   - Dropdown lists with canonical names only
   - Prevent free-text entry of cert names
   - Database constraints on certification type field

---

## Naming Standards Proposal

### Proposed Format Rules

1. **Capitalization**: Title Case for all cert names
   - Example: `Social Security Card` not `SOCIAL SECURITY CARD`

2. **Spaces**: No trailing or leading spaces
   - Trim all cert names in database

3. **Separators**: 
   - Use spaces between words
   - Use dash (-) for compound terms: `Non-DOT`, `Pre-Contract`
   - Use forward slash (/) only for alternatives: `Drug/Alcohol`

4. **Acronyms**: 
   - Keep acronyms in ALL CAPS: `DOT`, `MVR`, `CPR`, `AED`
   - Example: `DOT Physical Card`

5. **Abbreviations**:
   - Avoid where possible
   - If used, be consistent: `Alc` vs `Alcohol` (choose one)
   - Recommended: Spell out `Alcohol` for clarity

### Example Standardized Names

| Current Variations | Proposed Standard |
|-------------------|-------------------|
| SOCIAL SECURITY CARD, Social Security Card | Social Security Card |
| Defensive Driving, Defensive Driving  | Defensive Driving |
| Driver License , Drivers License, Driver's License | Driver License |
| Driver's License_BACKSIDE, Driver's License_BACKSIDE  | Driver License - Backside |
| DOT Drug & Alcohol Policy, DOT Drug and Alcohol Policy, DOT Drug/Alcohol Policy | DOT Drug and Alcohol Policy |
| BACKGROUND CHECK, Background Check, BackgroundCheck | Background Check |
| SERVICE AGREEMENT, Service Agreement | Service Agreement |
| CTAA PASSENGER ASSISTANCE, CTAA Passenger Assistance | CTAA Passenger Assistance |

---

## Testing Plan

### Phase 1: Validation
1. Export all cert names from requirements file
2. Export all cert names from operator records
3. Compare and identify all variations
4. Calculate impact: how many operators affected?

### Phase 2: Normalization
1. Create mapping table: old name → new canonical name
2. Update cert_requirements_by_status_division.json
3. Update all operator certification records in pay_Operators.json
4. Run validation to confirm all matches

### Phase 3: Verification
1. Re-run operator cert verification scripts
2. Check completion percentages before/after
3. Verify no operators lost valid certifications
4. Confirm naming consistency across all divisions

---

## Appendix: Complete Certification Inventory

### All Unique Certification Types (Normalized)

Total: 69 unique certification types found across all divisions and statuses

1. 10 Habits of a Professional Paratransit Operator
2. Background Check
3. Badge Photo
4. Big Star Compliance Form
5. Business Formation
6. CCF
7. COMPLIANCE REVIEW
8. CPR/AED/FIRST AID
9. CTAA Passenger Assistance
10. DART 5 STAR SRVC POLICY
11. DOT Chain of Custody Form
12. DOT Driver Questionnaire
13. DOT Drug & Alcohol Orientation
14. DOT Drug & Alcohol Policy
15. DOT Drug and Alcohol Policy
16. DOT Drug/Alcohol Policy
17. DOT Physical Card
18. DOT Pre Employment Donor Pass
19. DOT Pre-Contract Drug/Alc DOT
20. DOT Pre-Contract Drug/Alc Screen
21. DOT Pre-Contracting Drug/Alc Screen
22. DOT Release of Info Form 40.25
23. DRIVERS LICENSE w/CHAUF ENDORSE
24. Defensive Driving
25. Driver License
26. Driver's License_BACKSIDE
27. DriverMate Acknowledgement
28. Drivers License
29. Drivers License_BACKSIDE
30. Drug & Alcohol Orientation
31. Drug and Alcohol Policy
32. E-VERIFY
33. FT Code of Business Conduct
34. First Transit Orientation Acknowledgement
35. Fuel Passthrough Policy
36. Lease Inspection
37. Motor Vehicle Report (MVR)
38. NON DOT Pre Employment Donor Pass
39. NON-DOT Pre-Contract Drug/Alc Screen
40. Orientation-Big Star Safety and Service
41. Orientation-Client Hosted
42. RESULTS TRIMET BG CHECK_FingerPrint
43. SERVICE AGREEMENT
44. Service Agreement
45. Service Agreement-Schedule A
46. Social Security Card
47. TriMet Background Release Form A&B
48. UBER WAV APP
49. Vehicle Lease Agreement
50. VEHICLE LEASE INSPECTION
51. W9
52. WC Securement (Hands On)
53. Worker's Comp Coverage Waiver

*(Note: This list includes variations - actual unique concepts likely ~45-50)*

---

**Document Status**: Draft v1.0  
**Next Review**: After implementing Phase 1 recommendations  
**Owner**: Data Quality Team
