# 🔧 Pizza Status Architecture - Action Items

## ✅ Completed

1. **Deleted incorrect documentation** - Removed PIZZA_STATUS_ARCHITECTURE.md that assumed pay_StatusRequirements table exists
2. **Deleted invalid SQL** - Removed get_status_requirements_with_pizza.sql (queried non-existent table)
3. **Created correct documentation** - New PIZZA_STATUS_ARCHITECTURE.md explains inference-based approach
4. **Committed and pushed** - Corrections are now in GitHub

---

## 🚧 Still Needs Work

### 1. Update Compliance Script (scripts/reports/generate_compliance_gap_report.py)

**Current Approach:**
- Uses `config/master_cert_requirements.json`
- Manually defined global requirements + division overrides

**Needed Approach:**
- Group operators by PizzaStatusID
- Analyze certifications for each pizza status group
- Determine required certs (80%+ threshold)
- Apply same requirements to all Status+Division combos sharing that pizza status

**Code Changes Needed:**

```python
# Add to imports
status_types = load_json_data(base_path / 'data' / 'pay_StatusTypes.json')
pizza_statuses = load_json_data(base_path / 'data' / 'pay_PizzaStatuses.json')

# New function: Group operators by pizza status
def group_operators_by_pizza_status(operators, status_types):
    pizza_groups = {}
    for operator in operators:
        # Find operator's status type
        status = operator.get('CurrentStatus')
        division = operator.get('DivisionID')
        
        # Look up pizza status ID
        status_type = next((st for st in status_types 
                           if st['Status'] == status and st['DivisionID'] == division), None)
        
        if status_type and status_type.get('PizzaStatusID'):
            pizza_id = status_type['PizzaStatusID']
            if pizza_id not in pizza_groups:
                pizza_groups[pizza_id] = []
            pizza_groups[pizza_id].append(operator)
    
    return pizza_groups

# New function: Infer requirements for pizza status
def infer_requirements_for_pizza_status(operators, certifications, aliases, threshold=0.80):
    if not operators:
        return set()
    
    # Get all certifications for these operators
    operator_ids = {op['Id'] for op in operators}
    pizza_certs = [c for c in certifications if c.get('OperatorID') in operator_ids]
    
    # Count cert occurrences
    cert_counts = defaultdict(int)
    for cert in pizza_certs:
        if str(cert.get('isApproved', '0')) == '1' and str(cert.get('IsDeleted', '0')) == '0':
            cert_name = normalize_cert_name(cert['Name'], aliases)
            cert_counts[cert_name] += 1
    
    # Determine required (threshold% coverage)
    total_operators = len(operators)
    required = {cert for cert, count in cert_counts.items() 
                if count / total_operators >= threshold}
    
    return required

# Modify get_required_certs_for_operator() to use pizza status
def get_required_certs_for_operator_pizza(operator, status_types, pizza_requirements, master_reqs=None):
    """
    Get required certs using pizza status grouping.
    Can optionally use master_reqs as override/supplement.
    """
    status = operator.get('CurrentStatus')
    division = operator.get('DivisionID')
    
    # Find pizza status ID
    status_type = next((st for st in status_types 
                       if st['Status'] == status and st['DivisionID'] == division), None)
    
    if not status_type or not status_type.get('PizzaStatusID'):
        return set()
    
    pizza_id = status_type['PizzaStatusID']
    required = pizza_requirements.get(pizza_id, set())
    
    # Optional: Apply master_reqs overrides if provided
    if master_reqs:
        # Check for division overrides
        div_override = master_reqs.get('division_overrides', {}).get(division, {}).get(status, {})
        if 'add_required_certs' in div_override:
            required.update(div_override['add_required_certs'])
        if 'remove_required_certs' in div_override:
            required.difference_update(div_override['remove_required_certs'])
    
    return required

# Update main() to use pizza status approach
def main():
    # Load all data
    operators = load_json_data(base_path / 'data' / 'pay_Operators.json')
    certifications = load_json_data(base_path / 'data' / 'pay_Certifications.json')
    status_types = load_json_data(base_path / 'data' / 'pay_StatusTypes.json')
    pizza_statuses = load_json_data(base_path / 'data' / 'pay_PizzaStatuses.json')
    aliases = load_json_data(base_path / 'config' / 'certification_aliases.json')
    
    # Optional: Load master_reqs for overrides
    master_reqs = None
    if (base_path / 'config' / 'master_cert_requirements.json').exists():
        master_reqs = load_json_data(base_path / 'config' / 'master_cert_requirements.json')
    
    # Group operators by pizza status
    pizza_groups = group_operators_by_pizza_status(operators, status_types)
    
    # Infer requirements for each pizza status
    pizza_requirements = {}
    for pizza_id, pizza_operators in pizza_groups.items():
        pizza_requirements[pizza_id] = infer_requirements_for_pizza_status(
            pizza_operators, certifications, aliases, threshold=0.80
        )
    
    # Generate gap report using pizza status requirements
    # ... rest of logic
```

---

### 2. Decision: Master File Strategy

**Options:**

