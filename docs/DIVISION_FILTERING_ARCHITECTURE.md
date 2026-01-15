# Division Filtering Architecture

**Main page division filtering using CertTypes → PizzaStatusID → Pizza Status Requirements architecture.**

---

## Overview

The Control Center main page allows filtering operators and certifications by division. This uses a direct database query approach that matches the underlying data structure.

### Key Features

- **Division Dropdown**: Filter selector in Control Center panel
- **Operator Filtering**: Shows only operators from selected division
- **Certification Filtering**: Shows only certifications for selected division using actual CertTypes data
- **All Divisions Mode**: Shows all operators and all certifications across all divisions
- **Dynamic Division Display**: Status containers show contextual division information

---

## Architecture Flow

```
User selects division filter (e.g., "12 - PA")
    ↓
mainDivisionFilter variable updated
    ↓
renderWorkflow() called
    ↓
For each lifecycle status:
    ↓
    getRequiredCertsForStatus(statusName)
        ↓
        Step 1: Find pizza statuses with status_mappings[] matching:
            - mapping.status === statusName (e.g., "ONBOARDING")
            - mapping.division === mainDivisionFilter (if not 'ALL')
        ↓
        Step 2: Get pizza_status_id values from matching pizza statuses
        ↓
        Step 3: Query pay_CertTypes.json for cert types where:
            - CertType.PizzaStatusID matches one of the pizza status IDs
            - CertType.DivisionID contains selected division (e.g., "12")
        ↓
        Step 4: Return unique certification names
    ↓
Display filtered operators and certifications
```

---

## Data Structure

### pay_CertTypes.json (1,322 cert types)
```json
{
  "CertID": "...",
  "Certification": "Drivers License",
  "PizzaStatusID": "D884F3D1-...",
  "DivisionID": "12 - PA"
}
```

### pay_PizzaStatusRequirements.json (15 pizza statuses)
```json
{
  "D884F3D1-...": {
    "pizza_status_id": "D884F3D1-...",
    "pizza_status_name": "Onboarding",
    "is_operator": true,
    "status_mappings": [
      {
        "status": "ONBOARDING",
        "division": "12 - PA",
        "order": "2"
      }
    ],
    "required_certifications": [...]
  }
}
```

---

## Implementation

### Variables

```javascript
let mainDivisionFilter = 'ALL';  // Current division filter
let certTypes = [];              // Raw cert types from database
let pizzaStatusRequirements = {};// Pizza status definitions
let operators = [];              // Operator data
```

### Division Filter Dropdown

Located in Control Center panel:

```html
<select id="mainDivisionFilter" onchange="handleMainDivisionFilter()">
    <option value="ALL">🌐 All Divisions</option>
    <option value="2 - IL">2 - IL</option>
    <option value="3 - TX">3 - TX</option>
    <option value="5 - CA">5 - CA</option>
    <option value="6 - FL">6 - FL</option>
    <option value="7 - MI">7 - MI</option>
    <option value="8 - OH">8 - OH</option>
    <option value="10 - OR">10 - OR</option>
    <option value="11 - GA">11 - GA</option>
    <option value="12 - PA">12 - PA</option>
</select>
```

**Divisions Included**: All divisions with operators + 2-IL and 5-CA (always shown even if no operators)

**Divisions Excluded**: PA-BROOKES, 2-LAHORE (not in requirements)

### Core Filtering Function

```javascript
function getRequiredCertsForStatus(statusName) {
    const certs = new Set();
    
    // Step 1: Find pizza statuses that map to this lifecycle status
    const relevantPizzaStatusIds = new Set();
    Object.values(pizzaStatusRequirements).forEach(pizzaStatus => {
        const matchingMappings = (pizzaStatus.status_mappings || []).filter(mapping => {
            if (mapping.status === statusName) {
                if (mainDivisionFilter === 'ALL') {
                    return true;
                } else {
                    return mapping.division === mainDivisionFilter;
                }
            }
            return false;
        });
        
        if (matchingMappings.length > 0) {
            relevantPizzaStatusIds.add(pizzaStatus.pizza_status_id);
        }
    });
    
    // Step 2: Get cert types with these pizza status IDs and matching division
    certTypes.forEach(certType => {
        const pizzaStatusId = certType.PizzaStatusID;
        const divisionId = certType.DivisionID;
        const certName = certType.Certification;
        
        if (pizzaStatusId && relevantPizzaStatusIds.has(pizzaStatusId)) {
            if (mainDivisionFilter === 'ALL') {
                certs.add(certName);
            } else {
                // Check if division matches (handle "12 - PA" and "12-PA" formats)
                if (divisionId && divisionId.includes(mainDivisionFilter.replace(' - ', '-').split('-')[0])) {
                    certs.add(certName);
                }
            }
        }
    });

    return Array.from(certs).sort();
}
```

