# Orion Operator Lifecycle Automation - Data File Instructions

This document provides an overview of the data files found in the `data/` directory, which are used to manage the lifecycle of operators within the Orion system. It also outlines the requirements and architectural logic for building a "Rules Engine" and an "Automation Process" to manage operator status transitions.

## Data Files Overview:

### 1. `pay_Operators.txt`
- **Content:** This file contains a JSON array of operator records.
- **Purpose:** It serves as the primary list of operators, detailing their basic information and current status within the system.
- **Key Fields:**
    - `Id`: Unique identifier for each operator.
    - `FirstName`, `LastName`: Operator's name.
    - `DivisionID`: The division the operator belongs to (e.g., "11 - GA").
    - `StatusOrderSequence`: A numerical sequence for their current status.
    - `CurrentStatus`: The current operational status of the operator (e.g., "ONBOARDING", "IN-PROCESS").

### 2. `pay_CertTypes.txt`
- **Content:** This file is identical in structure and content to `pay_Operators.txt`, containing a JSON array of operator records.
- **Purpose:** It appears to be a duplicate or a specific view of the operator data, possibly used for certification tracking or a specific part of the onboarding process. It lists operators and their current status, similar to `pay_Operators.txt`.

### 3. `pay_Certifications.txt`
- **Content:** This file contains a SQL `SELECT` statement.
- **Purpose:** It queries the `pay_Certifications` table, filtering records by a list of `OperatorId`s. This suggests that `pay_Certifications` is a database table that stores certification details for operators, and this file is likely used to retrieve or reference those certifications for a specific set of operators. The `OperatorId`s in this query correspond to the `Id` field in `pay_Operators.txt` and `pay_CertTypes.txt`.

### 4. `pay_PizzaStatus.txt`
- **Content:** This file contains a JSON array of "Pizza Status" objects.
- **Purpose:** These statuses appear to be high-level categories or stages related to various processes within the system, potentially for tracking tasks or incidents. The `IsOperator` and `IsProvider` flags indicate that these statuses can apply to different types of entities.
- **Key Fields:**
    - `ID`: Unique identifier for the status.
    - `Status`: The name of the status (e.g., "Onboarding", "In-Service", "Incident Reported").
    - `Description`: A brief explanation of the status.
    - `MobileAppOrder`: Order for display in a mobile application.
    - `IsOperator`, `IsProvider`: Flags indicating applicability to operators or providers.

### 5. `pay_StatusTypes.txt`
- **Content:** This file contains a JSON array of detailed "Status Type" objects.
- **Purpose:** This file defines a comprehensive set of granular statuses used throughout the operator lifecycle. It includes various flags and metadata to control behavior and tracking. The `PizzaStatusID` field links these detailed statuses to the broader categories defined in `pay_PizzaStatus.txt`.
- **Key Fields:**
    - `Id`: Unique identifier for the status type.
    - `Status`: The name of the status type (e.g., "IN-PROCESS", "CREDENTIALING", "TERMINATED").
    - `Description`: A detailed description of the status type.
    - `DivisionID`: The division associated with this status type.
    - `Fleet`, `CertFlag`, `Providers`, `OutOfServiceFlag`: Boolean flags indicating various attributes of the status.
    - `isHireEvent`, `isTermEvent`: Flags indicating if the status is related to hiring or termination.
    - `PizzaStatusID`: Links to an `ID` in `pay_PizzaStatus.txt`, categorizing this status type under a broader "Pizza Status".

## Relationships Between Data Files:

- `pay_Operators.txt` and `pay_CertTypes.txt` both list operators and their current status.
- `pay_Certifications.txt` uses `OperatorId`s found in `pay_Operators.txt` and `pay_CertTypes.txt` to query certification data.
- `pay_StatusTypes.txt` defines detailed operational statuses, many of which are linked to broader categories in `pay_PizzaStatus.txt` via the `PizzaStatusID`.
- The `CurrentStatus` field in `pay_Operators.txt` and `pay_CertTypes.txt` likely refers to one of the `Status` values defined in `pay_StatusTypes.txt`.

These files collectively provide a snapshot and definitions for managing the various stages and attributes of operators within the Orion Operator Lifecycle Automation system.

---

## Building the Status Automation Engine

To automate the operator lifecycle, a "Rules Engine" is required to manage transitions between operator statuses based on certifications and other criteria.

### 1. The Review & Logic Prompt

This prompt should be used when feeding these files into an LLM or providing requirements to a developer for building the automation:

"Analyze these five tables to build a Status Automation Engine:

`pay_StatusTypes`: Our 14-step master sequence (OrderID 1-14).

`pay_PizzaStatus`: The mobile app categories mapped to StatusTypes.

`pay_CertTypes`: The master list of all possible certificates/documents.

`pay_Certifications`: The actual certificates held by specific Operators.

`pay_Operators`: The individual records currently assigned to a StatusID.

**Goal:** Create a transition matrix. For every OrderID (n), identify which CertTypeIDs are mandatory to advance the Operator to OrderID (n+1).

**Requirements:**

*   **Gap Analysis:** For any Operator in a status between 2 and 13, list the specific Certificates missing from `pay_Certifications` that are required for the next OrderID.
*   **Automation Trigger:** Define the logic where: IF (Required Certs for Next OrderID) are Valid AND Not Expired, THEN Update `pay_Operators.StatusID` to the Next ID in the sequence.
*   **Division Filtering:** Ensure logic respects the `DivisionID` mapping for all 14 steps."

### 2. The Automation Process (The "Traffic Controller")

To automate the flow, the application must follow this Evaluation Loop:

**Step A: The Requirement Map**
You must first create a "bridge" (either in code or a new table) that links Status to Certs. Example: * Step 4 (DOT Screening) requires: Medical_Card_Cert AND MVR_Cert.

