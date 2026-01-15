# Operator Lifecycle Analysis Suite

## Overview
Comprehensive analysis toolkit for understanding, diagnosing, and fixing issues in the operator lifecycle process. This suite provides deep insights into operator progression, identifies bottlenecks, analyzes certification gaps, and generates actionable recommendations.

## 📊 Analysis Phases

### Phase 0: Status Progression Timeline Analysis (NEW)
**Script:** `analyze_status_progression.py`

**Purpose:** Provides real-time progression analysis using StatusTracker historical data

**Analyzes:**
- **Time-in-Status:** Actual days operators spend at each lifecycle stage
- **Bottleneck Identification:** Statuses with longest average durations
- **Division Comparison:** Compare progression speeds across all divisions
- **Certification Timing:** When certifications are completed relative to status changes
- **Operator Journeys:** Individual progression paths through the lifecycle

**Key Outputs:**
- `status_progression_analysis.json` - Complete detailed analysis with all operator journeys
- `status_progression_summary.txt` - Human-readable summary with key findings

**Critical Findings:**
- **APPROVED FOR CONTRACTING** is the #1 bottleneck (230 days average)
- **IN-SERVICE** operators remain there 115.7 days on average
- Division 12-PA has the slowest journey (203.6 days vs 3.0 days in 7-MI)
- Certification completion timing shows most certs not completed during intended status

**When to use:** Start here to understand actual timing data and identify critical delays based on real operator progression history

---

### Phase 1: Lifecycle Overview
**Script:** `phase1_lifecycle_overview.py`

**Purpose:** Provides comprehensive mapping of the entire operator lifecycle structure

**Analyzes:**
- All lifecycle statuses and their hierarchical order
- Current operator distribution across phases
- Certification requirements by status
- High-level phase coverage (Onboarding → Credentialing → DOT → Orientation → Compliance → Contracting → In-Service)

**Key Outputs:**
- Lifecycle structure diagram
- Distribution charts by phase and division
- Concentration analysis (identifies if >70% stuck in one phase)
- Health indicators

**When to use:** Start here for initial assessment or when onboarding new stakeholders

---

### Phase 2: Status Progression & Velocity Analysis
**Script:** `phase2_progression_analysis.py`

**Purpose:** Identifies operators stuck at specific stages and abnormal progression patterns

**Analyzes:**
- Where operators are currently stuck (status distribution)
- Division-level progression performance
- Early-stage accumulation (Order < 5)
- Lifecycle gaps (missing stages)
- Average stage position and spread

**Key Outputs:**
- Bottleneck identification (>15% concentration)
- Division performance rankings
- List of stuck operators
- Progression health score

**When to use:** To understand why operators aren't moving through the lifecycle

---

### Phase 3: Certification Gap Analysis
**Script:** `phase3_certification_gaps.py`

**Purpose:** Identifies missing certifications blocking operator progression

**Analyzes:**
- Required vs. optional certifications by status
- Operator certification compliance rates
- Expired certifications
- Certifications expiring soon (<30 days)
- Operators with zero certifications

**Key Outputs:**
- Compliance rates by status
- List of operators with missing required certs
- Expired certification report
- Operators at risk (expiring soon)

**When to use:** When operators are stuck and you suspect certification issues

---

### Phase 4: Bottleneck & Process Issue Identification
**Script:** `phase4_bottleneck_analysis.py`

**Purpose:** Identifies systemic bottlenecks and structural process issues

**Analyzes:**
- Volume bottlenecks (>25% concentration at single status)
- Division-specific bottleneck patterns
- Process gaps (missing lifecycle stages)
- Certification-driven bottlenecks (stages with heavy cert requirements)
- Risk scoring for problematic stages

**Key Outputs:**
- Root cause analysis for each bottleneck
- Division issue summary
- Process gap report
- Prioritized issue list

**When to use:** To understand WHY bottlenecks exist and what's causing them

---

