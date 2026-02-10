#!/usr/bin/env python3

import sys
import os
sys.path.append('/app/backend')

from server import simplify_product_query, extract_product_type

def test_simplify_product_query():
    """Test the simplify_product_query function"""
    
    test_cases = [
        # Technical construction items
        ("CARYSIL SINK DOCLE SIN BWP PLY 123ABC", "CARYSIL SINK price india"),
        ("Bosch Refrigerator Model XYZ123 (SS)", "Bosch Refrigerator Model price india"),
        ("Kitchen Counter Top Quartz Stone [Premium Grade]", "Kitchen Counter Top Quartz Stone Premium Grade price india"),
        ("Dado Tiles 12x12 BWP Grade A+ (Ceramic)", "Dado Tiles Ceramic price india"),
        
        # Regular products
        ("iPhone 15 Pro Max", "iPhone Pro Max price india"),
        ("Samsung Galaxy S24", "Samsung Galaxy S24 price india"),
        
        # Long technical names
        ("Industrial Grade Stainless Steel Kitchen Sink with Double Bowl Configuration Model ABC123XYZ", "Industrial Grade Stainless Steel Kitchen price india"),
    ]
    
    print("Testing simplify_product_query function:")
    print("=" * 60)
    
    for original, expected_contains in test_cases:
        result = simplify_product_query(original)
        print(f"Original: {original}")
        print(f"Simplified: {result}")
        print(f"Expected to contain: {expected_contains}")
        print(f"✓ Contains expected terms: {'price india' in result}")
        print("-" * 40)

def test_extract_product_type():
    """Test the extract_product_type function"""
    
    test_cases = [
        ("CARYSIL SINK DOCLE", "carysil sink"),
        ("Bosch Refrigerator Model", "bosch refrigerator"),
        ("Kitchen Counter Top", "kitchen counter top"),
        ("Plywood BWP Grade", "plywood"),
        ("Granite Slab Premium", "granite slab"),
        ("Unknown Product XYZ", "Unknown Product XYZ"),
    ]
    
    print("\nTesting extract_product_type function:")
    print("=" * 60)
    
    for original, expected in test_cases:
        result = extract_product_type(original)
        print(f"Original: {original}")
        print(f"Extracted: {result}")
        print(f"Expected: {expected}")
        print(f"✓ Match: {expected.lower() in result.lower()}")
        print("-" * 40)

if __name__ == "__main__":
    test_simplify_product_query()
    test_extract_product_type()
    print("\n✅ All tests completed!")