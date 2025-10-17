#!/usr/bin/env python3
"""
Comprehensive testing suite for shells parser
Runs all shell parsing tests and validates complete functionality
"""
import os
import sys
import json
import subprocess

def run_test_script(script_name, html_file):
    """Run a specific test script and return success status"""
    try:
        result = subprocess.run([
            sys.executable, script_name, html_file
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR running {script_name}: {e}")
        return False

def validate_parsed_output(json_file):
    """Validate the final parsed JSON output"""
    print("=== Validating Final Parser Output ===")
    
    if not os.path.exists(json_file):
        print(f"✗ FAIL: Output file not found: {json_file}")
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ JSON file loaded successfully")
        print(f"  Total shells: {len(data)}")
        
        # Validate data completeness
        required_fields = ['name', 'rarity', 'class', 'cooldown', 'skills', 'stats', 'sets']
        skill_fields = ['awakened', 'non_awakened']
        stat_fields = ['HP', 'DEF', 'ATK', 'SPD']
        
        pass_count = 0
        total_shells = len(data)
        
        for i, shell in enumerate(data):
            shell_pass = True
            
            # Check required fields
            for field in required_fields:
                if field not in shell:
                    print(f"  ✗ Shell {i+1} ({shell.get('name', 'Unknown')}): Missing field '{field}'")
                    shell_pass = False
            
            # Check skills structure
            if 'skills' in shell:
                for skill_field in skill_fields:
                    if skill_field not in shell['skills']:
                        print(f"  ✗ Shell {i+1}: Missing skill '{skill_field}'")
                        shell_pass = False
            
            # Check stats structure  
            if 'stats' in shell:
                for stat_field in stat_fields:
                    if stat_field not in shell['stats']:
                        print(f"  ✗ Shell {i+1}: Missing stat '{stat_field}'")
                        shell_pass = False
            
            # Check sets
            if 'sets' in shell:
                if not shell['sets'] or len(shell['sets']) == 0:
                    print(f"  ✗ Shell {i+1}: Empty sets list")
                    shell_pass = False
            
            if shell_pass:
                pass_count += 1
        
        print(f"\n=== Output Validation Summary ===")
        print(f"Shells passed validation: {pass_count}/{total_shells}")
        print(f"Validation result: {'✓ PASS' if pass_count == total_shells else '✗ FAIL'}")
        
        # Show sample data
        if data:
            print(f"\nSample shell data ({data[0]['name']}):")
            sample = {k: v for k, v in data[0].items()}
            if 'skills' in sample:
                # Truncate skills for display
                for skill_type in sample['skills']:
                    if len(sample['skills'][skill_type]) > 100:
                        sample['skills'][skill_type] = sample['skills'][skill_type][:100] + "..."
            print(json.dumps(sample, indent=2, ensure_ascii=False))
        
        return pass_count == total_shells
    
    except Exception as e:
        print(f"✗ FAIL: Error validating output: {e}")
        return False

def run_complete_test_suite(html_file, output_file):
    """Run complete testing suite for shells parser"""
    print("=== Shells Parser Complete Test Suite ===")
    print(f"HTML file: {html_file}")
    print(f"Expected output: {output_file}\n")
    
    test_results = {}
    
    # Test 1: Structure validation
    print("1. Testing shell structure...")
    test_results['structure'] = run_test_script('testing_shell_structure.py', html_file)
    
    # Test 2: Skills extraction
    print("\n2. Testing skills extraction...")
    test_results['skills'] = run_test_script('testing_skills_extraction.py', html_file)
    
    # Test 3: Matrix sets extraction
    print("\n3. Testing matrix sets extraction...")
    test_results['matrix'] = run_test_script('testing_matrix_sets.py', html_file)
    
    # Test 4: Run actual parser
    print("\n4. Running actual parser...")
    try:
        parser_path = os.path.join(os.path.dirname(__file__), '..', 'html_parser', 'parse_shells.py')
        result = subprocess.run([
            sys.executable, parser_path, html_file
        ], capture_output=True, text=True, cwd=os.path.dirname(parser_path))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        test_results['parser'] = result.returncode == 0
    except Exception as e:
        print(f"ERROR running parser: {e}")
        test_results['parser'] = False
    
    # Test 5: Validate output
    print("\n5. Validating parser output...")
    test_results['output'] = validate_parsed_output(output_file)
    
    # Final summary
    print("\n=== Test Suite Summary ===")
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name.capitalize()} test: {status}")
    
    print(f"\nOverall result: {passed}/{total} tests passed")
    print(f"Suite status: {'✓ ALL TESTS PASSED' if passed == total else '✗ SOME TESTS FAILED'}")
    
    return passed == total

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testing_shells_parser_suite.py <html_file> <output_json_file>")
        print("Example: python testing_shells_parser_suite.py ../var/shells.html ../shells_parsed.json")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = run_complete_test_suite(html_file, output_file)
    sys.exit(0 if success else 1)
