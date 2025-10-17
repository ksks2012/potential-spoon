#!/usr/bin/env python3
"""
Testing script for shell HTML structure analysis
Tests basic shell parsing functionality and structure validation
"""
import os
import sys
from bs4 import BeautifulSoup
import re

def test_shell_structure(html_file):
    """Test shell structure to validate parsing logic"""
    
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
    
    # Find first shell element
    shell_element = soup.find('div', class_='single-shell')
    
    if shell_element:
        print("=== Shell Structure Test Results ===")
        
        # Test basic info extraction
        name_elem = shell_element.find('h4')
        print(f"Name element found: {name_elem is not None}")
        if name_elem:
            print(f"  Name: {name_elem.get_text(strip=True)}")
        
        # Test skill tab structure
        skill_tab = shell_element.find('div', role='tabpanel', id=re.compile(r'.*-tabpane-skill'))
        print(f"Skill tab found: {skill_tab is not None}")
        
        if skill_tab:
            print("Skill tab analysis:")
            h5_elements = skill_tab.find_all('h5')
            print(f"  H5 elements count: {len(h5_elements)}")
            
            for i, h5 in enumerate(h5_elements):
                h5_text = h5.get_text(strip=True)
                print(f"    H5 {i+1}: '{h5_text}'")
                # Check next sibling
                next_div = h5.find_next_sibling('div', class_='skill-with-coloring')
                if next_div:
                    skill_text = next_div.get_text(strip=True)[:100]
                    print(f"      -> Skill text preview: {skill_text}...")
                else:
                    print(f"      -> No skill div found")
        
        # Test sets section structure  
        sets_div = shell_element.find('div', class_='eth-shell-sets')
        print(f"Sets section found: {sets_div is not None}")
        
        if sets_div:
            print("Sets structure analysis:")
            set_divs = sets_div.find_all('div', class_='single-set')
            print(f"  Set elements count: {len(set_divs)}")
            
            for i, set_div in enumerate(set_divs):
                img_elem = set_div.find('img')
                if img_elem:
                    src = img_elem.get('src', '')
                    alt = img_elem.get('alt', '')
                    print(f"    Set {i+1}: src available={bool(src)}, alt='{alt}'")
        
        print("=== Structure Test Complete ===")
        return True
    else:
        print("ERROR: No shell elements found")
        return False

def run_structure_tests(html_file):
    """Run all shell structure tests"""
    print("Starting shell structure validation tests...")
    
    if not os.path.exists(html_file):
        print(f"ERROR: HTML file not found: {html_file}")
        return False
    
    try:
        result = test_shell_structure(html_file)
        print(f"Structure test result: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"ERROR during structure testing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python testing_shell_structure.py <html_file>")
        sys.exit(1)
    
    success = run_structure_tests(sys.argv[1])
    sys.exit(0 if success else 1)
