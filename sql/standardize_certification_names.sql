-- ============================================================================
-- CERTIFICATION NAME STANDARDIZATION SQL STATEMENTS
-- ============================================================================
-- Purpose: Update operator certification records to use canonical naming
-- Date: January 12, 2026
-- Affected Records: 74 operator certification records across 6 divisions
-- Impact: Ensures consistent certification matching across divisions
-- 
-- IMPORTANT: BACKUP DATABASE BEFORE EXECUTING THESE STATEMENTS
-- ============================================================================

-- ============================================================================
-- PRE-FLIGHT CHECKS
-- ============================================================================

-- Verify current state - Count records that will be updated
SELECT 
    'Background Check' AS CertificationType,
    COUNT(*) AS RecordsToUpdate,
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ') AS AffectedDivisions
FROM pay_Certifications
WHERE Cert = 'BACKGROUND CHECK'
UNION ALL
SELECT 
    'CTAA Passenger Assistance',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'CTAA PASSENGER ASSISTANCE'
UNION ALL
SELECT 
    'Defensive Driving',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'Defensive Driving '
UNION ALL
SELECT 
    'DOT Driver Questionnaire',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'DOT Driver Questionnaire'
UNION ALL
SELECT 
    'DOT Pre-Contracting Drug/Alc Screen',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'DOT Pre-Contracting Drug/Alc Screen'
UNION ALL
SELECT 
    'Driver''s License_BACKSIDE',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'Driver''s License_BACKSIDE '
UNION ALL
SELECT 
    'Service Agreement',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'SERVICE AGREEMENT'
UNION ALL
SELECT 
    'Social Security Card',
    COUNT(*),
    STRING_AGG(DISTINCT SUBSTRING(DivisionID, 1, 2), ', ')
FROM pay_Certifications
WHERE Cert = 'SOCIAL SECURITY CARD';

-- Total count
SELECT 
    COUNT(*) AS TotalRecordsToUpdate
FROM pay_Certifications
WHERE Cert IN (
    'BACKGROUND CHECK',
    'CTAA PASSENGER ASSISTANCE',
    'Defensive Driving ',
    'DOT Driver Questionnaire',
    'DOT Pre-Contracting Drug/Alc Screen',
    'Driver''s License_BACKSIDE ',
    'SERVICE AGREEMENT',
    'SOCIAL SECURITY CARD'
);

-- ============================================================================
-- BACKUP RECOMMENDATION
-- ============================================================================
-- Execute this before making changes:
--
-- BACKUP DATABASE YourDatabaseName 
-- TO DISK = 'C:\Backups\YourDatabase_CertNameStandardization_20260112.bak'
-- WITH FORMAT, 
--      NAME = 'Certification Name Standardization Backup',
--      DESCRIPTION = 'Backup before updating 74 cert records to canonical names';
--
-- ============================================================================

-- ============================================================================
-- UPDATE STATEMENTS - EXECUTE IN TRANSACTION
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- 1. Background Check: 'BACKGROUND CHECK' → 'Background Check'
-- ============================================================================
-- Division 7 (MI) - 9 records
-- Reason: Standardize to Title Case format used by 18 operators in other divisions
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'Background Check',
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'  -- System update
WHERE Cert = 'BACKGROUND CHECK'
  AND DivisionID LIKE '7%';

PRINT '✓ Updated Background Check: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 2. CTAA Passenger Assistance: 'CTAA PASSENGER ASSISTANCE' → 'CTAA Passenger Assistance'
-- ============================================================================
-- Division 7 (MI) - 7 records
-- Reason: Standardize to Title Case format used by 48 operators in other divisions
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'CTAA Passenger Assistance',
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'CTAA PASSENGER ASSISTANCE'
  AND DivisionID LIKE '7%';

