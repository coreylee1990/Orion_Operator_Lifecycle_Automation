# Database Standardization Summary

**Date:** January 12, 2026  
**Total Records to Update:** 74 certification records  
**SQL File:** `/sql_queries/standardize_certification_names.sql`

---

## Quick Reference: What Needs to Change

### Division 7 (Michigan) - 23 Records

Division 7 uses ALL CAPS format for certain certifications. These need to be updated to Title Case:

| Current Name (ALL CAPS) | → | Canonical Name (Title Case) | Count |
|------------------------|---|---------------------------|-------|
| `BACKGROUND CHECK` | → | `Background Check` | 9 |
| `CTAA PASSENGER ASSISTANCE` | → | `CTAA Passenger Assistance` | 7 |
| `SOCIAL SECURITY CARD` | → | `Social Security Card` | 7 |

**SQL Update Commands:**
```sql
UPDATE pay_Certifications SET Cert = 'Background Check' WHERE Cert = 'BACKGROUND CHECK' AND DivisionID LIKE '7%';
UPDATE pay_Certifications SET Cert = 'CTAA Passenger Assistance' WHERE Cert = 'CTAA PASSENGER ASSISTANCE' AND DivisionID LIKE '7%';
UPDATE pay_Certifications SET Cert = 'Social Security Card' WHERE Cert = 'SOCIAL SECURITY CARD' AND DivisionID LIKE '7%';
```

---

### Division 10 (Oregon) - 28 Records

| Issue | Current Name | → | Canonical Name | Count |
|-------|-------------|---|---------------|-------|
| Trailing space | `Defensive Driving ` | → | `Defensive Driving` | 17 |
| Case mismatch | `SERVICE AGREEMENT` | → | `Service Agreement` | 11 |

**SQL Update Commands:**
```sql
UPDATE pay_Certifications SET Cert = 'Defensive Driving' WHERE Cert = 'Defensive Driving ' AND DivisionID LIKE '10%';
UPDATE pay_Certifications SET Cert = 'Service Agreement' WHERE Cert = 'SERVICE AGREEMENT' AND DivisionID LIKE '10%';
```

---

### Division 7 (Michigan) - Trailing Space Issues

| Issue | Current Name | → | Canonical Name | Count |
|-------|-------------|---|---------------|-------|
| Trailing space | `Defensive Driving ` | → | `Defensive Driving` | 7 |
| Trailing space | `Driver's License_BACKSIDE ` | → | `Driver's License_BACKSIDE` | 6 |

**SQL Update Commands:**
```sql
UPDATE pay_Certifications SET Cert = 'Defensive Driving' WHERE Cert = 'Defensive Driving ' AND DivisionID LIKE '7%';
UPDATE pay_Certifications SET Cert = 'Driver''s License_BACKSIDE' WHERE Cert = 'Driver''s License_BACKSIDE ' AND DivisionID LIKE '7%';
```

---

### Division 8 (Ohio) - 1 Record

| Issue | Current Name | → | Canonical Name | Count |
|-------|-------------|---|---------------|-------|
| Trailing space | `Driver's License_BACKSIDE ` | → | `Driver's License_BACKSIDE` | 1 |

**SQL Update Command:**
```sql
UPDATE pay_Certifications SET Cert = 'Driver''s License_BACKSIDE' WHERE Cert = 'Driver''s License_BACKSIDE ' AND DivisionID LIKE '8%';
```

---

### Divisions 3, 6, 12 - Missing Trailing Space (8 Records)

**IMPORTANT:** The canonical format for these certifications **includes a trailing space**.

| Issue | Current Name | → | Canonical Name | Count | Divisions |
|-------|-------------|---|---------------|-------|-----------|
| Missing space | `DOT Driver Questionnaire` | → | `DOT Driver Questionnaire ` | 8 | 3, 6, 12 |
| Missing space | `DOT Pre-Contracting Drug/Alc Screen` | → | `DOT Pre-Contracting Drug/Alc Screen ` | 1 | 6 |

**SQL Update Commands:**
```sql
UPDATE pay_Certifications SET Cert = 'DOT Driver Questionnaire ' WHERE Cert = 'DOT Driver Questionnaire' AND DivisionID IN ('3%', '6%', '12%');
UPDATE pay_Certifications SET Cert = 'DOT Pre-Contracting Drug/Alc Screen ' WHERE Cert = 'DOT Pre-Contracting Drug/Alc Screen' AND DivisionID LIKE '6%';
```

---

## Summary by Certification Type

| # | Certification Type | Old Format(s) | Canonical Format | Records | Divisions |
|---|-------------------|--------------|-----------------|---------|-----------|
| 1 | Background Check | `BACKGROUND CHECK` | `Background Check` | 9 | 7 |
| 2 | CTAA Passenger Assistance | `CTAA PASSENGER ASSISTANCE` | `CTAA Passenger Assistance` | 7 | 7 |
| 3 | Defensive Driving | `Defensive Driving ` (with space) | `Defensive Driving` | 24 | 7, 10 |
| 4 | DOT Driver Questionnaire | `DOT Driver Questionnaire` (no space) | `DOT Driver Questionnaire ` | 8 | 3, 6, 12 |
| 5 | DOT Pre-Contracting | `DOT Pre-Contracting Drug/Alc Screen` (no space) | `DOT Pre-Contracting Drug/Alc Screen ` | 1 | 6 |
| 6 | Driver's License_BACKSIDE | `Driver's License_BACKSIDE ` (with space) | `Driver's License_BACKSIDE` | 7 | 7, 8 |
| 7 | Service Agreement | `SERVICE AGREEMENT` | `Service Agreement` | 11 | 10 |
| 8 | Social Security Card | `SOCIAL SECURITY CARD` | `Social Security Card` | 7 | 7 |

