# �� Quick Start Guide

## Overview
This system manages operator certification requirements using **pizza status grouping**. Requirements are defined directly from the database's `pay_CertTypes` table, where each certification type declares its `PizzaStatusID`.

## 🎯 Three Main Workflows

### 1️⃣ Generate Requirements (from Database)
Pull the latest cert type requirements from the database:

```bash
python3 scripts/generate_pizza_status_requirements.py
```

**Output:** `data/pay_PizzaStatusRequirements.json` (15 pizza statuses, ~141 certs)

### 2️⃣ Check Compliance Gaps
Analyze which operators are missing required certifications:

```bash
python3 scripts/reports/generate_compliance_gap_report.py
```

**Outputs:**
- `generated/compliance_gap_report.json` (detailed data)
- `generated/compliance_gap_report.txt` (human-readable)

**Current Results:**
- 79 operators analyzed
- 21.5% compliant, 78.5% non-compliant
- 1,154 missing certifications identified

### 3️⃣ Edit Requirements Visually
Use the drag-and-drop HTML editor:

```bash
# Open in browser
xdg-open tools/lifecycle-workflow-builder.html
```

**Features:**
- Visual status workflow
- Drag-drop certifications
- Save changes to JSON
- Generate SQL (reference)

## 📁 Key Files

### Data
- `data/pay_CertTypes.json` - Certification types (1,322 types) **[SOURCE OF TRUTH]**
- `data/pay_PizzaStatusRequirements.json` - Generated requirements (15 pizza statuses)
- `data/pay_Operators.json` - Operator data (81 operators)
- `data/pay_Certifications.json` - What certs operators have (4,430 records)
- `data/pay_StatusTypes.json` - Status+Division → PizzaStatusID mapping (973 mappings)

### Config
- `config/certification_aliases.json` - Cert name normalization (7 aliases)

### Scripts
- `scripts/generate_pizza_status_requirements.py` - **Main generator**
- `scripts/reports/generate_compliance_gap_report.py` - Gap analysis

### Tools
- `tools/lifecycle-workflow-builder.html` - Visual editor

## 🏗️ Architecture

```
CertType → PizzaStatusID → Requirements
     ↓
Operator → Status+Division → PizzaStatusID → Required Certs
```

**Key Insight:** Each certification type in `pay_CertTypes` has a `PizzaStatusID` field that directly declares which pizza status it belongs to. No inference needed!

## 📊 Pizza Status Examples

| Pizza Status | Certs | Example Requirements |
|--------------|-------|---------------------|
| Onboarding | 32 | Drivers License, SSN, CPR, CTAA |
| DOT Screening | 21 | DOT Physical, Drug Screen, CCF |
| Credentialing | 14 | Background Check, MVR |
| Orientation | 15 | Behind-the-Wheel, WC Securement |
| Contracting | 8 | Service Agreement, Workers Comp |

## 🔧 Common Tasks

### Update requirements from database
```bash
python3 scripts/generate_pizza_status_requirements.py
```

### Check specific operator compliance
Open `generated/compliance_gap_report.txt` and search by name.

### Add/remove certifications
1. Open HTML editor: `xdg-open tools/lifecycle-workflow-builder.html`
2. Drag certification to/from status
3. Click "Save Changes"
4. Replace `data/pay_PizzaStatusRequirements.json`
5. Refresh to see changes

### See which operators need specific cert
```bash
grep -A 5 "Missing:" generated/compliance_gap_report.txt | grep "Your Cert Name"
```

## 🎓 Understanding Pizza Statuses

**What is a Pizza Status?**
A grouping mechanism that consolidates multiple Status+Division combinations into a single certification requirement set.

**Example:**
- "ONBOARDING" status exists in 30 different divisions
- All map to Pizza Status "Onboarding" (ID: D884F3D1...)
- One set of 32 required certs applies to all 30 combinations
- Much easier than managing 30 separate requirement lists!

**Benefits:**
- Consistency across divisions
- Easier maintenance (manage ~16 pizza statuses vs 500+ status+div combos)
- Database-driven (requirements defined in cert types)
- Accurate compliance tracking

## 📈 Current Status

- **15 Pizza Statuses** with requirements
- **141 Total Required Certifications**
- **79 Operators** in system
- **78.5% Non-Compliant** (62 operators need certs)
- **1,154 Missing Certifications** identified

## 🆘 Troubleshooting

**Script fails to run?**
```bash
# Ensure you're in the project root
cd /home/eurorescue/Desktop/Orion_Operator_Lifecycle_Automation

# Check Python version (needs 3.6+)
python3 --version
```

**HTML editor won't load data?**
- Check browser console (F12)
- Verify `data/pay_PizzaStatusRequirements.json` exists
- Try hard refresh (Ctrl+Shift+R)

**Compliance report shows 0 operators?**
- Check `data/pay_Operators.json` exists
- Verify excluded divisions in script

## 📚 Documentation

- [CERTTYPE_ARCHITECTURE_COMPLETE.md](CERTTYPE_ARCHITECTURE_COMPLETE.md) - Full architecture details
- [PIZZA_STATUS_ARCHITECTURE.md](PIZZA_STATUS_ARCHITECTURE.md) - Pizza status explanation
- [README.md](README.md) - Project overview

## 🎯 Next Steps

1. **Review compliance report** - Identify operators with most gaps
2. **Prioritize certifications** - Focus on most commonly missing certs
3. **Update cert types** - Keep database current with business requirements
4. **Monitor progress** - Re-run compliance report regularly

---

**Need help?** Check the full documentation or examine the generated reports for detailed insights.
