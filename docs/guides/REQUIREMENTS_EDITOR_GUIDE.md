# Requirements Editor - User Guide

## Overview

The Requirements Editor is an interactive drag-and-drop interface for managing certification requirements by division and status. It allows you to visually assign certifications to different lifecycle stages without manually editing JSON files.

## Accessing the Editor

1. Open the workflow builder: `http://localhost:8083/lifecycle-workflow-builder.html`
2. Click the **📝 Edit Requirements** button in the top-left controls
3. The interface will switch from operator view to requirements editing mode

## Interface Components

### Mode Toggle Button
- **📝 Edit Requirements**: Switch to editing mode
- **👥 View Operators**: Return to normal operator workflow view

### Division Filter
- Appears when in edit mode
- Select a division to edit its requirements
- Options include: "7 - MI", "10 - OR", "3 - TX", etc.
- Changes are division-specific

### Certification Pool (Left Panel)
- Shows all available certifications for the selected division
- Certifications are extracted from actual operator data
- Each cert is a draggable badge
- Hover to see visual feedback

### Requirements Grid (Right Panel)
- Shows all lifecycle status steps
- Each card represents one status (REGISTRATION, ONBOARDING, etc.)
- Drop zones accept dragged certifications
- Badge shows current cert count for that status

### Save Panel (Bottom-Right)
- Appears when changes are made
- Shows summary: Added/Removed counts
- **Preview** button: See detailed list of all changes
- **Save Changes** button: Download updated JSON file

## How to Use

### Adding a Certification to a Status

1. Select a division from the dropdown
2. Find the certification in the left panel
3. Click and drag the cert badge
4. Drop it onto a status card's drop zone
5. The cert appears in the status's requirement list
6. Save panel updates with change count

### Removing a Certification

1. Find the assigned cert in a status card
2. Click the **✕** button next to it
3. The cert is removed from requirements
4. Save panel updates with change count

### Previewing Changes

1. Click **👁️ Preview** in the save panel
2. See formatted list of all changes by status:
   - `+ Cert Name` = Added to requirements
   - `- Cert Name` = Removed from requirements
3. Review before saving

### Saving Changes

1. Click **💾 Save Changes** in the save panel
2. Confirm the download prompt
3. A JSON file downloads: `cert_requirements_by_status_division_<timestamp>.json`
4. Replace the existing `cert_requirements_by_status_division.json` file
5. Refresh the page to see your changes applied

### Canceling Edit Mode

1. Click **✕ Cancel Edit** button in controls
2. If you have unsaved changes, you'll be prompted to confirm
3. Returns to operator view mode without saving

## Features

### Smart Duplicate Detection
- Won't add a cert that already exists (case-insensitive)
- Prevents duplicate requirements

### Automatic Statistics
- When adding a cert, automatically calculates:
  - How many operators in that status have it
  - Percentage of compliance
- Data-driven insights preserved

### Visual Feedback
- Drag operations show visual states
- Drop zones highlight when dragging over them
- Color-coded badges for different states

### Safe by Design
- Changes are only downloaded, not auto-saved
- You control when/if changes are applied
- Can cancel at any time without affecting data
- Preview before committing

## Division-Specific Editing

Each division has its own certification requirements:

- **7 - MI**: Michigan-specific certs (may use ALL CAPS)
- **10 - OR**: Oregon-specific requirements
- **3 - TX**: Texas-specific requirements

Changes made to one division don't affect others. You must select each division separately to edit its requirements.

## Workflow Integration

The editor uses the same ideal flow as the operator view:

1. REGISTRATION
2. ONBOARDING
3. CREDENTIALING
4. DOT SCREENING
5. ORIENTATION-BIG STAR SAFETY & SERVICE
6. APPROVED-ORIENTATION BTW
7. COMPLIANCE REVIEW
8. SBPC APPROVED FOR SERVICE
9. APPROVED FOR CONTRACTING
10. IN-SERVICE

All changes maintain consistency with this lifecycle progression.

## Technical Details

### Data Source
- Certification pool is generated from actual operator data
- Only shows certs that exist in the selected division
- Dynamically updates based on division selection

### File Format
- Downloads standard JSON format
- Compatible with existing data structure
- Includes operator counts and percentages

### Browser Compatibility
- Uses HTML5 Drag and Drop API
- Requires modern browser (Chrome, Firefox, Edge, Safari)
- No additional dependencies needed

## Best Practices

1. **Review Before Editing**: Switch to operator view first to understand current requirements
2. **Edit One Division at a Time**: Focus on one division, save, verify, then move to next
3. **Preview All Changes**: Always click Preview before Save
4. **Backup First**: Keep a copy of the original JSON file before applying changes
5. **Test After Applying**: Refresh and verify operator compliance percentages look correct
6. **Document Changes**: Note what you changed and why (consider adding to git commit message)

## Troubleshooting

### Division Filter Not Showing
- Make sure you clicked "Edit Requirements" button first
- Button should show green and say "View Operators"

### Can't Drag Certifications
- Ensure you're in edit mode
- Try refreshing the page and re-entering edit mode
- Check browser console for errors

### Save Panel Not Appearing
- Make sure you've actually made changes (add or remove a cert)
- Panel only appears when `changesMade = true`

### Downloaded File Not Working
- Verify the filename matches exactly: `cert_requirements_by_status_division.json`
- Check JSON is valid (use JSON validator)
- Make sure you're replacing the file in `generated/` directory

### Changes Not Appearing After Refresh
- Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)
- Check that you replaced the correct file
- Verify HTTP server is serving from `generated/` directory

## Future Enhancements

### Planned Features
- **Backend Save Endpoint**: Direct save to server (no manual file replacement)
- **Undo/Redo**: Step backwards/forwards through changes
- **Bulk Operations**: Add/remove multiple certs at once
- **Templates**: Copy requirements from one division to another
- **Version History**: Track who changed what and when
- **Validation Rules**: Prevent invalid requirement combinations

### Backend Integration (Coming Soon)

Example Flask endpoint structure:

```python
@app.route('/api/requirements/save', methods=['POST'])
def save_requirements():
    data = request.json
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'backups/cert_requirements_{timestamp}.json'
    shutil.copy('cert_requirements_by_status_division.json', backup_path)
    
    # Save new version
    with open('cert_requirements_by_status_division.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({'status': 'success', 'backup': backup_path})
```

## Support

If you encounter issues:

1. Check browser console (F12) for error messages
2. Verify HTTP server is running: `ps aux | grep http.server`
3. Confirm data files exist in `generated/` directory
4. Review [DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md](DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md) for data structure details

## Related Documentation

- [DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md](DIVISION_SPECIFIC_CERTIFICATION_LOGIC.md) - How division filtering works
- [CERTIFICATION_REQUIREMENTS_METHODOLOGY.md](CERTIFICATION_REQUIREMENTS_METHODOLOGY.md) - How requirements are determined
- [DATABASE_STANDARDIZATION_SUMMARY.md](DATABASE_STANDARDIZATION_SUMMARY.md) - Database naming conventions
- [WORKFLOW_BUILDER_CHANGELOG.md](WORKFLOW_BUILDER_CHANGELOG.md) - Feature evolution history

---

**Last Updated**: January 12, 2026  
**Version**: 1.0  
**Status**: Production Ready
