# Project Structure Reorganization Plan

## Current State (Disorganized)

```
Orion_Operator_Lifecycle_Automation/
├── ANALYSIS_SUITE_README.md
├── CERTIFICATION_DOCUMENTATION_SUMMARY.md
├── CERTIFICATIONS_SCHEMA.md
├── COMPLETE_SOLUTION_SUMMARY.md
├── CRITICAL_FINDINGS.md
├── DATA_SCHEMA.md
├── Instructions.md
├── operators.txt
├── PizzaStatuses.code-search
├── README.md
├── SCRIPT_AUDIT_REPORT.md
├── WORKFLOW_BUILDER_CHANGELOG.md
├── __pycache__/
├── data/
│   ├── pay_Certifications.json/txt
│   ├── pay_CertTypes.json/txt
│   ├── pay_Operators.json (+ 6 backups!)
│   ├── pay_StatusTracker.json/txt
│   ├── pay_StatusTypes.json/txt
│   ├── rawOperators.json
│   └── pay_PizzaStatuses.json/txt
├── externalSources/
│   └── [raw CSV/text files]
├── generated/
│   ├── cert_requirements_*
│   ├── certification_*
│   ├── operator_*
│   ├── *.html files
│   ├── *.md files
│   ├── generate_artifacts/
│   └── pay_Operators.json (duplicate!)
├── scripts/
│   ├── analyze_*.py (many)
│   ├── test_*.py
│   ├── deep_dive_*.py
│   └── generate_*.py
└── sql_queries/
    └── [SQL files]
```

**Problems**:
- 8+ MD files in root directory (mixing docs, reports, logs)
- Duplicate pay_Operators.json in both data/ and generated/
- 6 backup files cluttering data/
- Mixed concerns in generated/ (HTML, JSON, MD files)
- No clear separation between analysis, docs, and artifacts

---

## Proposed Structure (Organized)

```
Orion_Operator_Lifecycle_Automation/
│
├── README.md                          # Main project overview
├── .gitignore                         # Ignore backups, pycache, etc.
│
├── documentation/                     # All documentation
│   ├── README.md                      # Index of all docs
│   ├── PROJECT_OVERVIEW.md
│   ├── DATA_SCHEMA.md
│   ├── CERTIFICATIONS_SCHEMA.md
│   ├── CERTIFICATION_NAMING_DISCREPANCIES.md
│   ├── USER_GUIDE.md
│   └── DEVELOPMENT_GUIDE.md
│
├── reports/                           # Analysis findings & reports
│   ├── CRITICAL_FINDINGS.md
│   ├── SCRIPT_AUDIT_REPORT.md
│   ├── ANALYSIS_SUITE_README.md
│   ├── CERTIFICATION_DOCUMENTATION_SUMMARY.md
│   └── COMPLETE_SOLUTION_SUMMARY.md
│
├── changelogs/                        # Development history
│   └── WORKFLOW_BUILDER_CHANGELOG.md
│
├── data/                              # Source data (read-only)
│   ├── raw/                           # Original unmodified data
│   │   ├── pay_Operators.json
│   │   ├── pay_Certifications.json
│   │   ├── pay_CertTypes.json
│   │   ├── pay_StatusTracker.json
│   │   ├── pay_StatusTypes.json
│   │   └── pay_PizzaStatuses.json
│   │
│   ├── processed/                     # Cleaned/processed data
│   │   ├── operators_normalized.json
│   │   └── cert_requirements_by_status_division.json
│   │
│   ├── external/                      # Data from external sources
│   │   ├── operators_raw_text.txt
│   │   ├── certificates_raw_text.txt
│   │   └── operators_export.csv
│   │
│   └── backups/                       # Time-stamped backups
│       ├── pay_Operators.json.backup.20260110_183158
│       ├── pay_Operators.json.backup.20260110_183243
│       └── [other backups]
│
├── scripts/                           # All Python scripts
│   ├── README.md                      # Script index & usage
│   │
│   ├── analysis/                      # Data analysis scripts
│   │   ├── analyze_cert_requirements_by_status_division.py
│   │   ├── analyze_cert_requirements_by_status.py
│   │   ├── analyze_cert_types_from_data.py
│   │   ├── analyze_certifications.py
│   │   ├── analyze_operator_cert_gaps.py
│   │   ├── deep_dive_operator_analysis.py
│   │   └── test_operator_cert_verification.py
│   │
│   ├── generation/                    # Artifact generation
│   │   ├── generate_cert_requirements_viewer.py
│   │   ├── generate_operator_gaps_viewer.py
│   │   ├── generate_lifecycle_workflow_builder.py
│   │   └── generate_reports.py
│   │
│   ├── utilities/                     # Helper/utility scripts
│   │   ├── normalize_cert_names.py
│   │   ├── create_backups.py
│   │   ├── validate_data_integrity.py
│   │   └── export_to_formats.py
│   │
│   └── sql/                           # SQL query generators
│       ├── get_status_tracker_data.sql
│       └── [other SQL files]
│
├── web_interface/                     # Web-based tools
│   ├── README.md                      # How to run the server
│   ├── server.sh                      # Start script for HTTP server
│   │
│   ├── assets/                        # Shared CSS/JS/images
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── lifecycle_workflow_builder/
│   │   ├── index.html                 # Main workflow builder
│   │   ├── workflow.js
│   │   └── workflow.css
│   │
│   ├── cert_requirements_viewer/
│   │   ├── index.html
│   │   ├── viewer.js
│   │   └── viewer.css
│   │
│   └── operator_gaps_viewer/
│       ├── index.html
│       ├── gaps.js
│       └── gaps.css
│
├── output/                            # Generated analysis outputs
│   ├── json/                          # Generated JSON data
│   │   ├── cert_requirements_analysis.json
│   │   ├── operator_certification_gaps.json
│   │   └── status_progression_analysis.json
│   │
│   ├── reports/                       # Generated text reports
│   │   ├── certification_analysis_report.txt
│   │   ├── operator_gaps_report.txt
│   │   └── progression_summary.txt
│   │
│   └── exports/                       # Exportable formats
│       ├── certification_matrix.csv
│       └── operator_status_export.xlsx
│
├── tests/                             # Test scripts
│   ├── test_data_integrity.py
│   ├── test_cert_matching.py
│   └── test_operator_validation.py
│
├── config/                            # Configuration files
│   ├── divisions.json                 # Division definitions
│   ├── status_types.json              # Status definitions
│   └── certification_standards.json   # Canonical cert names
│
└── archive/                           # Archived/deprecated files
    ├── operators.txt
    ├── PizzaStatuses.code-search
    └── rawOperators.json
```