### Operator Filtering

```javascript
function renderWorkflow() {
    currentWorkflow.forEach((flowStep, index) => {
        const statusName = flowStep.status;
        
        // Filter operators by status
        let operatorsInStep = operators.filter(op => 
            op.StatusName === statusName || 
            (op.StatusName && op.StatusName.toUpperCase() === statusName.toUpperCase())
        );
        
        // Apply division filter
        if (mainDivisionFilter !== 'ALL') {
            operatorsInStep = operatorsInStep.filter(op => 
                op.DivisionID === mainDivisionFilter
            );
        }
        
        // ... render operators and certifications
    });
}
```

### Dynamic Division Display

Status container headers show contextual division information:

```javascript
// Get divisions dynamically based on filter
let divisionsText;
if (mainDivisionFilter === 'ALL') {
    // Show all divisions that have this status in pizza status requirements
    const divisionsForStatus = new Set();
    Object.values(pizzaStatusRequirements).forEach(pizzaStatus => {
        (pizzaStatus.status_mappings || []).forEach(mapping => {
            if (mapping.status === statusName) {
                divisionsForStatus.add(mapping.division);
            }
        });
    });
    const divList = Array.from(divisionsForStatus).sort();
    divisionsText = divList.length > 0 ? divList.join(', ') : 'No divisions';
} else {
    // Show only the filtered division
    divisionsText = mainDivisionFilter;
}
```

**Result**:
- **All Divisions**: "Divisions: 10-OR, 11-GA, 12-PA, 3-TX, 7-MI"
- **Filtered**: "Division: 12 - PA"

---

## Division-Specific Certification Counts

### Division 12 - PA (Operator Pizza Statuses)

```
ONBOARDING: 5 certs
├─ Drivers License
├─ Driver's License_BACKSIDE
├─ Social Security Card
├─ Defensive Driving
└─ CTAA Passenger Assistance

DOT SCREENING: 5 certs
├─ CCF
├─ Drug & Alcohol Orientation
├─ Drug and Alcohol Policy
├─ NON DOT Pre Employment Donor Pass
└─ NON-DOT Pre-Contract Drug/Alc Screen

ORIENTATION: 4 certs
├─ Orientation-Behind the Wheel
├─ Orientation-Big Star Safety and Service
├─ UBER WAV APP
└─ WAV WC Securement

CREDENTIALING: 2 certs
├─ BackgroundCheck
└─ MVR

IN-SERVICE: 6 certs
├─ Annual Insurance Card
├─ Business Formation
├─ Vehicle Inspection Client-UBERWAV
├─ Vehicle Registration
├─ Vehicle State Safety Inspection
└─ WAV Vehicle Modification QA

CONTRACTING: 3 certs
├─ Service Agreement
├─ Service Agreement-Schedule A
└─ Worker's Comp Coverage Waiver

VEHICLE LEASING: 4 certs
├─ Lease Inspection
├─ VEHICLE LEASE INSPECTION
├─ Vehicle Lease Agreement
└─ Vehicle Lease Inspection

COMPLIANCE REVIEW: 1 cert
└─ COMPLIANCE REVIEW

Total: 30 certifications across 8 operator pizza statuses
```

### Other Divisions

Each division has its own set of certifications based on:
- Which pizza statuses are active for that division
- Which cert types in pay_CertTypes.json have that DivisionID
- The pizza status → lifecycle status mappings

---

## Data Loading

### Required Files

1. **pay_CertTypes.json** (../data/pay_CertTypes.json)
   - All certification types with PizzaStatusID and DivisionID
   - 1,322 total cert types

2. **pay_PizzaStatusRequirements.json** (../data/pay_PizzaStatusRequirements.json)
   - Pizza status definitions with status_mappings
   - 15 pizza statuses

3. **pay_Operators.json** (tools/pay_Operators.json)
   - Operator data with DivisionID and StatusName
   - Used for operator filtering

### Load Sequence