### Phase 5: Actionable Recommendations Generator
**Script:** `phase5_recommendations.py`

**Purpose:** Synthesizes all analysis into prioritized, actionable recommendations

**Generates:**
- Critical priority actions (immediate)
- High priority actions (1-2 weeks)
- Medium priority actions (1 month)
- Specific action plans for each issue
- Impact and effort estimates
- Expected outcomes
- Measurement strategy

**Key Outputs:**
- Comprehensive recommendations document
- Executive summary with priorities
- Implementation roadmap
- Success metrics

**When to use:** After running all other phases, to create action plan

---

## 🚀 Quick Start

### Run Complete Analysis
```bash
cd /home/eurorescue/Desktop/Orion_Operator_Lifecycle_Automation
python3 scripts/run_full_analysis.py
```

This master script runs all 5 phases in sequence and generates a unified executive report.

### Run Individual Phase
```bash
# Example: Run just the progression analysis
python3 scripts/phase2_progression_analysis.py

# Or make it executable and run directly
./scripts/phase2_progression_analysis.py
```

---

## 📁 Data Requirements

The scripts expect the following data files in the `data/` directory:

### Required Files:
- `pay_Operators.txt` - Operator records (JSON array)
- `pay_Operators_sample_across_statuses.txt` - Sample operators across lifecycle (JSON array)
- `pay_StatusTypes.txt` - Status definitions with OrderID (JSON array)
- `pay_PizzaStatuses.txt` - High-level status categories (JSON array)

### Optional Files (enhance analysis):
- `pay_Certifications.txt` - Operator certifications (JSON array)
- `pay_CertTypes.txt` - Certification requirements by status (JSON array)

### Data Schema:

**pay_Operators fields:**
```json
{
  "Id": "GUID",
  "FirstName": "string",
  "LastName": "string",
  "DivisionID": "string (e.g., '7 - MI')",
  "StatusName": "string",
  "CurrentStatus": "string",
  "StatusOrderSequence": "integer",
  "PizzaStatus": "string (high-level category)"
}
```

**pay_StatusTypes fields:**
```json
{
  "Id": "GUID",
  "Status": "string (status name)",
  "OrderID": "integer (progression order)",
  "DivisionID": "string",
  "PizzaStatusID": "GUID",
  "IsOperator": "boolean"
}
```

---

## 🎯 Common Use Cases

### 1. Monthly Health Check
```bash
# Run full analysis to track lifecycle health over time
python3 scripts/run_full_analysis.py
```

### 2. Bottleneck Investigation
```bash
# Run phases 2 and 4 to identify and diagnose bottlenecks
python3 scripts/phase2_progression_analysis.py
python3 scripts/phase4_bottleneck_analysis.py
```

### 3. Certification Compliance Audit
```bash
# Run phase 3 to check certification compliance
python3 scripts/phase3_certification_gaps.py
```

### 4. New Stakeholder Briefing
```bash
# Run phase 1 for high-level overview
python3 scripts/phase1_lifecycle_overview.py
```

### 5. Action Plan Creation
```bash
# Run full analysis, focusing on phase 5 recommendations
python3 scripts/run_full_analysis.py
# Then review: generated/comprehensive_recommendations.txt
```

---

## 📈 Interpreting Results

### Health Indicators

**✓ Healthy:**
- Distribution spread across multiple stages
- <25% concentration at any single status
- <30% of operators in early stages (Order < 5)
- >20% reaching final stages (Order >= 12)
- All lifecycle stages have operators
- Certification compliance >90%

**⚠️ Warning:**
- 25-50% concentration at single status
- 30-50% in early stages
- 10-20% reaching final stages
- Some lifecycle gaps
- Certification compliance 70-90%

**🚨 Critical:**
- >50% concentration at single status
- >50% in early stages
- <10% reaching final stages
- Multiple lifecycle gaps
- Certification compliance <70%
- Multiple expired certifications

---

## 🔧 Troubleshooting