---

## Migration Steps

### Step 1: Create New Directory Structure
```bash
mkdir -p documentation reports changelogs
mkdir -p data/{raw,processed,external,backups}
mkdir -p scripts/{analysis,generation,utilities,sql}
mkdir -p web_interface/{assets/{css,js,images},lifecycle_workflow_builder,cert_requirements_viewer,operator_gaps_viewer}
mkdir -p output/{json,reports,exports}
mkdir -p tests config archive
```

### Step 2: Move Documentation
```bash
mv DATA_SCHEMA.md documentation/
mv CERTIFICATIONS_SCHEMA.md documentation/
mv CRITICAL_FINDINGS.md reports/
mv ANALYSIS_SUITE_README.md reports/
mv CERTIFICATION_DOCUMENTATION_SUMMARY.md reports/
mv COMPLETE_SOLUTION_SUMMARY.md reports/
mv SCRIPT_AUDIT_REPORT.md reports/
mv WORKFLOW_BUILDER_CHANGELOG.md changelogs/
mv Instructions.md documentation/DEVELOPMENT_GUIDE.md
```

### Step 3: Organize Data Files
```bash
# Move raw data
mv data/*.json data/raw/
mv data/*.txt data/raw/

# Move backups
mv data/*.backup.* data/backups/

# Move external sources
mv externalSources/* data/external/
rmdir externalSources

# Move processed data
mv generated/cert_requirements_by_status_division.json data/processed/
mv generated/certification_requirements_analysis.json data/processed/
```

### Step 4: Organize Scripts
```bash
# Move analysis scripts
mv scripts/analyze_*.py scripts/analysis/
mv scripts/test_*.py scripts/analysis/
mv scripts/deep_dive_*.py scripts/analysis/

# Move generation scripts  
mv scripts/generate_*.py scripts/generation/

# Move SQL
mv sql_queries/* scripts/sql/
rmdir sql_queries
```