```javascript
async function loadData() {
    // 1. Load operators
    const operatorsResponse = await fetch('pay_Operators.json' + cacheBuster);
    operators = await operatorsResponse.json();
    
    // 2. Load cert types (NEW - CRITICAL)
    const certTypesResponse = await fetch('../data/pay_CertTypes.json' + cacheBuster);
    certTypes = await certTypesResponse.json();
    
    // 3. Load pizza status requirements
    const pizzaReqResponse = await fetch('../data/pay_PizzaStatusRequirements.json' + cacheBuster);
    pizzaStatusRequirements = await pizzaReqResponse.json();
    
    // 4. Populate division filter
    populateMainDivisionFilter();
    
    // 5. Render workflow
    renderWorkflow();
}
```

---

## Why This Architecture?

### Previous Approach (Incorrect)

❌ Used `pizzaStatusRequirements.required_certifications[]` array  
❌ Array had generic certs without proper division association  
❌ Division field on certs didn't match mainDivisionFilter format  
❌ Result: 0 certs when filtering by division

### Current Approach (Correct)

✅ Queries `pay_CertTypes.json` directly (source of truth)  
✅ Uses actual database DivisionID field  
✅ Matches PizzaStatusID to connect certs → pizza status → lifecycle status  
✅ Result: Accurate cert counts matching database query

### Benefits

- **Accuracy**: Matches actual database contents
- **Performance**: Direct table query (no complex lookups)
- **Maintainability**: Single source of truth (CertTypes table)
- **Consistency**: Same logic as Python queries
- **Scalability**: Handles all 1,322 cert types efficiently

---

## Verification Query

To verify division filtering is working correctly:

```python
import json

cert_types = json.load(open('data/pay_CertTypes.json'))
pizza_statuses = json.load(open('data/pay_PizzaStatusRequirements.json'))

# Get division 12 cert types with PizzaStatusID
div_12 = [ct for ct in cert_types 
          if ct.get('DivisionID') and '12' in ct['DivisionID'] 
          and ct.get('PizzaStatusID')]

# Group by pizza status
ps_map = {}
for ct in div_12:
    pid = ct['PizzaStatusID']
    if pid not in ps_map:
        ps_map[pid] = {'certs': [], 'name': None, 'is_operator': False}
    ps_map[pid]['certs'].append(ct['Certification'])
    if pid in pizza_statuses:
        ps_map[pid]['name'] = pizza_statuses[pid].get('pizza_status_name')
        ps_map[pid]['is_operator'] = pizza_statuses[pid].get('is_operator', False)

# Display operator pizza statuses
for pid, data in sorted(ps_map.items(), key=lambda x: x[1]['name'] or ''):
    if data['is_operator']:
        print(f"{data['name']}: {len(data['certs'])} certs")
```

**Expected Output for Division 12**:
- Total cert types: 40
- Operator pizza statuses: 8
- Total certs: 30

---

## Troubleshooting

### No certifications showing for division

**Check**:
1. Are cert types loaded? (`console.log(certTypes.length)`)
2. Do cert types have PizzaStatusID? (`certTypes.filter(ct => ct.PizzaStatusID).length`)
3. Does division format match? (`certType.DivisionID` should contain division number)
4. Are pizza status mappings present? (`pizzaStatusRequirements[id].status_mappings`)

### Wrong certification count

**Check**:
1. Browser console logging shows which certs are being added
2. Compare with Python query results
3. Verify PizzaStatusID matches between CertTypes and PizzaStatusRequirements
4. Check division format matching logic

### Division not appearing in dropdown

**Check**:
1. Does division have operators? (`operators.filter(op => op.DivisionID === '12 - PA')`)
2. Is division in hardcoded list? (2-IL and 5-CA are always shown)
3. `populateMainDivisionFilter()` called on page load?

---

## Future Enhancements

### Potential Improvements

- **Division-specific stats**: Show cert completion percentage by division
- **Division comparison**: Side-by-side comparison of requirements
- **Export filtered data**: CSV/JSON export for specific division
- **Division color coding**: Visual indicators for different divisions
- **Multi-division filter**: Select multiple divisions simultaneously

### Performance Optimization

- **Caching**: Cache cert lookups by division to avoid repeated queries
- **Indexing**: Pre-index cert types by PizzaStatusID and DivisionID
- **Lazy loading**: Load cert types on-demand instead of all at once

---

## Related Documentation

- [DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md](DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md) - Division-specific business logic
- [PIZZA_STATUS_ARCHITECTURE.md](../PIZZA_STATUS_ARCHITECTURE.md) - Overall pizza status system
- [REQUIREMENTS_EDITOR_IMPLEMENTATION.md](REQUIREMENTS_EDITOR_IMPLEMENTATION.md) - Requirements editor details

---

**Last Updated**: January 13, 2026  
**Status**: ✅ Implemented and Verified
