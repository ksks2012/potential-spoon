#!/usr/bin/env python3
"""
Testing script for matrix sets parsing functionality
Tests matrix set extraction and image source parsing
"""
import os
import sys
from bs4 import BeautifulSoup
import re

def test_matrix_sets_extraction(html_file):
    """Test matrix sets extraction logic"""
    
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
    
    # Find first shell element
    shell_element = soup.find('div', class_='single-shell')
    
    if shell_element:
        print("=== Matrix Sets Extraction Test Results ===")
        
        # Check sets section
        sets_div = shell_element.find('div', class_='eth-shell-sets')
        print(f"Sets section found: {sets_div is not None}")
        
        if sets_div:
            print("Matrix sets parsing analysis:")
            
            # Check all div children
            all_divs = sets_div.find_all('div')
            print(f"  Total divs in sets section: {len(all_divs)}")
            
            # Look for set names in different ways
            set_divs = sets_div.find_all('div', class_='single-set')
            print(f"  Single-set elements found: {len(set_divs)}")
            
            extracted_sets = []
            
            for i, set_div in enumerate(set_divs):
                print(f"\n  Testing Set {i+1}:")
                
                # Test noscript method (primary)
                noscript_elem = set_div.find('noscript')
                if noscript_elem:
                    noscript_img = noscript_elem.find('img')
                    if noscript_img:
                        src = noscript_img.get('src', '')
                        if 'set_' in src:
                            set_name = src.split('set_')[-1].split('.webp')[0]
                            extracted_sets.append(set_name.capitalize())
                            print(f"    ✓ Extracted via noscript: '{set_name.capitalize()}'")
                        else:
                            print(f"    ✗ No 'set_' in noscript src: '{src[:50]}...'")
                    else:
                        print(f"    ✗ No img in noscript")
                else:
                    print(f"    ⚠ No noscript element")
                
                # Test fallback methods
                if not noscript_elem:
                    img_elem = set_div.find('img')
                    if img_elem:
                        for attr in ['data-lazy-src', 'data-src', 'src']:
                            src = img_elem.get(attr, '')
                            if 'set_' in src:
                                set_name = src.split('set_')[-1].split('.webp')[0]
                                extracted_sets.append(set_name.capitalize())
                                print(f"    ✓ Extracted via {attr}: '{set_name.capitalize()}'")
                                break
                        else:
                            print(f"    ✗ No 'set_' found in any img attribute")
                    else:
                        print(f"    ✗ No img element found")
                
                # Additional debugging info
                text_content = set_div.get_text(strip=True)
                if text_content:
                    print(f"    Text content: '{text_content[:30]}...'")
                
                classes = set_div.get('class', [])
                print(f"    Classes: {classes}")
            
            print(f"\n=== Matrix Sets Test Summary ===")
            print(f"Expected sets count: 8")
            print(f"Actually extracted: {len(extracted_sets)}")
            print(f"Extracted sets: {extracted_sets}")
            print(f"Test result: {'✓ PASS' if len(extracted_sets) >= 6 else '✗ FAIL'}")
            
            return len(extracted_sets) >= 6
        else:
            print("✗ FAIL: No sets section found")
            return False
    else:
        print("✗ FAIL: No shell element found")
        return False

def test_set_name_extraction():
    """Test set name extraction logic independently"""
    print("\n=== Set Name Extraction Logic Test ===")
    
    test_urls = [
        "/static/60e7a17a8840bb49201c7501657fb75a/0c531/set_wellspring.webp",
        "/static/75042f673d31984fc8ed35214f814445/0c531/set_bramble.webp", 
        "/static/d6b7aedc2b821ecf46fb030ea397cf0f/0c531/set_bloodbath.webp",
        "/some/path/set_colossguard.webp",
        "invalid_url_without_set",
        "/path/set_strive.png"
    ]
    
    for url in test_urls:
        print(f"Testing URL: '{url}'")
        if 'set_' in url:
            if '.webp' in url:
                set_name = url.split('set_')[-1].split('.webp')[0]
            elif '.png' in url:
                set_name = url.split('set_')[-1].split('.png')[0] 
            else:
                set_name = url.split('set_')[-1]
            print(f"  ✓ Extracted: '{set_name.capitalize()}'")
        else:
            print(f"  ✗ No 'set_' pattern found")
        print()

def run_matrix_tests(html_file):
    """Run all matrix sets extraction tests"""
    print("Starting matrix sets extraction validation tests...")
    
    if not os.path.exists(html_file):
        print(f"ERROR: HTML file not found: {html_file}")
        return False
    
    try:
        # Test extraction logic first
        test_set_name_extraction()
        
        # Test actual extraction
        result = test_matrix_sets_extraction(html_file)
        print(f"\nMatrix sets extraction test result: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"ERROR during matrix sets testing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python testing_matrix_sets.py <html_file>")
        sys.exit(1)
    
    success = run_matrix_tests(sys.argv[1])
    sys.exit(0 if success else 1)