**Total: 74 records**

---

## Division Impact Summary

| Division | State | Records to Update | Certification Types Affected |
|----------|-------|------------------|----------------------------|
| **7** | MI | **23** | Background Check (9), CTAA (7), Social Security Card (7) |
| **10** | OR | **28** | Defensive Driving (17), Service Agreement (11) |
| **3** | TX | **6** | DOT Driver Questionnaire (6) |
| **6** | FL | **2** | DOT Driver Questionnaire (1), DOT Pre-Contracting (1) |
| **8** | OH | **7** | Driver's License_BACKSIDE (7) |
| **12** | PA | **1** | DOT Driver Questionnaire (1) |
| **7** | MI | **7** | Defensive Driving (7) + Driver's License (included in 23 above) |

---

## Why These Changes Are Needed

### 1. **Case Variations (Division 7)**
Division 7 (Michigan) historically used ALL CAPS for certain certifications:
- `BACKGROUND CHECK` (should be `Background Check`)
- `CTAA PASSENGER ASSISTANCE` (should be `CTAA Passenger Assistance`)
- `SOCIAL SECURITY CARD` (should be `Social Security Card`)

This is **not a data error** - it's a division-specific convention. However, for consistent system-wide matching, we're standardizing to Title Case.

### 2. **Trailing Space Issues**
Several certifications have inconsistent trailing spaces:
- **Remove space:** `Defensive Driving `, `Driver's License_BACKSIDE `
- **Add space:** `DOT Driver Questionnaire`, `DOT Pre-Contracting Drug/Alc Screen`

Trailing spaces cause exact string matching to fail even though the certifications are logically the same.

### 3. **Mixed Case in Same Division**
Division 10 has both `SERVICE AGREEMENT` and `Service Agreement` - standardizing to Title Case.

---

## Execution Plan

### Before Running SQL:

1. **Backup Database**
   ```sql
   BACKUP DATABASE YourDatabaseName 
   TO DISK = 'C:\Backups\YourDatabase_CertNameStandardization_20260112.bak';
   ```

2. **Review Pre-Flight Checks**
   - Run the verification queries in the SQL file
   - Confirm 74 total records will be updated
   - Review affected divisions

### Execute Updates:

1. **Run in Transaction**
   - Execute all UPDATE statements within `BEGIN TRANSACTION`
   - Review verification queries
   - If correct: `COMMIT TRANSACTION`
   - If issues: `ROLLBACK TRANSACTION`

2. **Verify Results**
   - Check that old formats no longer exist
   - Confirm canonical formats have expected counts
   - Review audit log (UpdateAt timestamps)

### After Database Update:

1. **Update Application Code**
   - Deploy `cert_name_normalizer.py` module
   - Update `lifecycle-workflow-builder.html` to use normalization
   - Update Python analysis scripts

2. **Test Thoroughly**
   - Run `analyze_cert_name_mismatches.py` - should find 0 issues
   - Test operator profile UI - progress bars should calculate correctly
   - Verify certification matching across all divisions

3. **Monitor**
   - Watch for any matching issues in production
   - Review operator certification gaps report
   - Check for new naming variations

---

## Rollback Plan

If issues occur after commit:

```sql
RESTORE DATABASE YourDatabaseName 
FROM DISK = 'C:\Backups\YourDatabase_CertNameStandardization_20260112.bak'
WITH REPLACE;
```

---

## Files Created/Updated

### Documentation
- ✅ [DIVISION_SPECIFIC_CERT_NAMING_CONVENTIONS.md](../documentation/DIVISION_SPECIFIC_CERT_NAMING_CONVENTIONS.md) - Full analysis with patterns and recommendations
- ✅ [DATABASE_STANDARDIZATION_SUMMARY.md](../documentation/DATABASE_STANDARDIZATION_SUMMARY.md) - This file

### Code
- ✅ [cert_name_normalizer.py](../scripts/cert_name_normalizer.py) - Python module for name normalization
- ✅ [analyze_all_cert_variations.py](../scripts/analyze_all_cert_variations.py) - Comprehensive variation analysis
- ✅ [analyze_cert_name_mismatches.py](../scripts/analyze_cert_name_mismatches.py) - Operator-specific mismatch analysis

### SQL
- ✅ [standardize_certification_names.sql](../sql_queries/standardize_certification_names.sql) - Production-ready UPDATE statements

---

## Next Steps

1. **Review this summary** with stakeholders
2. **Schedule maintenance window** for database updates
3. **Execute SQL** in test environment first
4. **Deploy code changes** after successful database update
5. **Run validation** to confirm 0 mismatches
6. **Update documentation** if needed

---

## Contact

For questions about this standardization:
- Review full documentation: `DIVISION_SPECIFIC_CERT_NAMING_CONVENTIONS.md`
- Test normalization: `python3 scripts/cert_name_normalizer.py`
- Analyze current state: `python3 scripts/analyze_all_cert_variations.py`

---

**Prepared By:** AI Analysis System  
**Last Updated:** January 12, 2026  
**Version:** 1.0  
**Status:** Ready for Review
