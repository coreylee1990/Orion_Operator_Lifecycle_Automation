# Orion Operator Lifecycle Automation

**Single source of truth for operator certification requirements and compliance tracking.**

---

## 📁 Project Structure

```
Orion_Operator_Lifecycle_Automation/
├── config/                        # Configuration files
│   └── master_cert_requirements.json    # Master requirements definition
├── data/                          # Raw database exports (JSON)
│   ├── pay_Certifications.json
│   ├── pay_Operators.json
│   └── ...
├── tools/                         # User-facing tools
│   ├── lifecycle-workflow-builder.html  # Requirements editor UI
│   ├── pay_Operators.json              # Operator data for UI
│   └── master_cert_requirements.json   # Requirements for UI
├── scripts/                       # Python automation scripts
│   ├── reports/                   # Report generators
│   ├── utilities/                 # Helper scripts
│   └── archive/                   # Deprecated scripts
├── sql/                           # SQL queries for database
├── docs/                          # Documentation
│   ├── guides/                    # User guides
│   ├── technical/                 # Technical documentation
│   └── archive/                   # Old documentation
├── output/                        # Generated reports
│   ├── compliance_gap_report.json
│   └── archive/                   # Historical reports
└── external/                      # External data sources
```

---

## 🚀 Quick Start

### 1. View Operator Compliance

```bash
# Generate compliance gap report
python3 scripts/reports/generate_compliance_gap_report.py

# Output:
# - output/compliance_gap_report.json (detailed)
# - output/compliance_gap_report.txt (summary)
```

### 2. Edit Requirements (Web UI)

```bash
# Start web server (if not running)
python3 -m http.server 8083

# Open browser
http://127.0.0.1:8083/tools/lifecycle-workflow-builder.html
```

### 3. Update Operator Data

```bash
# Merge latest operator data with certifications
python3 scripts/utilities/merge_operators_with_certs.py

# Updates: tools/pay_Operators.json
```

---

## 📋 Key Files

### Configuration
- **`config/master_cert_requirements.json`** - Single source of truth for requirements

### Tools
- **`tools/lifecycle-workflow-builder.html`** - Visual requirements editor

### Reports
- **`output/compliance_gap_report.json`** - Compliance status

---

## 🎯 How It Works

1. **Define** requirements in `config/master_cert_requirements.json`
2. **Check** compliance with `generate_compliance_gap_report.py`
3. **Identify** gaps in the report
4. **Fix** gaps by executing generated SQL

---

## 🔧 Common Tasks

### Add New Requirement

Edit `config/master_cert_requirements.json` or use the web UI.

### Exclude a Division

Add to `EXCLUDED_DIVS` in scripts (currently: PA - BROOKES, 2 - LAHORE).

---

## 📚 Documentation

- **User Guides**: `docs/guides/`
- **Technical Docs**: `docs/technical/`
- **Archived**: `docs/archive/`

---

## 🛠️ Maintenance

### Update Master Requirements
```bash
# 1. Edit config/master_cert_requirements.json
# 2. Copy to tools/
cp config/master_cert_requirements.json tools/

# 3. Regenerate reports
python3 scripts/reports/generate_compliance_gap_report.py
```

### Refresh Operator Data
```bash
# 1. Export latest data from SQL Server to data/
# 2. Merge with certifications
python3 scripts/utilities/merge_operators_with_certs.py

# 3. Copy to tools/
cp generated/pay_Operators.json tools/
```

---

**Internal use only - Orion Operator Lifecycle Management System**
