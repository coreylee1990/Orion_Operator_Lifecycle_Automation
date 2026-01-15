#!/usr/bin/env python3
"""
Generate SQL query to fetch certifications for all operators in the sample data.
Reads operator IDs from pay_Operators_sample_across_statuses.txt and generates 
get_operator_certifications.sql dynamically.
"""

import json
import sys
from pathlib import Path

def load_operators(data_file: Path) -> list:
    """Load operators from JSON data file."""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            # Handle both array format and object format with 'operators' key
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'operators' in data:
                return data['operators']
            else:
                print(f"Error: Unexpected JSON format in {data_file}", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error loading {data_file}: {e}", file=sys.stderr)
        sys.exit(1)

def generate_cert_query(operators: list, output_file: Path):
    """Generate SQL query with all operator IDs."""
    
    # Build operator ID list without comments
    operator_list = []
    for op in operators:
        op_id = op.get('ID') or op.get('operatorID') or op.get('Id')
        operator_list.append(f"        '{op_id}',")
    
    # Join all but last with comma, last without comma
    operator_ids_formatted = '\n'.join(operator_list[:-1]) + '\n' + operator_list[-1].rstrip(',')
    
    # Generate SQL with ALL 67 certification fields - using updated operator fields
    sql = f"""SELECT 
    o.ID,
    o.FirstName,
    o.LastName,
    o.Email,
    o.Mobile,
    o.DivisionID,
    o.Status,
    o.StatusID,
    o.StatusName,
    o.OrderID,
    o.StartDate,
    o.LastStatusDate,
    o.DateCreated,
    c.ID AS CertificationID,
    c.CertTypeID,
    c.FleetID,
    c.Cert,
    c.Date,
    c.Attachments,
    c.IsDeleted,
    c.ProviderID,
    c.isApproved,
    c.ApprovedBy,
    c.Comments,
    c.RecordAt,
    c.RecordBy,
    c.UpdateAt,
    c.UpdateBy,
    c.EsignStatus,
    c.DocumentID,
    c.FolderID,
    c.CompletionDate,
    c.ApprovedDate,
    c.SmsCount,
    c.isMobile,
    c.isProviderPortal,
    c.isOperatorPortal,
    c.isBackOffice,
    c.SignerID,
    c.isReviewed,
    c.Sent,
    c.ESignSendBy,
    c.ESignSendAt,
    c.ESignUpdatedAt,
    c.ESignUpdatedBy,
    c.ScheduledAppt,
    c.eSignInvitationExpiryDate,
    c.Passport,
    c.CloneID,
    c.isDisapproved,
    c.DisapprovedBy,
    c.DisapprovedAt,
    c.RejectedAt,
    c.RejectedBy,
    c.IsRejected,
    c.DisapprovalReason,
    c.RejectReason,
    c.SignNowInviteID,
    c.DeletedBy,
    c.UnDeletedBy,
    c.DeletedAt,
    c.UnDeletedAt,
    c.StripeAccountID,
    c.IsUploadByProvider,
    c.BatchID,
    c.BatchRemoveID,
    c.IsPaid,
    c.IsPaymentDate,
    c.PaymentReferenceID,
    c.I3ReferenceNumber,
    c.DonorPass,
    c.IsSensitive,
    c.IsRandom,
    c.SignedAttachments,
    c.IsDisqualified,
    c.AIReviewed,
    c.AINotes,
    c.AIRecommendation,
    c.DocumentReasonID,
    c.BETransactionHeaderID
FROM dbo.pay_Operators AS o
INNER JOIN dbo.pay_StatusTypes AS st ON o.StatusID = st.Id
LEFT JOIN dbo.pay_Certifications AS c ON o.ID = c.OperatorId
WHERE o.ID IN (
{operator_ids_formatted}
)
AND (c.ID IS NULL OR ISNULL(c.IsDeleted, 0) = 0)
ORDER BY st.Status, CAST(st.OrderID AS INT), o.LastName, o.FirstName, c.Cert;
"""
    
    # Write SQL file
    try:
        with open(output_file, 'w') as f:
            f.write(sql)
        print(f"✅ Generated {output_file}")
        print(f"   Included {len(operators)} operators")
        return True
    except Exception as e:
        print(f"Error writing {output_file}: {e}", file=sys.stderr)
        return False

def main():
    # Setup paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Use pay_Operators.json for operator data
    data_file = project_root / 'data' / 'pay_Operators.json'
    output_file = script_dir / 'get_operator_certifications.sql'
    
    print("=" * 80)
    print("Certification Query Generator")
    print("=" * 80)
    print(f"Reading operators from: {data_file}")
    print(f"Generating SQL to:      {output_file}")
    print()
    
    # Load and process
    operators = load_operators(data_file)
    
    if not operators:
        print("⚠️  No operators found in data file!", file=sys.stderr)
        sys.exit(1)
    
    print(f"📊 Found {len(operators)} operators")
    print()
    
    # Generate query
    success = generate_cert_query(operators, output_file)
    
    print()
    print("=" * 80)
    if success:
        print("✅ Done! You can now run get_operator_certifications.sql in SQL Server")
    else:
        print("❌ Failed to generate query", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
