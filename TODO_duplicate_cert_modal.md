# TODO: Centralize Duplicate Cert Modal Logic for All Add Entry Points

## Problem
Currently, the confirmation modal for duplicate certification assignment only appears when adding a cert type via the manual add button. Other entry points—such as autocomplete selection, drag-and-drop, and bulk add—bypass this logic and call `addCertToStatus` directly. This results in certs being reassigned without user confirmation, which can lead to accidental data changes.

## Solution
- Refactor all add-cert entry points (manual add, autocomplete, drag-and-drop, bulk add) to use a single function (e.g., `safeAddCertToStatus`) that performs the duplicate check and shows the confirmation modal if needed.
- Remove duplicate check and modal logic from individual entry points and ensure all use the centralized function.
- This will guarantee the modal always appears before any duplicate cert is reassigned, regardless of how the add is triggered.

## Status
- Manual add: Modal works
- Autocomplete, drag-and-drop, bulk add: Modal does NOT appear (logic bypassed)

## Action Needed
- Refactor as described above to ensure consistent user experience and data integrity.
