#!/usr/bin/env python3
"""
Testing script for skills extraction functionality
Tests awakened and non-awakened skill parsing logic
"""
import os
import sys
from bs4 import BeautifulSoup
import re

def test_skills_extraction(html_file):
    """Test skills extraction logic in detail"""
    
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
    
    # Find first shell element
    shell_element = soup.find('div', class_='single-shell')
    
    if shell_element:
        print("=== Skills Extraction Test Results ===")
        
        # Find the skill tab content
        skill_tab = shell_element.find('div', role='tabpanel', id=re.compile(r'.*-tabpane-skill'))
        print(f"Skill tab found: {skill_tab is not None}")
        
        if skill_tab:
            print("Skills parsing analysis:")
            
            # Find all h5 elements (no class filter)
            h5_elements = skill_tab.find_all('h5')
            print(f"  H5 elements found: {len(h5_elements)}")
            
            awakened_found = False
            non_awakened_found = False
            
            for i, h5 in enumerate(h5_elements):
                h5_text = h5.get_text(strip=True)
                print(f"\n  Testing H5 {i+1}: '{h5_text}'")
                
                # Test awakened skill detection
                if 'Non-Awakened' in h5_text:
                    print("    -> Detected as NON-AWAKENED skill")
                    non_awakened_found = True
                    skill_div = h5.find_next_sibling('div', class_='skill-with-coloring')
                    if skill_div:
                        skill_text = skill_div.get_text(strip=True)[:100]
                        print(f"       ✓ Skill content found: '{skill_text}...'")
                    else:
                        print("       ✗ No skill content found")
                        # Debug next siblings
                        next_siblings = list(h5.next_siblings)
                        print(f"       Debug: {len([s for s in next_siblings if hasattr(s, 'name')])} siblings")
                
                elif 'Awakened' in h5_text:
                    print("    -> Detected as AWAKENED skill")
                    awakened_found = True
                    skill_div = h5.find_next_sibling('div', class_='skill-with-coloring')
                    if skill_div:
                        skill_text = skill_div.get_text(strip=True)[:100]
                        print(f"       ✓ Skill content found: '{skill_text}...'")
                    else:
                        print("       ✗ No skill content found")
                        # Debug next siblings
                        next_siblings = list(h5.next_siblings)
                        print(f"       Debug: {len([s for s in next_siblings if hasattr(s, 'name')])} siblings")
            
            print(f"\n=== Skills Test Summary ===")
            print(f"Awakened skill detected: {'✓ PASS' if awakened_found else '✗ FAIL'}")
            print(f"Non-Awakened skill detected: {'✓ PASS' if non_awakened_found else '✗ FAIL'}")
            
            return awakened_found and non_awakened_found
        else:
            print("✗ FAIL: No skill tab found")
            return False
    else:
        print("✗ FAIL: No shell element found")
        return False

def test_skill_parsing_logic():
    """Test the skill detection logic independently"""
    print("\n=== Skill Detection Logic Test ===")
    
    test_cases = [
        "Skill[Awakened]",
        "Skill[Non-Awakened]", 
        "Some other text",
        "Awakened Skill",
        "Non-Awakened Skill"
    ]
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        
        # Test original logic (problematic)
        if 'Awakened' in test_text:
            print(f"  Original logic: Detected as AWAKENED")
        elif 'Non-Awakened' in test_text:
            print(f"  Original logic: Detected as NON-AWAKENED")
        else:
            print(f"  Original logic: Not detected")
        
        # Test corrected logic
        if 'Non-Awakened' in test_text:
            print(f"  Corrected logic: Detected as NON-AWAKENED ✓")
        elif 'Awakened' in test_text:
            print(f"  Corrected logic: Detected as AWAKENED ✓")
        else:
            print(f"  Corrected logic: Not detected")
        print()

def run_skills_tests(html_file):
    """Run all skills extraction tests"""
    print("Starting skills extraction validation tests...")
    
    if not os.path.exists(html_file):
        print(f"ERROR: HTML file not found: {html_file}")
        return False
    
    try:
        # Test logic first
        test_skill_parsing_logic()
        
        # Test actual extraction
        result = test_skills_extraction(html_file)
        print(f"\nSkills extraction test result: {'PASS' if result else 'FAIL'}")
        return result
    except Exception as e:
        print(f"ERROR during skills testing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python testing_skills_extraction.py <html_file>")
        sys.exit(1)
    
    success = run_skills_tests(sys.argv[1])
    sys.exit(0 if success else 1)
