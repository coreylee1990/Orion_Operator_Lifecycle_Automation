# Requirements Editor - Quick Start Card

## 🚀 Getting Started (30 seconds)

### Open the Editor
```
http://localhost:8083/lifecycle-workflow-builder.html
```

### Switch to Edit Mode
1. Click **📝 Edit Requirements** button (top-left)
2. Button turns green → You're in edit mode

### Select Division
1. Dropdown appears after clicking edit
2. Choose: **7 - MI**, **10 - OR**, **3 - TX**, etc.

## ✏️ Quick Actions

### Add Certification
```
Drag cert from left panel → Drop on status card → Done!
```

### Remove Certification
```
Click ✕ next to cert name → Removed!
```

### Preview Changes
```
Bottom-right panel shows changes → Click "Preview" for details
```

### Save Changes
```
Click "Save Changes" → Download JSON → Replace file → Refresh
```

### Cancel
```
Click "Cancel Edit" → Confirm → Back to operator view
```

## 🎯 Common Tasks

### Add Social Security Card to REGISTRATION for Michigan
1. Click "Edit Requirements"
2. Select "7 - MI"
3. Find "SOCIAL SECURITY CARD" in left panel
4. Drag to "REGISTRATION" drop zone
5. Click "Save Changes"
6. Replace `cert_requirements_by_status_division.json`
7. Refresh page

### Remove Expired Cert from All Statuses
1. Enter edit mode
2. Select division
3. Find cert in each status card
4. Click ✕ on each occurrence
5. Preview changes
6. Save if correct

### Copy Requirements from One Division to Another
*Currently manual:*
1. Edit first division, note requirements
2. Switch to second division
3. Drag same certs to same statuses
4. Save changes

*(Automated copy feature planned for Phase 2)*

## 🎨 Visual Guide

```
┌──────────────────────────────────────────────────────┐
│  📝 Edit Requirements  │ [Select Division ▼] │ ...  │
└──────────────────────────────────────────────────────┘

┌────────────────┬─────────────────────────────────────┐
│ 🏷️ Cert Pool   │  📋 Requirements Grid               │
│                │                                      │
│ [Cert 1] ←──┐  │  ┌──────────────────────────────┐   │
│ [Cert 2]    │  │  │ REGISTRATION          (2)     │   │
│ [Cert 3]    │  │  │ ┌────────────────────────┐    │   │
│ ...         └──┼─→│ │ Drop certs here...     │    │   │
│                │  │ └────────────────────────┘    │   │
│ (100 certs)    │  └──────────────────────────────┘   │
│                │                                      │
│                │  ┌──────────────────────────────┐   │
│                │  │ ONBOARDING            (5)     │   │
│                │  │ • Cert A              [✕]    │   │
│                │  │ • Cert B              [✕]    │   │
│                │  └──────────────────────────────┘   │
└────────────────┴─────────────────────────────────────┘

                        ┌──────────────────┐
                        │ Changes Made:    │
                        │ Added: 3         │
                        │ Removed: 1       │
                        │                  │
                        │ [💾 Save] [👁️ Preview] │
                        └──────────────────┘
```

## ⚡ Keyboard Shortcuts

*Currently none - mouse-based interface*  
*(Keyboard shortcuts planned for future release)*

## 🔒 Safety Features

- ✅ **No Auto-Save**: Changes only saved when you click "Save"
- ✅ **Confirmation Prompts**: Warns before discarding changes
- ✅ **Preview First**: Review all changes before applying
- ✅ **Timestamped Backups**: Downloaded files include timestamp
- ✅ **Can Always Cancel**: Exit without saving anytime

## 🐛 Troubleshooting

### Editor Not Appearing
```
1. Check button is green (edit mode active)
2. Select a division from dropdown
3. Refresh page if needed (Ctrl+Shift+R)
```

### Can't Drag Certifications
```
1. Verify you're in edit mode (green button)
2. Make sure division is selected
3. Try different browser if issue persists
```

### Changes Not Saving
```
1. Click "Save Changes" button
2. Check download folder for JSON file
3. Replace old file: generated/cert_requirements_by_status_division.json
4. Hard refresh page (Ctrl+Shift+R)
```

### Division Filter Empty
```
1. Check operators have DivisionID values
2. Verify pay_Operators.json loaded correctly
3. Check browser console for errors (F12)
```

## 📚 More Help

- **Full Guide**: `documentation/REQUIREMENTS_EDITOR_GUIDE.md`
- **Technical Details**: `documentation/REQUIREMENTS_EDITOR_IMPLEMENTATION.md`
- **Data Structure**: `documentation/DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md`
- **Requirements Logic**: `documentation/CERTIFICATION_REQUIREMENTS_METHODOLOGY.md`

## 💡 Pro Tips

1. **Edit in Small Batches**: Make a few changes, save, verify, repeat
2. **Use Preview Liberally**: Always preview before saving
3. **Keep Backups**: Save dated copies of JSON before making changes
4. **One Division at a Time**: Focus on one division completely
5. **Check Operator View**: Switch back to verify progress bars look right

## 🎯 Next Steps

After using the editor:

1. **Test Thoroughly**: Try adding/removing various certs
2. **Verify Operator Impact**: Check progress bars in operator view
3. **Document Changes**: Note what you changed and why
4. **Share Feedback**: Report any issues or desired features
5. **Plan Next Edits**: Use preview to plan future requirement changes

---

**Version**: 1.0  
**Last Updated**: January 12, 2026  
**Status**: Production Ready ✅
