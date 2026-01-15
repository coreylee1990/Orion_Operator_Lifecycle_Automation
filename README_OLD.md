# 🎯 Orion Operator Lifecycle Automation

## Quick Navigation

### 📖 Read These First
1. **[DATA_SCHEMA.md](DATA_SCHEMA.md)** ← **START HERE for Data Structure**
   - Complete field descriptions for all data files
   - Real data schema from Orion database
   - Certification requirements analysis

2. **[COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)**
   - Executive summary of findings
   - Critical bottlenecks identified
   - Immediate action items

3. **[ANALYSIS_SUITE_README.md](ANALYSIS_SUITE_README.md)**
   - Detailed technical documentation
   - How to use each analysis phase
   - Troubleshooting guide

---

## 🎯 Key Analysis Tools

### 1. **Status Progression Analysis** (NEW - Real Timeline Data)
```bash
# Analyze operator progression through lifecycle with actual timing data
python3 scripts/analyze_status_progression.py

# View results
cat generated/status_progression_summary.txt
```

**Output:** 
- **Time-in-Status:** How long operators spend at each lifecycle stage
- **Bottlenecks:** Statuses where operators get stuck longest (e.g., APPROVED FOR CONTRACTING: 230 days avg)
- **Division Comparison:** Compare progression speed across divisions
- **Cert Timing:** When certifications are completed relative to status changes

### 2. **Certification Requirements Analysis** (Real Data)
```bash
# Analyze what certifications are required for each lifecycle status
python3 scripts/analyze_cert_requirements_by_status.py

# View results
cat generated/certification_requirements_analysis.txt
```

**Output:** Identifies CRITICAL PATH certifications and requirements at each status based on real adoption patterns (80%+ = required, 50-79% = common, <50% = optional)

### 3. **Complete 5-Phase Analysis**
```bash
# Run comprehensive lifecycle analysis
python3 scripts/run_full_analysis.py

# View results
cat generated/comprehensive_recommendations.txt
```

---

## 📊 Real Data Overview

### Current Data (As of Latest Export)
- **81 Operators** sampled across lifecycle statuses
- **92 Operator Fields** including demographics, status, licensing, integration IDs
- **4,731 Certification Records** (100 unique certification types)
- **200 Status Progression Events** from StatusTracker (33 operators tracked)
- **5 Critical Path Certifications** identified for progression
- **75 Certification Fields** per record (see DATA_SCHEMA.md)

### Key Operator Fields
- **ID** - Primary key (GUID)
- **StatusID** - Links to pay_StatusTypes (current lifecycle stage)
- **StatusName** - Human-readable status ("REGISTRATION", "IN-SERVICE", etc.)
- **OrderID** - Lifecycle progression order (1-14)
- **DivisionID** - Branch/location ("PA - BROOKES", "10 - OR", etc.)
- **Demographics** - FirstName, LastName, Email, Mobile, Address, Birthdate
- **Licensing** - LicenseNbr, LicenseState, LicenseExp, LicensePhoto
- **Integration** - AspNetUserId, UberDriverId, ProviderID, ClientID

### Status Distribution (Sample)
- Multiple lifecycle statuses represented
- Filtered for active operators (isDeleted = 0)
- Spread across divisions for analysis coverage

---

## 📦 What's Included

### ✅ Real Data Files (data/)
- `pay_Operators.txt/json` - 81 operators with 92 complete fields from Orion database
- `pay_Certifications.txt/json` - 4,731 certification records with 75 fields
- `pay_CertTypes.txt/json` - Certification type definitions
- `pay_StatusTypes.txt/json` - Status type definitions
- `pay_PizzaStatuses.txt/json` - Pizza status workflow definitions
- `rawOperators.json` - Raw operator data export
- `operators_100_lifecycle.json` - Balanced sample across lifecycle stages

### ✅ Analysis Scripts (scripts/)
- **Status Progression Analysis:** (NEW)
  - `analyze_status_progression.py` - Time-in-status, bottlenecks, division comparison
  - `convert_status_tracker_to_json.py` - Convert StatusTracker exports to JSON
  - `generate_status_tracker_query.py` - Generate SQL to fetch progression history

