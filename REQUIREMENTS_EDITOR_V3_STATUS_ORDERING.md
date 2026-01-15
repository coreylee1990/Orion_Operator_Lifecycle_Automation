# Requirements Editor - V3 Update

## 🎉 New Feature: Status Order Management

### What's New

The Requirements Editor now supports **drag-and-drop status reordering** with full visual feedback and safety warnings.

---

## 🎯 Features

### 1. Drag-and-Drop Status Reordering

**How to Use:**
1. Open the Requirements Editor
2. Select a division (or "ALL")
3. Click and drag the status cards using the **⠿** handle
4. Drop on another status to reorder

**Visual Indicators:**
- **⠿** Drag handle on each status card
- **#1, #2, #3** Order badge shows current position
- Cards highlight when dragging over them
- Smooth animations during reorder

### 2. ALL Divisions Warning System

**When editing ALL divisions, you'll see:**
- ⚠️ **Orange warning banner** at the top:
  - "GLOBAL EDIT MODE - ALL DIVISIONS"
  - Animated pulse effect to draw attention
  - Clear warning that changes affect all divisions

**When reordering statuses in ALL mode:**
- Modal confirmation dialog appears
- Explains that division-specific orders will be overridden
- Requires explicit confirmation before proceeding

### 3. Visual Status Order Display

**Each status card now shows:**
```
⠿ #2 ONBOARDING        [5 certs]
```
- ⠿ = Drag handle
- #2 = Order number
- ONBOARDING = Status name
- [5 certs] = Required certifications count

---

## 💾 How Data is Stored

### Single Source of Truth

**Location:** `config/master_cert_requirements.json`

**Structure:**
```json
{
  "global_requirements": {
    "ONBOARDING": {
      "order": 2,
      "description": "Basic onboarding documentation and identification",
      "required_certs": ["Driver License", "Social Security Card", "W9"],
      "notes": "Must have valid driver's license and basic documentation"
    }
  },
  "division_overrides": {
    "10 - OR": {
      "ONBOARDING": {
        "add_required_certs": ["TriMet Background Release Form A&B"],
        "notes": "Oregon (TriMet) requires additional background release forms"
      }
    }
  },
  "certification_aliases": {
    "Driver License": [
      "Driver License",
      "Drivers License",
      "Driver's License",
      "DRIVERS LICENSE w/CHAUF ENDORSE"
    ]
  }
}
```

### How It Works

1. **Global Requirements** = Base requirements ALL divisions must meet
2. **Division Overrides** = Additional certs specific divisions need (inherited + extras)
3. **Order Field** = Status sequence number (determines workflow order)
4. **Aliases** = Different names for the same certification (for matching)

---

## 🔄 Complete Workflow

### 1. Make Changes in HTML Editor

**Add/Remove Certifications:**
- Drag certs from left panel → status boxes
- Click ❌ to remove individual certs
- Click 🗑️ to delete cert type from all statuses

**Reorder Statuses:**
- Drag status cards to reorder
- Confirm if using ALL divisions mode

### 2. Save Changes

Click **💾 Save Requirements** button:
- Downloads `master_cert_requirements.json`
- Contains all changes (certs + order numbers)
- Ready to copy to `config/` directory

### 3. Copy to Config

```bash
# Manually copy downloaded file
cp ~/Downloads/master_cert_requirements.json config/master_cert_requirements.json

# Also update tools directory
cp config/master_cert_requirements.json tools/master_cert_requirements.json
```

### 4. Run Compliance Report

```bash
python3 scripts/reports/generate_compliance_gap_report.py
```

Compliance report will use the new requirements and status orders.

---

## ⚠️ Important Notes

### ALL Divisions Mode

When **"ALL"** is selected:
- Changes apply to EVERY division
- Orange warning banner is always visible
- Confirmation modal appears for status reorders
- Individual division settings are overridden

**Use ALL mode when:**
- ✅ Setting company-wide requirements
- ✅ Establishing baseline workflow order
- ✅ Creating global certification standards

