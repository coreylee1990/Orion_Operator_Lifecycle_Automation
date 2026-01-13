# Certification Naming Convention Analysis & Standardization Plan

**Date:** January 12, 2026  
**Purpose:** Document division-specific naming conventions and provide database standardization plan

---

## Executive Summary

Analysis of 81 operators across 8 divisions revealed **8 certification types with naming variations** affecting **74 operator records**. These variations are **NOT data quality errors** but rather **division-specific naming conventions**, particularly Division 7 (MI) which uses ALL CAPS format for certain certifications.

**Key Finding:** Division 7 (Michigan) consistently uses ALL CAPS for certifications like "CTAA PASSENGER ASSISTANCE" while all other divisions use Title Case "CTAA Passenger Assistance". This pattern is consistent in both operator records and certification requirements.

---

## Certification Variations Found

### 1. Background Check

**Canonical Format:** `Background Check`

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `Background Check` ✅ | 18 | 10, 6 | 10 - OR, 6 - FL |
| `BACKGROUND CHECK` | 9 | 7 | 7 - MI |

**Division Pattern:**
- Division 7 (MI): ALL CAPS
- All others: Title Case

**Database Updates Needed:** 9 operator records in Division 7

---

### 2. CTAA Passenger Assistance

**Canonical Format:** `CTAA Passenger Assistance`

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `CTAA Passenger Assistance` ✅ | 48 | 10, 11, 12, 3, 6, 8 | 10 - OR, 11 - GA, 12 - PA, 3 - TX, 5 - CA, 6 - FL, 8 - OH |
| `CTAA PASSENGER ASSISTANCE` | 7 | 7 | 7 - MI |

**Division Pattern:**
- Division 7 (MI): ALL CAPS
- All others: Title Case

**Database Updates Needed:** 7 operator records in Division 7

**Example Operator:** Willie Quainton (Division 7 - MI) has "CTAA PASSENGER ASSISTANCE" which is correct for Division 7's naming convention but needs standardization.

---

### 3. Defensive Driving

**Canonical Format:** `Defensive Driving` (NO trailing space)

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `Defensive Driving` ✅ | 32 | 11, 12, 3, 6, 8 | 11 - GA, 12 - PA, 3 - TX, 5 - CA, 6 - FL, 8 - OH |
| `Defensive Driving ` | 24 | 10, 7 | 10 - OR, 7 - MI |

**Issue:** Trailing space variation

**Database Updates Needed:** 24 operator records in Divisions 10 & 7

---

### 4. DOT Driver Questionnaire

**Canonical Format:** `DOT Driver Questionnaire ` (WITH trailing space)

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `DOT Driver Questionnaire ` ✅ | 34 | 10, 11, 6, 7, 8 | 10 - OR, 11 - GA, 5 - CA, 7 - MI, 8 - OH |
| `DOT Driver Questionnaire` | 8 | 12, 3, 6 | 3 - TX, 6 - FL |

**Issue:** Trailing space variation (canonical HAS trailing space)

**Database Updates Needed:** 8 operator records in Divisions 12, 3, 6

---

### 5. DOT Pre-Contracting Drug/Alc Screen

**Canonical Format:** `DOT Pre-Contracting Drug/Alc Screen ` (WITH trailing space)

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `DOT Pre-Contracting Drug/Alc Screen ` ✅ | 13 | 11 | 11 - GA |
| `DOT Pre-Contracting Drug/Alc Screen` | 1 | 6 | 6 - FL |

**Issue:** Trailing space variation (canonical HAS trailing space)

**Database Updates Needed:** 1 operator record in Division 6

---

### 6. Driver's License_BACKSIDE

**Canonical Format:** `Driver's License_BACKSIDE` (NO trailing space)

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `Driver's License_BACKSIDE` ✅ | 35 | 10, 12, 3, 6 | 10 - OR, 12 - PA, 3 - TX, 5 - CA, 6 - FL |
| `Driver's License_BACKSIDE ` | 7 | 7, 8 | 7 - MI, 8 - OH |

**Issue:** Trailing space variation

**Database Updates Needed:** 7 operator records in Divisions 7 & 8

---

### 7. Service Agreement

**Canonical Format:** `Service Agreement`

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `Service Agreement` ✅ | 11 | 10, 11, 7, 8 | 11 - GA, 8 - OH |
| `SERVICE AGREEMENT` | 11 | 10 | 10 - OR |

**Issue:** Mixed case within Division 10

**Database Updates Needed:** 11 operator records in Division 10

---

### 8. Social Security Card

**Canonical Format:** `Social Security Card`

| Format | Operator Count | Divisions | Requirement Divisions |
|--------|---------------|-----------|---------------------|
| `Social Security Card` ✅ | 53 | 10, 11, 12, 3, 6, 8 | 10 - OR, 11 - GA, 12 - PA, 2 - IL, 3 - TX, 5 - CA, 6 - FL, 8 - OH |
| `SOCIAL SECURITY CARD` | 7 | 7 | 7 - MI |

**Division Pattern:**
- Division 7 (MI): ALL CAPS
- All others: Title Case

**Database Updates Needed:** 7 operator records in Division 7

---

## Division-Specific Patterns