- **Certification Analysis:** 
  - `analyze_cert_requirements_by_status.py` - Detect required certs by lifecycle status
  - `generate_cert_query.py` - Generate SQL to fetch all certifications
  - `convert_cert_csv_to_json.py` - Convert cert exports to JSON

- **Lifecycle Analysis (5 Phases):**
  - `phase1_lifecycle_overview.py` - Lifecycle structure & distribution
  - `phase2_progression_analysis.py` - Stuck operators & velocity
  - `phase3_certification_gaps.py` - Missing/expired certifications
  - `phase4_bottleneck_analysis.py` - Process bottlenecks
  - `phase5_recommendations.py` - Actionable recommendations
  - `run_full_analysis.py` - Master orchestrator

### ✅ SQL Queries (scripts/)
- `get_operator_certifications.sql` - Fetch all certs for 168 operators
- `get_random_operators_across_statuses.sql` - Sample operators by status
- `get_status_cert_requirements.sql` - Get cert requirements by status

### ✅ Complete Documentation
- Data schema with real field descriptions
- Analysis findings and recommendations
- Technical documentation
- Quick start guides

---

## � Key Insights from Real Data
**CRITICAL BOTTLENECKS IDENTIFIED (StatusTracker Analysis):**
- **APPROVED FOR CONTRACTING:** 230 days average (Step 12) - CRITICAL DELAY
- **IN-SERVICE:** 115.7 days average (Step 5) - Operators stuck after activation
- **ORIENTATION:** 24.6 days average (Step 5) - Training delays
- **ONBOARDING:** 15.2 days average (Step 2) - Range 0-409 days (high variance)

**Division Performance:**
- **Slowest:** 12 - PA (203.6 days average journey)
- **Fastest:** 7 - MI (3.0 days average journey)
- **Most Efficient:** 3 - TX (30 days, 11 stages completed)

**Certification Completion Challenge:**
- Most required certifications show 0% completion DURING their intended status
- Suggests certifications may be uploaded in batch or tracked elsewhere
- Requires further investigation of cert timestamp accuracy
**Current Status Distribution (168 Operators):**
- **IN-SERVICE:** 36 operators (21.4%) ✓ Target state achieved
- **ONBOARDING:** 31 operators (18.5%) - Healthy pipeline
- **DOT SCREENING:** 25 operators (14.9%) - W9 is critical here (80% adoption)
- **COMPLIANCE REVIEW:** 15 operators (8.9%)
- **Other stages:** 61 operators (36.3%) across 9 other statuses

**Critical Path Certifications Identified:**
1. **W9** - Required at DOT SCREENING (80% adoption, Order 4)
2. **DOT Drug & Alcohol Policy** - Required at SBPC (80%, Order 10)
3. **DOT Pre-Contracting Drug/Alc Screen** - Required at SBPC (80%, Order 10)
4. **Vehicle Lease Agreement** - Required for LEASING (100%, Order 13)
5. **Social Security Card** - Required throughout (83.3% at IN-SERVICE)

**Analysis Results:**
- ✅ Good distribution across lifecycle (not bottlenecked)
- ✅ 100 unique certification types identified
- ✅ 4,731 certification records analyzed
- ✅ Data-driven requirements based on real adoption patterns

---

## 📊 Analysis Capabilities

| What | How | Output |
|------|-----|--------|
| **Overall Health** | `phase1_lifecycle_overview.py` | Distribution charts, health score |
| **Find Stuck Operators** | `phase2_progression_analysis.py` | Bottleneck list, velocity metrics |
| **Check Certifications** | `phase3_certification_gaps.py` | Compliance rates, missing certs |
| **Root Causes** | `phase4_bottleneck_analysis.py` | Why operators are stuck |
| **What to Do** | `phase5_recommendations.py` | Prioritized action plans |

---

## 🎯 Next Steps

1. Read **[COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)** (5 min)
2. Run `python3 scripts/run_full_analysis.py` (2 min)
3. Review `generated/comprehensive_recommendations.txt` (10 min)
4. Implement critical priority actions
5. Re-run monthly to track improvements

---

**Everything is ready to go. Start with [COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)!**