### Step 5: Organize Web Interface
```bash
# Move HTML files
mv generated/lifecycle-workflow-builder.html web_interface/lifecycle_workflow_builder/index.html
mv generated/cert_requirements_viewer.html web_interface/cert_requirements_viewer/index.html
mv generated/operator_gaps_viewer.html web_interface/operator_gaps_viewer/index.html
mv generated/index.html web_interface/

# Create server script
echo '#!/bin/bash
cd "$(dirname "$0")"
python3 -m http.server 8083
' > web_interface/server.sh
chmod +x web_interface/server.sh
```

### Step 6: Organize Output Files
```bash
# Move generated analysis
mv generated/*.json output/json/
mv generated/*.txt output/reports/
```

### Step 7: Archive Old Files
```bash
mv operators.txt archive/
mv PizzaStatuses.code-search archive/
mv data/raw/rawOperators.json archive/
```

### Step 8: Create Index Files
```bash
# Create documentation index
cat > documentation/README.md << 'EOF'
# Documentation Index

## Project Documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - High-level project description
- [DATA_SCHEMA.md](DATA_SCHEMA.md) - Data structure documentation
- [CERTIFICATIONS_SCHEMA.md](CERTIFICATIONS_SCHEMA.md) - Certification data schema
- [CERTIFICATION_NAMING_DISCREPANCIES.md](CERTIFICATION_NAMING_DISCREPANCIES.md) - Known naming issues
- [USER_GUIDE.md](USER_GUIDE.md) - How to use the tools
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Developer instructions
EOF

# Create scripts index
cat > scripts/README.md << 'EOF'
# Scripts Index

## Analysis Scripts (scripts/analysis/)
- `analyze_cert_requirements_by_status_division.py` - Analyze requirements by division
- `analyze_operator_cert_gaps.py` - Find missing certifications
- `deep_dive_operator_analysis.py` - Detailed operator analysis
- `test_operator_cert_verification.py` - Verify operator cert status

## Generation Scripts (scripts/generation/)
- `generate_cert_requirements_viewer.py` - Create cert viewer HTML
- `generate_lifecycle_workflow_builder.py` - Create workflow builder

## Utility Scripts (scripts/utilities/)
- `normalize_cert_names.py` - Standardize certification names
- `validate_data_integrity.py` - Check data consistency
EOF
```

### Step 9: Update File Paths
Create a migration script to update import paths:

```python
# scripts/utilities/update_file_paths.py
import os
import re

PATH_MAPPINGS = {
    '../generated/pay_Operators.json': '../data/raw/pay_Operators.json',
    '../generated/cert_requirements_by_status_division.json': '../data/processed/cert_requirements_by_status_division.json',
    'pay_Operators.json': '../data/raw/pay_Operators.json',
    'cert_requirements_by_status_division.json': '../data/processed/cert_requirements_by_status_division.json',
}

def update_file_paths(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') or file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                updated = content
                for old_path, new_path in PATH_MAPPINGS.items():
                    updated = updated.replace(old_path, new_path)
                
                if updated != content:
                    with open(filepath, 'w') as f:
                        f.write(updated)
                    print(f'Updated: {filepath}')

if __name__ == '__main__':
    update_file_paths('scripts/')
    update_file_paths('web_interface/')
```

---

## .gitignore Recommendations

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Backups
*.backup.*
*~

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data (optional - depends on if you want to track data files)
# data/raw/*.json
# data/processed/*.json

# Outputs (regeneratable)
output/json/
output/reports/
output/exports/

# Logs
*.log
```

---

## Benefits of New Structure

1. **Clear Separation of Concerns**
   - Documentation vs Reports vs Code vs Data
   - No more mixing HTML, JSON, MD in same folder

2. **Easier Navigation**
   - Related files grouped together
   - Clear purpose for each directory
   - README files provide guidance

3. **Better Version Control**
   - Backups in dedicated folder
   - Can gitignore generated outputs
   - Clearer commit history

4. **Scalability**
   - Easy to add new scripts/tools
   - Room for tests and config
   - Archive for deprecated code

5. **Professional Appearance**
   - Follows industry best practices
   - Easier for new developers to understand
   - Documentation-first approach

---

## Post-Migration Checklist

- [ ] All scripts run successfully with new paths
- [ ] Web interface loads from new location
- [ ] Documentation links are updated
- [ ] Old directories removed
- [ ] .gitignore created
- [ ] README.md updated with new structure
- [ ] Team notified of new structure
- [ ] Bookmark server URL: http://localhost:8083/

---

**Status**: Proposed  
**Implementation Time**: ~2 hours  
**Breaking Changes**: Yes (file paths change)  
**Requires Testing**: Yes (all scripts and web interface)