### Issue: "No data found"
**Solution:** Ensure data files exist in `data/` directory and are valid JSON

### Issue: "KeyError" on field names
**Solution:** Check that your data files match the expected schema (see Data Schema section)

### Issue: Analysis shows all operators at one status
**Solution:** You may need to run the SQL query `get_random_operators_across_statuses.sql` to get a diverse sample

### Issue: No certification analysis
**Solution:** Ensure `pay_CertTypes.txt` and `pay_Certifications.txt` files exist with proper mappings

---

## 📊 Output Files

All analysis outputs are saved to the `generated/` directory:

- `phase1_lifecycle_overview_report.txt` - Lifecycle structure and distribution
- `comprehensive_recommendations.txt` - Prioritized action plan
- Additional reports generated by each phase

---

## 🔄 Workflow

```
1. Data Collection
   ↓
2. Run Full Analysis (run_full_analysis.py)
   ↓
3. Review Executive Summary
   ↓
4. Read Detailed Recommendations (generated/comprehensive_recommendations.txt)
   ↓
5. Prioritize Actions
   ↓
6. Implement Fixes
   ↓
7. Monitor Progress
   ↓
8. Re-run Analysis (monthly) → Loop back to step 2
```

---

## 🎓 Understanding the Operator Lifecycle

### Typical Flow:
1. **REGISTRATION** (Order 1) - Initial sign-up
2. **ONBOARDING** (Order 2) - Welcome and initial setup
3. **CREDENTIALING** (Order 3) - Background checks and verifications
4. **DOT SCREENING** (Order 4) - Department of Transportation screening
5. **ORIENTATION** (Order 5-7) - Training and orientation sessions
6. **COMPLIANCE REVIEW** (Order 8-10) - Final compliance checks
7. **CONTRACTING** (Order 11-12) - Contract finalization
8. **VEHICLE LEASING** (Order 13) - Vehicle assignment (if needed)
9. **IN-SERVICE** (Order 13-14) - Active and working

### Common Bottlenecks:
- **Onboarding** - Too many new operators, insufficient processing capacity
- **Credentialing** - Background check delays, missing documentation
- **DOT Screening** - Medical exam delays, failed tests
- **Compliance Review** - Certification verification delays
- **Contracting** - Legal review bottlenecks

---

## 💡 Best Practices

1. **Run analysis monthly** to track trends
2. **Compare division performance** to identify best practices
3. **Focus on critical priorities first** - don't try to fix everything at once
4. **Measure impact** - track metrics before and after changes
5. **Share findings** with all stakeholders
6. **Iterate** - continuous improvement is key

---

## 🛠️ Customization

### Adjusting Thresholds:
Edit the threshold constants in each script:
- `BOTTLENECK_THRESHOLD` in phase4 (default: 0.25 = 25%)
- Early stage threshold in phase2 (default: Order < 5)

### Adding Custom Metrics:
Each phase script can be extended with additional analysis functions. Follow the existing pattern:
```python
def analyze_custom_metric(self):
    print("\n" + "=" * 80)
    print("[X/Y] CUSTOM ANALYSIS")
    print("=" * 80)
    # Your analysis code here
```

---

## 📞 Support

For issues, questions, or enhancement requests, refer to the script comments or review the generated output files for diagnostic information.

---

## 📝 Version History

**v1.0** (2026-01-09)
- Initial release with 5 comprehensive analysis phases
- Master runner script for unified execution
- Detailed recommendations engine
- Support for multi-division analysis
- Certification compliance tracking

---

## 🎯 Success Metrics

After implementing recommendations, track:
- **Average days per stage** - should decrease
- **Bottleneck concentration** - should drop below 25%
- **Early stage percentage** - should drop below 30%
- **Final stage completion rate** - should increase above 20%
- **Certification compliance** - should increase above 90%
- **Division variance** - should decrease (more standardization)

Run monthly analyses to track these metrics over time.