### Division 7 (Michigan) - ALL CAPS Convention

Division 7 consistently uses ALL CAPS for the following certifications:
- `BACKGROUND CHECK`
- `CTAA PASSENGER ASSISTANCE`
- `SOCIAL SECURITY CARD`

**This is NOT a data error** - both operator records AND certification requirements use ALL CAPS in Division 7.

**Reason:** Likely historical convention, different data entry system, or state-specific formatting requirements.

---

## Impact Analysis

### By Division

| Division | Records to Update | Affected Certifications |
|----------|------------------|------------------------|
| **7 (MI)** | **23** | Background Check (9), CTAA (7), Social Security Card (7) |
| **10 (OR)** | **28** | Defensive Driving (17), Service Agreement (11) |
| **3 (TX)** | **6** | DOT Driver Questionnaire (6) |
| **6 (FL)** | **2** | DOT Driver Questionnaire (1), DOT Pre-Contracting (1) |
| **8 (OH)** | **7** | Driver's License_BACKSIDE (7) |
| **12 (PA)** | **1** | DOT Driver Questionnaire (1) |

**Total:** 74 operator certification records need updating

### By Certification Type

| Certification | Records to Update |
|--------------|------------------|
| Defensive Driving | 24 |
| Service Agreement | 11 |
| Background Check | 9 |
| DOT Driver Questionnaire | 8 |
| CTAA Passenger Assistance | 7 |
| Social Security Card | 7 |
| Driver's License_BACKSIDE | 7 |
| DOT Pre-Contracting Drug/Alc Screen | 1 |

---

## Recommendations

### 1. Database Standardization (Immediate)

**Action:** Update all operator certification records to use canonical naming format.

**Method:** Execute SQL UPDATE statements (provided separately) to standardize all 74 records.

**Timeline:** Can be executed immediately; non-breaking change.

**Risk:** LOW - Only affects exact string matching, not data integrity.

### 2. Code Implementation (Required)

**Action:** Update all certification matching logic to use normalization function.

**Files to Update:**
- `generated/lifecycle-workflow-builder.html` - JavaScript matching logic
- `scripts/deep_dive_operator_analysis.py` - Python validation
- `scripts/analyze_cert_requirements_by_status_division.py` - Requirements analysis

**Method:** Import and use `cert_name_normalizer.py` module for all comparisons.

### 3. Requirements File Update (Optional but Recommended)

**Action:** Update `cert_requirements_by_status_division.json` to use canonical names.

**Affected:** Division 7 (MI) requirements need 3 certifications updated to canonical format.

**Decision Point:** Keep as-is (historically accurate) OR standardize (consistency).

### 4. Data Entry Prevention (Long-term)

**Action:** Implement validation at data entry point to prevent future variations.

**Methods:**
- Dropdown selection (not free text)
- Auto-correction on save
- Validation rules in database

---

## Division Reference Table

| Division # | State | Naming Convention | Notes |
|-----------|-------|------------------|-------|
| 2 | IL | Standard (Title Case) | - |
| 3 | TX | Standard (Title Case) | Some trailing space variations |
| 5 | CA | Standard (Title Case) | - |
| 6 | FL | Standard (Title Case) | Some trailing space variations |
| 7 | **MI** | **ALL CAPS** | Consistent pattern for 3 cert types |
| 8 | OH | Standard (Title Case) | Some trailing space variations |
| 10 | OR | Mixed | Has both formats for some certs |
| 11 | GA | Standard (Title Case) | - |
| 12 | PA | Standard (Title Case) | - |

---

## Testing Requirements

Before deploying database updates:

1. ✅ **Verify canonical mappings** - Confirm chosen formats match majority usage
2. ✅ **Test normalization function** - Ensure all variations correctly map to canonical
3. ⚠️ **Backup database** - Create backup before executing UPDATE statements
4. ⚠️ **Test matching logic** - Verify operators still match requirements after updates
5. ⚠️ **Validate progress bars** - Ensure UI still calculates correctly

---

## Maintenance Plan

### Monthly Review
- Check for new certification name variations
- Update canonical mapping if new certs added
- Review data entry patterns

### Quarterly Audit
- Verify all divisions still using expected formats
- Check for drift from canonical names
- Update documentation

### Annual Assessment
- Evaluate if division-specific conventions still necessary
- Consider full standardization if appropriate
- Update validation rules

---

## Related Files

- **Normalization Module:** `scripts/cert_name_normalizer.py`
- **Analysis Script:** `scripts/analyze_all_cert_variations.py`
- **SQL Updates:** `sql_queries/standardize_certification_names.sql`
- **Original Discovery:** `documentation/CERTIFICATION_NAMING_DISCREPANCIES.md`

---

## Glossary

- **Canonical Format:** The standardized, official name format chosen for a certification
- **Title Case:** First Letter Of Each Word Capitalized (e.g., "Background Check")
- **ALL CAPS:** EVERY LETTER CAPITALIZED (e.g., "BACKGROUND CHECK")
- **Trailing Space:** Invisible space character at end of string (e.g., "Defensive Driving ")
- **Normalization:** Converting names to consistent format for comparison

---

**Prepared By:** AI Analysis System  
**Last Updated:** January 12, 2026  
**Version:** 1.0