**Step B: The Automation Logic Flow**
*   **Check Current State:** Query `pay_Operators` to find their current `OrderID`.
*   **Look Ahead:** Query `pay_StatusTypes` to find the requirements for `OrderID + 1`.
*   **Validate Documents:** Check `pay_Certifications` for that Operator.
    *   **Condition:** Document must exist AND `ExpirationDate > Today`.
*   **Auto-Move:**
    *   If requirements are met: Update `Operator.StatusID` to the new ID.
    *   If requirements are NOT met: Flag the missing `CertType` in the "Next Steps" dashboard.

### 3. Data Integrity "Red Flags" to Watch For

During the review of these five files, the app must check for these common breaks in the chain:

| Table             | Potential Failure Point                                                              |
| :---------------- | :----------------------------------------------------------------------------------- |
| `pay_Certifications` | Multiple versions of the same cert; app must pick the one with the latest `RecordAt` date. |
| `pay_StatusTypes`    | `isDeleted = 1` on a middle step (e.g., Step 7 is deleted), breaking the 1-14 chain. |
| `pay_Operators`      | `StatusID` is `NULL` or points to an `ID` that doesn't exist in the current Division. |
| `pay_CertTypes`      | Mapping a certificate to a status that doesn't exist in that specific Division.       |

### 4. Summary of the "Automation Engine" App

Your app should have two main screens:

*   **The Processor:** A background job that runs the SQL updates automatically based on certificate uploads.
*   **The Oversight Dashboard:** A view of the "Top 100" Operators showing:
    *   Current Status (e.g., Step 6)
    *   Next Status (e.g., Step 7)
    *   Missing Docs (A list of `CertTypes` required for Step 7 but not found in `pay_Certifications`).

---

## Source of Truth and Multi-File Integration

To build the automation engine, a Source of Truth that links the database structure to the business logic is essential.

### 1. The Master 14-Step Alignment Reference

This table represents the ideal state for operator progression. The application must use this to validate that every division is aligned before it starts moving operators.

| OrderID | Internal Status Name                 | Pizza Status (Mobile App Category) | Mobile Order |
| :------ | :----------------------------------- | :--------------------------------- | :----------- |
| 1       | REGISTRATION                         | Onboarding                         | 1            |
| 2       | ONBOARDING                           | Onboarding                         | 1            |
| 3       | CREDENTIALING                        | Credentialing                      | 2            |
| 4       | DOT SCREENING                        | DOT Screening                      | 3            |
| 5       | ORIENTATION-BIG STAR SAFETY & SERVICE | Orientation                        | 4            |
| 6       | ORIENTATION-CLIENT HOSTED            | Orientation                        | 4            |
| 7       | Approved for CHO (Client Hosted)     | Orientation                        | 4            |
| 8       | APPROVED-ORIENTATION BTW             | Orientation                        | 4            |
| 9       | COMPLIANCE REVIEW                    | Compliance Review                  | 5            |
| 10      | SBPC APPROVED FOR SERVICE            | Compliance Review                  | 5            |
| 11      | Approved for Service                 | Contracting                        | 6            |
| 12      | APPROVED FOR CONTRACTING             | Contracting                        | 6            |
| 13      | APPROVED FOR LEASING                 | Vehicle Leasing                    | 7            |
| 14      | IN-SERVICE                           | In-Service                         | 8            |

### 2. The Multi-File Integration Prompt

When ready to process data, use this specific instruction set to define how the files interact:

"Review the following five data files to build an automated Operator Pipeline:

*   `pay_StatusTypes` (The Map): Use the `OrderID` (1-14) to define the path.
*   `pay_PizzaStatus` (The UI): Group the 14 statuses into the 8 visible mobile app categories.
*   `pay_CertTypes` (The Rules): Define which document types (e.g., Driver's License, Medical Card) are required for which `OrderID`.
*   `pay_Certifications` (The Evidence): The actual files uploaded by operators.
*   `pay_Operators` (The Subjects): The current location of every operator in the 14-step journey."

**The Automation Logic Requirements:**

*   **Sequential Progression:** An operator cannot move to `OrderID: 5` unless they have successfully cleared all requirements for `OrderID: 4`.
*   **Document Validation:** Access `pay_Certifications`. Check `IsExpired`, `IsVerified`, and `CertTypeID`.
*   **The Transition Trigger:** Create a logic gate:
    *   IF Operator is at Order (n) AND all required `CertTypeID`s for Order (n+1) are `IsVerified = TRUE` and `IsExpired = FALSE`, THEN update `pay_Operators.StatusID` to `OrderID (n+1)`.
    *   ELSE, if any required `CertTypeID` for Order (n+1) is `IsVerified = FALSE` or `IsExpired = TRUE`, THEN flag the operator for manual review and list the specific missing or invalid `CertTypeID`s.
*   **Division-Specific Rules:** Ensure that the `DivisionID` in `pay_Operators` is respected throughout the progression. An operator can only move to the next `OrderID` if the `DivisionID` matches the requirements defined in `pay_StatusTypes` for that `OrderID`.
*   **Error Handling:** Implement robust error handling for cases where `StatusID` is `NULL` or points to a non-existent `ID`, or if `isDeleted = 1` for a critical step in `pay_StatusTypes`.
*   **Logging:** Log all status transitions, including the `OperatorID`, old `StatusID`, new `StatusID`, and the `CertTypeID`s that triggered the change.
*   **Reporting:** Generate a daily report of operators who are stuck due to missing or invalid certifications, categorized by `DivisionID` and `OrderID`.

---

Would you like me to write a Python script template that performs this cross-table "Gap Analysis" using these five file names?