**A) Keep as Override/Supplement** ✅ RECOMMENDED
- Use pizza status inference as base
- Keep master_cert_requirements.json for manual overrides
- Benefits:
  - Handles edge cases (TriMet forms for OR, etc.)
  - Allows manual adjustments when inference isn't perfect
  - Provides override mechanism for business requirements

**B) Pure Pizza Status Inference**
- Delete master_cert_requirements.json
- Use ONLY pizza status grouping + 80% threshold
- Benefits:
  - Simpler, fully data-driven
  - No manual maintenance needed
  - Always reflects actual operator data

**C) Generate Master File FROM Pizza Status**
- Run inference, generate master_cert_requirements.json automatically
- Allow manual edits to generated file
- Benefits:
  - Combines both approaches
  - Transparent (can see inferred requirements)
  - Can manually adjust after generation

---

### 3. HTML Editor Enhancements (Future)

**Current State:**
- Edits master_cert_requirements.json
- Shows requirements per Status+Division

**Potential Enhancements:**

1. **Pizza Status View Tab**
   - Show all ~16 unique pizza statuses
   - Display which Status+Division combos share each pizza status
   - Show inferred requirements with percentages

2. **Inference Visualization**
   - For each pizza status: show cert coverage (e.g., "Social Security Card: 95/139 = 68%")
   - Highlight certs near threshold (75-85%)
   - Allow testing different thresholds

3. **Edit by Pizza Status**
   - Add/remove requirements at pizza status level
   - Affects ALL Status+Division combos with that pizza status
   - Generate SQL to... what? (No StatusRequirements table to update)

4. **Override System**
   - Keep division-specific overrides in master file
   - Show which divisions have overrides vs. using pizza status inference

---

## 🤔 Questions to Answer

### 1. Threshold Value
- **Current:** 80% coverage = required
- **Question:** Is this the right threshold?
- **Consider:** 
  - Too high (e.g., 90%) = miss some requirements
  - Too low (e.g., 70%) = too many false positives
  - Different thresholds per pizza status?

### 2. Edge Cases
- **What about certs at 75-79% coverage?** (just below threshold)
  - Treat as "recommended" instead of "required"?
  - Show in reports with different formatting?
  
- **Pizza statuses with few operators?** (< 10 operators)
  - Fall back to manual definition?
  - Use lower threshold?
  - Warn in reports?

- **Division-specific requirements?**
  - Keep using master file overrides? (TriMet forms for OR, etc.)
  - Or encode these in database somehow?

### 3. SQL Generation
- **Current:** HTML editor generates SQL to update master file
- **Problem:** No pay_StatusRequirements table exists
- **Options:**
  - Generate SQL to update master_cert_requirements.json? (not really SQL)
  - Generate JSON diff instead?
  - Request database team to create StatusRequirements table?
  - Keep editing master file as JSON download?

---

## 📝 Recommended Next Steps

### Phase 1: Update Compliance Script ⚡ HIGH PRIORITY

1. Add pizza status grouping logic
2. Add inference calculation (80% threshold)
3. Keep master_reqs as optional override
4. Test with actual data
5. Compare output: old approach vs. pizza status approach

**Expected Result:** More consistent requirements across divisions with same pizza status

---

### Phase 2: Test & Validate 🧪

1. Run updated compliance script
2. Check sample operators:
   - Do the inferred requirements make sense?
   - Are there obvious gaps? (certs below 80% that should be required)
   - Are there false positives? (certs above 80% that shouldn't be required)
3. Compare with master file approach:
   - Which produces more accurate results?
   - Are there significant differences?

---

### Phase 3: Documentation Updates 📚

1. Update README.md with pizza status explanation
2. Update REQUIREMENTS_EDITOR guides with pizza status info
3. Document the threshold approach (80% = required)
4. Add examples showing pizza status grouping

---

### Phase 4: HTML Editor Enhancement (Optional) 🎨

1. Add pizza status visualization
2. Show inferred requirements with percentages
3. Allow threshold testing
4. Keep master file editing for overrides

---

## 🎯 Current Status

**What We Know:**
- ✅ Status + Division → PizzaStatusID mapping exists
- ✅ ~16 unique pizza statuses vs. 500+ Status+Division combos
- ✅ Requirements inferred from actual operator data (80% threshold)
- ✅ No pay_StatusRequirements table exists

**What Works:**
- ✅ Current compliance script (using master file)
- ✅ HTML editor (editing master file)
- ✅ Gap reports are generated correctly

**What Needs Improvement:**
- ⚠️ Not leveraging pizza status grouping for consistency
- ⚠️ Analyzing 500+ Status+Division combos instead of 16 pizza statuses
- ⚠️ Manual master file maintenance instead of data-driven inference

**What's Unclear:**
- ❓ Should we keep master file as override, or go pure inference?
- ❓ Is 80% the right threshold?
- ❓ How to handle edge cases (low coverage certs, small sample sizes)?
- ❓ What should HTML editor generate? (no SQL table to update)

---

*Last Updated: 2025-01-10*  
*Ready for user decision on next steps*
