#!/usr/bin/env python3
"""
Certification Name Normalization Module

This module provides functions to normalize certification names for cross-division matching.
Handles variations in case, trailing spaces, and division-specific naming conventions.

Usage:
    from cert_name_normalizer import normalize_cert_name, certs_match
    
    if certs_match('CTAA PASSENGER ASSISTANCE', 'CTAA Passenger Assistance'):
        print("Match!")
"""

import re
from typing import Dict, List, Set

# Canonical mappings for known variations
# Format: { 'normalized_key': 'Canonical Name' }
CANONICAL_CERT_NAMES = {
    'background check': 'Background Check',
    'ctaa passenger assistance': 'CTAA Passenger Assistance',
    'defensive driving': 'Defensive Driving',
    'dot driver questionnaire': 'DOT Driver Questionnaire ',  # Note: trailing space is canonical
    'dot pre-contracting drug/alc screen': 'DOT Pre-Contracting Drug/Alc Screen ',  # Note: trailing space is canonical
    "driver's license_backside": "Driver's License_BACKSIDE",
    'service agreement': 'Service Agreement',
    'social security card': 'Social Security Card',
}

def normalize_cert_name(cert_name: str) -> str:
    """
    Normalize a certification name for comparison purposes.
    
    This function:
    1. Converts to lowercase
    2. Strips leading/trailing whitespace
    3. Replaces multiple spaces with single space
    4. Returns the canonical form if known
    
    Args:
        cert_name: The certification name to normalize
        
    Returns:
        Normalized certification name for comparison
        
    Examples:
        >>> normalize_cert_name('CTAA PASSENGER ASSISTANCE')
        'ctaa passenger assistance'
        
        >>> normalize_cert_name('Defensive Driving ')
        'defensive driving'
    """
    if not cert_name:
        return ''
    
    # Basic normalization
    normalized = cert_name.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)  # Replace multiple spaces with single space
    
    return normalized

def get_canonical_name(cert_name: str) -> str:
    """
    Get the canonical (standardized) name for a certification.
    
    Args:
        cert_name: Any variation of the certification name
        
    Returns:
        The canonical certification name, or the original if not in mapping
        
    Examples:
        >>> get_canonical_name('CTAA PASSENGER ASSISTANCE')
        'CTAA Passenger Assistance'
        
        >>> get_canonical_name('ctaa passenger assistance')
        'CTAA Passenger Assistance'
        
        >>> get_canonical_name('SOCIAL SECURITY CARD')
        'Social Security Card'
    """
    normalized = normalize_cert_name(cert_name)
    return CANONICAL_CERT_NAMES.get(normalized, cert_name)

def certs_match(cert1: str, cert2: str) -> bool:
    """
    Check if two certification names match (ignoring case and spacing variations).
    
    Args:
        cert1: First certification name
        cert2: Second certification name
        
    Returns:
        True if certifications match, False otherwise
        
    Examples:
        >>> certs_match('CTAA PASSENGER ASSISTANCE', 'CTAA Passenger Assistance')
        True
        
        >>> certs_match('Defensive Driving', 'Defensive Driving ')
        True
        
        >>> certs_match('Background Check', 'CTAA Passenger Assistance')
        False
    """
    return normalize_cert_name(cert1) == normalize_cert_name(cert2)

def find_matching_cert(cert_name: str, cert_list: List[str]) -> str:
    """
    Find a matching certification from a list (case-insensitive, space-insensitive).
    
    Args:
        cert_name: Certification name to find
        cert_list: List of certification names to search
        
    Returns:
        The matching certification name from the list, or None if not found
        
    Examples:
        >>> certs = ['CTAA Passenger Assistance', 'Background Check']
        >>> find_matching_cert('ctaa passenger assistance', certs)
        'CTAA Passenger Assistance'
    """
    normalized_target = normalize_cert_name(cert_name)
    
    for cert in cert_list:
        if normalize_cert_name(cert) == normalized_target:
            return cert
    
    return None

def standardize_cert_names(cert_list: List[str]) -> List[str]:
    """
    Standardize a list of certification names to their canonical forms.
    
    Args:
        cert_list: List of certification names (any variation)
        
    Returns:
        List of canonical certification names
        
    Examples:
        >>> standardize_cert_names(['SOCIAL SECURITY CARD', 'ctaa passenger assistance'])
        ['Social Security Card', 'CTAA Passenger Assistance']
    """
    return [get_canonical_name(cert) for cert in cert_list]

