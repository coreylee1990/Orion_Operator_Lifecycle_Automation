# 🔄 HTML Editor Migration to Pizza Status Requirements

## Status: IN PROGRESS

The lifecycle-workflow-builder.html needs to be updated to work with the new pizza status requirements system instead of the master_cert_requirements.json file.

---

## Required Changes

### 1. Data Loading (Lines ~1988)

**Current:**
```javascript
const masterReqResponse = await fetch('master_cert_requirements.json' + cacheBuster);
const masterRequirements = await masterReqResponse.json();
certRequirements = buildRequirementsFromMaster(masterRequirements);
```

**New:**
```javascript
// Load pizza status requirements
const pizzaReqResponse = await fetch('../data/pay_PizzaStatusRequirements.json' + cacheBuster);
const pizzaRequirements = await pizzaReqResponse.json();

// Load status types for mapping
const statusTypesResponse = await fetch('../data/pay_StatusTypes.json' + cacheBuster);
const statusTypes = await statusTypesResponse.json();

// Build cert requirements structure from pizza status definitions
certRequirements = buildRequirementsFromPizzaStatus(pizzaRequirements, statusTypes);
```

---

### 2. Build Requirements Function

**Need to create new function:**
```javascript
function buildRequirementsFromPizzaStatus(pizzaRequirements, statusTypes) {
    const requirements = {};
    
    // For each status type, find its pizza status and get requirements
    for (const st of statusTypes) {
        const status = st.Status;
        const division = st.DivisionID;
        const pizzaId = st.PizzaStatusID;
        
        if (!pizzaId || !pizzaRequirements[pizzaId]) {
            continue;
        }
        
        const pizzaReq = pizzaRequirements[pizzaId];
        const requiredCerts = pizzaReq.required_certifications.map(c => c.name);
        
        const key = `${status}-${division}`;
        requirements[key] = {
            status,
            division,
            pizzaStatusId: pizzaId,
            pizzaStatusName: pizzaReq.pizza_status_name,
            requiredCertifications: requiredCerts,
            order: st.OrderID
        };
    }
    
    return requirements;
}
```

---

### 3. Save Function (Lines ~2834-2894)

**Current:**
```javascript
function downloadJSON(blob, filename = 'master_cert_requirements.json') {
    // Downloads master file
}
```

**New:**
```javascript
function savePizzaStatusRequirements() {
    // Convert current cert requirements back to pizza status format
    const pizzaRequirements = convertToPizzaStatusFormat(certRequirements);
    
    // Create blob and download
    const blob = new Blob([JSON.stringify(pizzaRequirements, null, 2)], 
                          {type: 'application/json'});
    downloadJSON(blob, 'pay_PizzaStatusRequirements.json');
}

function convertToPizzaStatusFormat(certRequirements) {
    // Group requirements by pizza status
    const pizzaGroups = {};
    
    for (const [key, req] of Object.entries(certRequirements)) {
        const pizzaId = req.pizzaStatusId;
        
        if (!pizzaGroups[pizzaId]) {
            pizzaGroups[pizzaId] = {
                pizza_status_id: pizzaId,
                pizza_status_name: req.pizzaStatusName,
                required_certifications: req.requiredCertifications.map(cert => ({
                    name: cert,
                    coverage: { /* can be calculated or left as metadata */ }
                })),
                status_mappings: []
            };
        }
        
        // Add this status+division to the mappings
        pizzaGroups[pizzaId].status_mappings.push({
            status: req.status,
            division: req.division,
            order: req.order
        });
    }
    
    return pizzaGroups;
}
```

---

### 4. UI Updates

**Option A: Keep Current UI (Simplest)**
- Show requirements per Status+Division as before
- Internally map to pizza status
- Save updates pizza status requirements file
- **Benefit:** Minimal UI changes, familiar workflow

**Option B: Add Pizza Status View**
- Add new tab showing pizza status groups
- Show which Status+Division combos share each pizza status
- Edit at pizza status level (affects all mappings)
- **Benefit:** More powerful, shows the grouping

**Recommendation:** Start with Option A, add Option B later

---

### 5. SQL Generation

**Issue:** Current SQL generation creates INSERT/UPDATE statements for non-existent tables.

**Options:**
1. **Remove SQL generation** - Just save JSON file
2. **Generate JSON diff** - Show what changed
3. **Keep for reference** - Generate SQL as "would be" statements

**Recommendation:** Option 2 (JSON diff) or Option 1 (remove)

---

### 6. Alias Handling (Lines ~1881)

**Current:**
```javascript
"certification_aliases": {}  // Empty in HTML, loaded from master file
```

**New:**
```javascript
// Load aliases separately
const aliasesResponse = await fetch('../config/certification_aliases.json' + cacheBuster);
const certificationAliases = await aliasesResponse.json();
```

---

## Implementation Plan

### Phase 1: Backend (✅ COMPLETE)
- [x] Delete master_cert_requirements.json
- [x] Create generate_pizza_status_requirements.py script
- [x] Generate data/pay_PizzaStatusRequirements.json
- [x] Update compliance script to use pizza status requirements
- [x] Extract certification_aliases.json to config/

### Phase 2: HTML Editor (🚧 IN PROGRESS)
- [ ] Update data loading to fetch pizza status requirements
- [ ] Create buildRequirementsFromPizzaStatus() function
- [ ] Update save function to write pizza status requirements
- [ ] Load certification aliases separately
- [ ] Test drag-drop functionality still works
- [ ] Update SQL generation or remove it

### Phase 3: Testing (⏳ PENDING)
- [ ] Test loading pizza status requirements
- [ ] Test editing requirements (drag-drop certs)
- [ ] Test saving changes
- [ ] Verify saved file structure is correct
- [ ] Test compliance script with edited requirements

---

## Key Benefits of Pizza Status Approach

1. **Consistency:** Same requirements for all Status+Division combos sharing a pizza status
2. **Efficiency:** Edit once, apply to multiple divisions
3. **Accuracy:** Larger sample sizes for inference (139 vs 15 operators)
4. **Alignment:** Uses database structure (PizzaStatusID field)
5. **Simplicity:** ~16 pizza statuses vs 500+ Status+Division combos

---

## Current State

**✅ Working:**
- Pizza status requirements file generated
- Compliance script updated and working
- Certification aliases extracted

**🚧 In Progress:**
- HTML editor migration (needs JavaScript updates)

**⏳ To Do:**
- Test entire workflow end-to-end
- Update documentation

---

*Last Updated: 2026-01-13*  
*Next: Update HTML editor JavaScript*
