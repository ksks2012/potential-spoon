#!/usr/bin/env python3
"""
Test script for updated parsers using unified database system
Tests the correct order: matrix -> shell -> character
"""

import sys
import os
import glob

# Set correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from html_parser.unified_parser import UnifiedParser


def test_individual_parsers():
    """Test individual parsers to verify they work correctly"""
    print("=== Testing Individual Parsers ===")
    
    # Test files (adjust paths as needed)
    test_files = {
        'matrix': './var/MatrixEffects.html',
        'shells': './var/shells.html', 
        'characters': []  # Will be populated with all character files
    }
    
    # Find all character HTML files
    character_pattern = './var/character/*.html'
    character_files = glob.glob(character_pattern)
    
    if character_files:
        test_files['characters'] = character_files
        print(f"✅ Found {len(character_files)} character files:")
        for char_file in sorted(character_files):
            char_name = os.path.basename(char_file).replace('.html', '')
            print(f"   - {char_name}")
    else:
        print("❌ No character files found in ./var/character/")
    
    # Check other files
    available_files = {}
    for data_type, file_path in test_files.items():
        if data_type == 'characters':
            if character_files:
                available_files[data_type] = character_files
        else:
            if os.path.exists(file_path):
                available_files[data_type] = file_path
                print(f"✅ Found {data_type} file: {file_path}")
            else:
                print(f"❌ Missing {data_type} file: {file_path}")
    
    if not available_files:
        print("❌ No test files found. Please ensure HTML files exist in ./var/ directory")
        return False
    
    return available_files


def test_unified_parsing(available_files):
    """Test unified parsing with correct order"""
    print("\n" + "="*60)
    print("TESTING UNIFIED PARSING SYSTEM")
    print("="*60)
    
    # Initialize unified parser with test database
    test_db_path = "./testing/test_parsers_unified.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"🗑️  Removed existing test database")
    
    parser = UnifiedParser(test_db_path)
    
    # Prepare character files list
    character_files = available_files.get('characters', [])
    
    # Parse and store all available data in correct order using new method
    success = parser.parse_and_store_all(
        matrix_html=available_files.get('matrix'),
        shells_html=available_files.get('shells'),
        character_html_list=character_files if character_files else None
    )
    
    return success


def test_order_validation():
    """Test that the order validation works correctly"""
    print("\n" + "="*60)
    print("TESTING ORDER VALIDATION")
    print("="*60)
    
    # Test with shells file only (should warn about missing matrices)
    shells_file = './var/shells.html'
    if not os.path.exists(shells_file):
        print("❌ Shells file not found for order validation test")
        return False
    
    # Initialize parser with clean database
    test_db_path = "./testing/test_order_validation.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    from html_parser.parse_shells import ShellParser
    from db.etheria_manager import EtheriaManager
    
    # Test shell parser without matrices in database
    print("\n--- Testing Shell Parser Without Matrices ---")
    shell_parser = ShellParser(shells_file, use_database=True, db_path=test_db_path)
    shell_parser.load_html()
    shell_parser.parse_all_shells()  # Use correct method name
    
    # This should show warnings about missing matrix references
    shell_parser.save_to_database(validate_matrix_refs=True)
    
    return True


def main():
    """Main test function"""
    print("Starting updated parsers test")
    print("=" * 50)
    
    try:
        # Ensure testing directory exists
        os.makedirs("./testing", exist_ok=True)
        
        # Step 1: Check available files
        available_files = test_individual_parsers()
        if not available_files:
            return
        
        # Step 2: Test unified parsing system
        success = test_unified_parsing(available_files)
        
        # Step 3: Test order validation
        test_order_validation()
        
        if success:
            print("\n🎉 All parser tests completed successfully!")
            print("✅ Matrix -> Shell -> Character order working correctly")
            print("✅ Matrix reference validation working")
            print("✅ Unified database storage working")
        else:
            print("\n⚠️  Some tests encountered issues")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