def get_variations_info() -> Dict[str, List[str]]:
    """
    Get information about known certification name variations.
    
    Returns:
        Dictionary mapping canonical names to lists of known variations
    """
    variations = {}
    
    # Known variations based on analysis
    variations['Background Check'] = ['BACKGROUND CHECK', 'Background Check']
    variations['CTAA Passenger Assistance'] = ['CTAA PASSENGER ASSISTANCE', 'CTAA Passenger Assistance']
    variations['Defensive Driving'] = ['Defensive Driving', 'Defensive Driving ']
    variations['DOT Driver Questionnaire '] = ['DOT Driver Questionnaire', 'DOT Driver Questionnaire ']
    variations['DOT Pre-Contracting Drug/Alc Screen '] = ['DOT Pre-Contracting Drug/Alc Screen', 'DOT Pre-Contracting Drug/Alc Screen ']
    variations["Driver's License_BACKSIDE"] = ["Driver's License_BACKSIDE", "Driver's License_BACKSIDE "]
    variations['Service Agreement'] = ['SERVICE AGREEMENT', 'Service Agreement']
    variations['Social Security Card'] = ['SOCIAL SECURITY CARD', 'Social Security Card']
    
    return variations

def validate_cert_name(cert_name: str) -> Dict[str, any]:
    """
    Validate a certification name and provide recommendations.
    
    Args:
        cert_name: Certification name to validate
        
    Returns:
        Dictionary with validation info:
        - 'is_canonical': Whether name is in canonical form
        - 'canonical_name': The canonical form
        - 'has_trailing_space': Whether name has trailing space
        - 'has_case_issues': Whether case doesn't match canonical
        - 'recommendation': What to do
    """
    canonical = get_canonical_name(cert_name)
    is_canonical = cert_name == canonical
    
    has_trailing_space = cert_name.rstrip() != cert_name
    has_leading_space = cert_name.lstrip() != cert_name
    has_case_issues = cert_name.lower() == canonical.lower() and cert_name != canonical
    
    recommendation = 'OK'
    if not is_canonical:
        recommendation = f"Update to '{canonical}'"
    
    return {
        'is_canonical': is_canonical,
        'canonical_name': canonical,
        'has_trailing_space': has_trailing_space,
        'has_leading_space': has_leading_space,
        'has_case_issues': has_case_issues,
        'recommendation': recommendation
    }

# Division-specific patterns (Division 7 - MI uses ALL CAPS for certain certs)
DIVISION_PATTERNS = {
    '7': {  # Michigan
        'pattern': 'ALL_CAPS',
        'description': 'Division 7 (MI) uses ALL CAPS for some certifications in source data',
        'affected_certs': [
            'BACKGROUND CHECK',
            'CTAA PASSENGER ASSISTANCE',
            'SOCIAL SECURITY CARD'
        ]
    }
}

def is_division_specific_variation(cert_name: str, division: str) -> bool:
    """
    Check if a certification name is a division-specific variation.
    
    Args:
        cert_name: Certification name
        division: Division number (e.g., '7', '10')
        
    Returns:
        True if this is a known division-specific variation
    """
    if division in DIVISION_PATTERNS:
        pattern_info = DIVISION_PATTERNS[division]
        if pattern_info['pattern'] == 'ALL_CAPS':
            # Check if this cert is in the affected list
            return cert_name in pattern_info['affected_certs']
    
    return False


if __name__ == '__main__':
    # Test examples
    print("Certification Name Normalization Module - Test Examples")
    print("=" * 80)
    
    test_cases = [
        ('CTAA PASSENGER ASSISTANCE', 'CTAA Passenger Assistance'),
        ('Defensive Driving', 'Defensive Driving '),
        ('SOCIAL SECURITY CARD', 'Social Security Card'),
        ('Background Check', 'BACKGROUND CHECK'),
    ]
    
    print("\nMatching Tests:")
    for cert1, cert2 in test_cases:
        match = certs_match(cert1, cert2)
        print(f"  '{cert1}' == '{cert2}': {match}")
    
    print("\nCanonical Name Lookup:")
    for cert1, cert2 in test_cases:
        canonical = get_canonical_name(cert1)
        print(f"  '{cert1}' → '{canonical}'")
    
    print("\nValidation Tests:")
    test_names = ['CTAA PASSENGER ASSISTANCE', 'CTAA Passenger Assistance', 'Defensive Driving ']
    for name in test_names:
        result = validate_cert_name(name)
        print(f"\n  '{name}':")
        print(f"    Canonical: {result['is_canonical']}")
        print(f"    Recommendation: {result['recommendation']}")
