#!/usr/bin/env python3
"""
Simplified integrated database test
"""

import sys
import os

# Set correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.etheria_manager import EtheriaManager
import json


def test_basic_functionality():
    """Test basic functionality"""
    print("=== Basic functionality test ===")
    
    # Use a temporary database
    test_db_path = "./testing/test_simple.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    manager = EtheriaManager(test_db_path)
    
    # Test database statistics
    stats = manager.get_comprehensive_stats()
    print(f"Initial database stats: {stats['database']['total_characters']} characters")
    
    # Test character insertion (correct data structure)
    test_character = {
        'basic_info': {
            'name': 'Test Character',
            'rarity': 'SSR',
            'element': 'Fire'
        },
        'stats': {
            'hp': {'base': 5000, 'bonus': 500},
            'attack': {'base': 800, 'bonus': 80}
        },
        'skills': [
            {'name': 'Test Skill', 'type': 'normal', 'description': 'Test skill description'}
        ]
    }
    
    char_id = manager.characters.insert_character(test_character)
    print(f"Character insert ID: {char_id}")
    
    # Test matrix insertion (correct data structure)
    test_matrix = {
        'name': 'Test Matrix',
        'source': 'Testing',
        'type': ['Attack'],
        'effects': [
            {
                'required': 2,
                'total': 4,
                'extra_effect': '+10% ATK',
                'effect': {
                    'attack': 100
                }
            }
        ]
    }
    
    matrix_id = manager.matrices.insert_matrix_effect(test_matrix)
    print(f"Matrix insert ID: {matrix_id}")
    
    # Test shell insertion (correct data structure)
    test_shell = {
        'name': 'Test Shell',
        'rarity': 'SSR',
        'class': 'DPS',
        'cooldown': 30,
        'skills': {
            'awakened': [{'name': 'Awakened Skill', 'description': 'Test skill'}],
            'non_awakened': [{'name': 'Normal Skill', 'description': 'Normal test skill'}]
        },
        'stats': {
            'hp': 500,
            'attack': 100
        },
        'sets': ['Test Set']
    }
    
    shell_id = manager.shells.insert_shell(test_shell)
    print(f"Shell insert ID: {shell_id}")
    
    # Final statistics
    final_stats = manager.get_comprehensive_stats()
    print("Final statistics:")
    print(f"  Characters: {final_stats['database']['total_characters']}")
    print(f"  Matrices: {final_stats['database']['total_matrix_effects']}")
    print(f"  Shells: {final_stats['database']['total_shells']}")
    
    return char_id, matrix_id, shell_id


def test_relationships():
    """Test relationships functionality"""
    print("\n=== Relationships test ===")
    
    # Recreate manager to use the same database
    manager = EtheriaManager("./testing/test_simple.db")
    
    # Get existing IDs
    char_result = manager.db.execute_query('SELECT id FROM characters LIMIT 1')
    matrix_result = manager.db.execute_query('SELECT id FROM matrix_effects LIMIT 1')
    shell_result = manager.db.execute_query('SELECT id FROM shells LIMIT 1')
    
    if char_result and matrix_result and shell_result:
        char_id = char_result[0]['id']
        matrix_id = matrix_result[0]['id']
        shell_id = shell_result[0]['id']
        
        # Test matrix compatibility
        success = manager.shells.add_matrix_compatibility(shell_id, matrix_id, 95.0)
        print(f"Matrix compatibility: {'✅' if success else '❌'}")
        
        # Test integration statistics
        stats = manager.get_comprehensive_stats()
        print(f"Integration stats: {stats['integration']}")
    else:
        print("❌ Test data not found")


def main():
    """Main test function"""
    print("Starting simplified test")
    print("=" * 40)
    
    try:
        # Ensure test directory exists
        os.makedirs("./testing", exist_ok=True)
        
        char_id, matrix_id, shell_id = test_basic_functionality()
        
        if all([char_id, matrix_id, shell_id]):
            test_relationships()
            print("\n🎉 Simplified test completed")
        else:
            print("\n❌ Basic insertion test failed")
            print(f"Character ID: {char_id}, Matrix ID: {matrix_id}, Shell ID: {shell_id}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
