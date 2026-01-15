# Orion Operator Lifecycle Automation

**Data-driven operator certification requirements using Pizza Status inference system.**
cd /home/eurorescue/Desktop/Orion_Operator_Lifecycle_Automation
python3 -m http.server 8000
---

## 🍕 Pizza Status Requirements System

This system uses **inference** to determine certification requirements by grouping operators by their **PizzaStatusID**. 

### How It Works

1. **Group:** Operators are grouped by PizzaStatusID (~16 unique groups)
2. **Analyze:** Count which certifications those operators have
3. **Infer:** Certs with 80%+ coverage = required
4. **Apply:** Same requirements for all Status+Division combos sharing that pizza status

### Benefits

- **Data-Driven:** Requirements reflect actual operator data
- **Consistent:** Same pizza status = same requirements across divisions
- **Efficient:** Manage 16 pizza statuses instead of 500+ Status+Division combinations
- **Accurate:** Larger sample sizes (100+ operators per pizza status)

---

## 📁 Project Structure

```
Orion_Operator_Lifecycle_Automation/
├── data/                          # Data files
│   ├── pay_CertTypes.json                # All cert types with PizzaStatusID + DivisionID
│   ├── pay_PizzaStatusRequirements.json  # Inferred requirements (source of truth)
│   ├── pay_StatusTypes.json              # Status → PizzaStatusID mapping
│   ├── pay_Operators.json                # Operator data
│   └── pay_Certifications.json           # Certification data
├── config/                        # Configuration
│   └── certification_aliases.json        # Cert name normalization
├── tools/                         # User-facing tools
│   └── lifecycle-workflow-builder.html   # Visual requirements editor with division filtering
├── scripts/                       # Automation scripts
│   ├── generate_pizza_status_requirements.py  # Generate from inference
│   └── reports/
│       └── generate_compliance_gap_report.py  # Gap analysis
├── sql/                           # SQL queries for database
├── docs/                          # Documentation
│   ├── DIVISION_FILTERING_ARCHITECTURE.md     # Division filtering system (NEW)
│   └── WORKFLOW_BUILDER_CHANGELOG.md          # Version history
├── generated/                     # Generated reports
└── external/                      # External data sources
```

---

## 🚀 Quick Start

### 1. Generate Requirements from Data

```bash
# Analyze operator data and infer requirements
python3 scripts/generate_pizza_status_requirements.py

# Output: data/pay_PizzaStatusRequirements.json
```

### 2. View Operator Compliance

```bash
# Generate compliance gap report
python3 scripts/reports/generate_compliance_gap_report.py

# Output:
# - generated/compliance_gap_report.json (detailed)
# - generated/compliance_gap_report.txt (summary)
```

### 3. Edit Requirements (Visual Editor)

1. Start web server: `python3 -m http.server 8000`
2. Open browser: `http://localhost:8000/tools/lifecycle-workflow-builder.html`
3. **Filter by Division**: Use division dropdown to view division-specific requirements
4. Drag and drop certifications to statuses (Edit Requirements mode)
5. Click "Save Changes"
6. Download `pay_PizzaStatusRequirements.json`
7. Replace file in `data/` directory
8. Refresh browser

**New Feature**: Main page now includes division filtering that shows:
- Operators filtered by selected division
- Certifications filtered by division using CertTypes → PizzaStatusID architecture
- See [docs/DIVISION_FILTERING_ARCHITECTURE.md](docs/DIVISION_FILTERING_ARCHITECTURE.md) for details

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

### Key Documents
- **[DIVISION_FILTERING_ARCHITECTURE.md](docs/DIVISION_FILTERING_ARCHITECTURE.md)** - Division filtering system using CertTypes table
- **[WORKFLOW_BUILDER_CHANGELOG.md](docs/WORKFLOW_BUILDER_CHANGELOG.md)** - Version history and updates

### Additional Documentation
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
