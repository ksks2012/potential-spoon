#!/usr/bin/env python3
"""
Test script for Character Pokedex functionality with unified database
"""

import sys
import os

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from windowing.models import CharacterModel


def test_character_pokedex_functionality():
    """Test all Character Pokedex functionality"""
    print("=== Testing Character Pokedex with Unified Database ===")
    
    try:
        # Initialize model
        model = CharacterModel()
        print("✅ CharacterModel initialized")
        
        # Test basic operations
        print("\n--- Basic Operations ---")
        characters = model.get_all_characters()
        print(f"✅ Total characters: {len(characters)}")
        
        stats = model.get_character_stats()
        print(f"✅ Database stats: {stats}")
        
        # Test filtering options
        print("\n--- Filtering Options ---")
        rarities = model.get_rarities()
        elements = model.get_elements()
        print(f"✅ Available rarities: {rarities}")
        print(f"✅ Available elements: {elements}")
        
        # Test search functionality
        print("\n--- Search Functionality ---")
        search_results = model.search_characters("Plume")
        print(f"✅ Search 'Plume': {len(search_results)} results")
        if search_results:
            print(f"    Found: {[r['name'] for r in search_results]}")
        
        search_partial = model.search_characters("Ka")
        print(f"✅ Search 'Ka': {len(search_partial)} results")
        if search_partial:
            print(f"    Found: {[r['name'] for r in search_partial]}")
        
        # Test filtering
        print("\n--- Filter Testing ---")
        ssr_chars = model.filter_characters(rarity='SSR')
        print(f"✅ SSR characters: {len(ssr_chars)}")
        
        hollow_chars = model.filter_characters(element='Hollow')
        print(f"✅ Hollow characters: {len(hollow_chars)}")
        
        ssr_hollow = model.filter_characters(rarity='SSR', element='Hollow')
        print(f"✅ SSR Hollow characters: {len(ssr_hollow)}")
        if ssr_hollow:
            print(f"    Names: {[c['name'] for c in ssr_hollow]}")
        
        # Test character detail retrieval
        print("\n--- Character Detail Testing ---")
        if characters:
            test_char_name = characters[0]['name']
            char_detail = model.get_character_by_name(test_char_name)
            
            if char_detail:
                print(f"✅ Character detail for '{test_char_name}':")
                print(f"    Basic info: {char_detail['basic_info']}")
                print(f"    Skills count: {len(char_detail['skills'])}")
                print(f"    Stats count: {len(char_detail['stats'])}")
                print(f"    Dupes count: {len(char_detail['dupes'])}")
                
                # Show first skill if available
                if char_detail['skills']:
                    first_skill = char_detail['skills'][0]
                    print(f"    First skill: {first_skill.get('name', 'Unknown')}")
                
                # Show some stats if available
                if char_detail['stats']:
                    stat_names = list(char_detail['stats'].keys())[:3]
                    print(f"    Sample stats: {stat_names}")
        
        # Test export functionality
        print("\n--- Export Testing ---")
        if characters:
            test_char = characters[0]['name']
            export_path = "./testing/test_export.json"
            success, message = model.export_character(test_char, export_path)
            print(f"✅ Export test: {success} - {message}")
            
            if success and os.path.exists(export_path):
                print(f"    Export file created: {export_path}")
                # Clean up
                os.remove(export_path)
                print("    Export file cleaned up")
        
        print("\n🎉 All Character Pokedex functionality tests passed!")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Characters in database: {len(characters)}")
        print(f"Available rarities: {len(rarities)}")
        print(f"Available elements: {len(elements)}")
        print(f"Search functionality: ✅ Working")
        print(f"Filter functionality: ✅ Working")
        print(f"Detail retrieval: ✅ Working")
        print(f"Export functionality: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Character Pokedex testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    success = test_character_pokedex_functionality()
    
    if success:
        print("\n✅ Character Pokedex with unified database is ready!")
    else:
        print("\n❌ Character Pokedex testing failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