PRINT '✓ Updated CTAA Passenger Assistance: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 3. Defensive Driving: 'Defensive Driving ' → 'Defensive Driving' (remove trailing space)
-- ============================================================================
-- Divisions 10 (OR) & 7 (MI) - 24 records
-- Reason: Remove trailing space to match format used by 32 operators
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'Defensive Driving',
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'Defensive Driving '  -- Note: trailing space
  AND DivisionID IN (
      SELECT DISTINCT DivisionID 
      FROM pay_Certifications 
      WHERE DivisionID LIKE '10%' OR DivisionID LIKE '7%'
  );

PRINT '✓ Updated Defensive Driving: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 4. DOT Driver Questionnaire: 'DOT Driver Questionnaire' → 'DOT Driver Questionnaire ' (add trailing space)
-- ============================================================================
-- Divisions 12 (PA), 3 (TX), 6 (FL) - 8 records
-- Reason: Add trailing space to match format used by 34 operators (canonical has trailing space)
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'DOT Driver Questionnaire ',  -- Note: trailing space added
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'DOT Driver Questionnaire'  -- No trailing space
  AND DivisionID IN (
      SELECT DISTINCT DivisionID 
      FROM pay_Certifications 
      WHERE DivisionID LIKE '12%' OR DivisionID LIKE '3%' OR DivisionID LIKE '6%'
  );

PRINT '✓ Updated DOT Driver Questionnaire: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 5. DOT Pre-Contracting Drug/Alc Screen: Add trailing space
-- ============================================================================
-- Division 6 (FL) - 1 record
-- Reason: Add trailing space to match format used by 13 operators
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'DOT Pre-Contracting Drug/Alc Screen ',  -- Note: trailing space added
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'DOT Pre-Contracting Drug/Alc Screen'  -- No trailing space
  AND DivisionID LIKE '6%';

PRINT '✓ Updated DOT Pre-Contracting Drug/Alc Screen: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 6. Driver's License_BACKSIDE: Remove trailing space
-- ============================================================================
-- Divisions 7 (MI) & 8 (OH) - 7 records
-- Reason: Remove trailing space to match format used by 35 operators
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'Driver''s License_BACKSIDE',  -- No trailing space
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'Driver''s License_BACKSIDE '  -- Note: trailing space
  AND DivisionID IN (
      SELECT DISTINCT DivisionID 
      FROM pay_Certifications 
      WHERE DivisionID LIKE '7%' OR DivisionID LIKE '8%'
  );

PRINT '✓ Updated Driver''s License_BACKSIDE: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 7. Service Agreement: 'SERVICE AGREEMENT' → 'Service Agreement'
-- ============================================================================
-- Division 10 (OR) - 11 records
-- Reason: Standardize to Title Case format used by requirements in Divisions 11 & 8
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'Service Agreement',
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'SERVICE AGREEMENT'
  AND DivisionID LIKE '10%';

PRINT '✓ Updated Service Agreement: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- 8. Social Security Card: 'SOCIAL SECURITY CARD' → 'Social Security Card'
-- ============================================================================
-- Division 7 (MI) - 7 records
-- Reason: Standardize to Title Case format used by 53 operators in other divisions
-- ============================================================================

UPDATE pay_Certifications
SET Cert = 'Social Security Card',
    UpdateAt = GETDATE(),
    UpdateBy = '00000000-0000-0000-0000-000000000000'
WHERE Cert = 'SOCIAL SECURITY CARD'
  AND DivisionID LIKE '7%';

PRINT '✓ Updated Social Security Card: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' records';

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- After updates, verify no old formats remain
SELECT 
    'VERIFICATION: Old formats remaining' AS CheckType,
    Cert,
    COUNT(*) AS Count,
    STRING_AGG(DISTINCT DivisionID, ', ') AS Divisions