**Use individual division when:**
- ✅ Adding division-specific requirements
- ✅ Maintaining unique workflow for one location
- ✅ Testing changes before global rollout

### Status Order Best Practices

1. **Maintain logical progression**
   - REGISTRATION → ONBOARDING → CREDENTIALING → etc.

2. **Use consistent numbering**
   - Sequential: 1, 2, 3, 4...
   - Gaps are okay: 1, 2, 5, 8... (allows future insertions)

3. **Document major changes**
   - Note why statuses were reordered
   - Communicate to team before implementing

4. **Test before production**
   - Reorder in test environment first
   - Verify compliance reports still accurate
   - Check SQL generation works correctly

---

## 🎨 Visual Indicators Quick Reference

| Indicator | Meaning |
|-----------|---------|
| ⠿ | Drag handle (grab here to reorder) |
| #2 | Status order number |
| ⚠️ | Warning (ALL divisions mode) |
| 🌐 | Editing all divisions |
| 📍 | Editing specific division |
| ❌ | Remove cert from this status |
| 🗑️ | Delete cert type from all statuses |
| 💾 | Save all changes |

---

## 🔧 Technical Details

### Data Flow

```
HTML Editor (tools/)
    ↓ User makes changes
    ↓ Click Save
Downloaded JSON
    ↓ Manual copy
config/master_cert_requirements.json
    ↓ Used by
Compliance Report Script
    ↓ Generates
output/compliance_gap_report.json
```

### Why Manual Copy?

The HTML runs in a browser, which **cannot directly write to your file system** for security reasons. It can only download files to your Downloads folder.

**Alternative approaches:**
- ✅ Current: Manual copy (simple, safe)
- ❌ Backend API: Would require Python/Node.js server (complex)
- ❌ Browser file system API: Limited browser support, security concerns

---

## 🚀 Quick Start Guide

### First Time Setup

1. Start web server:
   ```bash
   cd /home/eurorescue/Desktop/Orion_Operator_Lifecycle_Automation
   python3 -m http.server 8083
   ```

2. Open editor:
   ```
   http://127.0.0.1:8083/tools/lifecycle-workflow-builder.html
   ```

3. Click **✏️ Edit Requirements**

4. Select division or "ALL"

### Making Changes

**To add a required cert:**
- Drag cert from left panel → drop in status box

**To remove a cert:**
- Click ❌ next to cert name

**To reorder statuses:**
- Drag ⠿ handle on status card → drop on target status

**To save:**
- Click 💾 Save Requirements
- Copy downloaded file to `config/`
- Copy to `tools/` directory too

### Verifying Changes

```bash
# Check compliance with new requirements
python3 scripts/reports/generate_compliance_gap_report.py

# View the report
cat output/compliance_gap_report.txt | head -50
```

---

## 📞 Need Help?

**Common Issues:**

**Q: Status cards won't drag**
- A: Make sure you're grabbing the ⠿ handle, not the cert area below

**Q: Confirmation modal won't appear**
- A: Check browser console for errors (F12)

**Q: Changes not saving**
- A: Check that you copied downloaded file to `config/` directory

**Q: Order numbers not updating**
- A: Make sure you saved after reordering and copied to config

**Q: ALL mode warning not showing**
- A: Check that "ALL" is selected in dropdown (should see 🌐 icon)

---

## 📝 Summary

**Storage:** `config/master_cert_requirements.json` (single source of truth)

**What You Can Do:**
- ✅ Add/remove required certs per status
- ✅ Drag-and-drop to reorder statuses
- ✅ Edit all divisions or just one
- ✅ Delete cert types completely
- ✅ Generate SQL for database updates
- ✅ Visual warnings for global changes

**Best Practice:**
1. Make changes in HTML editor
2. Save and copy to config/
3. Run compliance report
4. Review changes
5. Execute SQL if needed
6. Commit to Git

**Professional & Clean:**
- One master file
- Clear hierarchy (global + overrides)
- Visual safety warnings
- Change confirmation for bulk edits
- Order numbers persist with statuses