FROM pay_Certifications
WHERE Cert IN (
    'BACKGROUND CHECK',
    'CTAA PASSENGER ASSISTANCE',
    'Defensive Driving ',  -- with space
    'DOT Driver Questionnaire',  -- without space
    'DOT Pre-Contracting Drug/Alc Screen',  -- without space
    'Driver''s License_BACKSIDE ',  -- with space
    'SERVICE AGREEMENT',
    'SOCIAL SECURITY CARD'
)
GROUP BY Cert;

-- Should return 0 rows if all updates successful

-- ============================================================================
-- FINAL VERIFICATION - Count canonical formats
-- ============================================================================
SELECT 
    'VERIFICATION: Canonical formats' AS CheckType,
    Cert,
    COUNT(*) AS Count,
    STRING_AGG(DISTINCT DivisionID, ', ') AS Divisions
FROM pay_Certifications
WHERE Cert IN (
    'Background Check',
    'CTAA Passenger Assistance',
    'Defensive Driving',
    'DOT Driver Questionnaire ',
    'DOT Pre-Contracting Drug/Alc Screen ',
    'Driver''s License_BACKSIDE',
    'Service Agreement',
    'Social Security Card'
)
GROUP BY Cert
ORDER BY Cert;

-- ============================================================================
-- COMMIT OR ROLLBACK
-- ============================================================================
-- Review verification results above before committing
-- If everything looks correct:
--   COMMIT TRANSACTION;
-- If there are issues:
--   ROLLBACK TRANSACTION;

-- Uncomment one of the following after reviewing results:
-- COMMIT TRANSACTION;
-- ROLLBACK TRANSACTION;

PRINT '';
PRINT '============================================================================';
PRINT 'IMPORTANT: Review verification results before committing!';
PRINT 'If all looks good: COMMIT TRANSACTION;';
PRINT 'If issues found: ROLLBACK TRANSACTION;';
PRINT '============================================================================';

-- ============================================================================
-- POST-UPDATE RECOMMENDATIONS
-- ============================================================================
-- After successful commit:
-- 1. Update cert_requirements_by_status_division.json with canonical names (optional)
-- 2. Deploy updated lifecycle-workflow-builder.html with normalization function
-- 3. Update Python analysis scripts to use cert_name_normalizer.py
-- 4. Run full validation: python3 scripts/analyze_cert_name_mismatches.py
-- 5. Test operator profile UI to ensure progress bars calculate correctly
-- ============================================================================

-- ============================================================================
-- ROLLBACK PROCEDURE (if needed after commit)
-- ============================================================================
-- If you need to rollback after commit, you can restore from backup:
--
-- RESTORE DATABASE YourDatabaseName 
-- FROM DISK = 'C:\Backups\YourDatabase_CertNameStandardization_20260112.bak'
-- WITH REPLACE;
--
-- ============================================================================

-- ============================================================================
-- NOTES
-- ============================================================================
-- * All updates include UpdateAt timestamp and system UpdateBy ID
-- * Division filters use LIKE for flexibility with division format (e.g., '7 - MI')
-- * Trailing spaces are explicitly noted in comments
-- * Each update is isolated by division to prevent unintended changes
-- * Total expected updates: 74 records
-- 
-- BREAKDOWN BY DIVISION:
-- - Division 7 (MI): 23 records (3 cert types)
-- - Division 10 (OR): 28 records (2 cert types)
-- - Division 3 (TX): 6 records (1 cert type)
-- - Division 6 (FL): 2 records (2 cert types)
-- - Division 8 (OH): 7 records (1 cert type)
-- - Division 12 (PA): 1 record (1 cert type)
-- 
-- CERTIFICATION TYPES AFFECTED:
-- 1. Background Check (9 records)
-- 2. CTAA Passenger Assistance (7 records)
-- 3. Defensive Driving (24 records)
-- 4. DOT Driver Questionnaire (8 records)
-- 5. DOT Pre-Contracting Drug/Alc Screen (1 record)
-- 6. Driver's License_BACKSIDE (7 records)
-- 7. Service Agreement (11 records)
-- 8. Social Security Card (7 records)
-- ============================================================================
