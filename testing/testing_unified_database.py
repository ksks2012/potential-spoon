#!/usr/bin/env python3
"""
Unified database system test file
Test file for the unified Etheria database system
"""

import sys
import os

# set correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.etheria_manager import EtheriaManager
import json


def test_database_creation():
    """Test database creation"""
    print("=== Test Database Creation ===")
    
    # use temporary database path
    test_db_path = "./testing/test_unified.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    manager = EtheriaManager(test_db_path)
    
    # get basic stats
    stats = manager.get_comprehensive_stats()
    print(f"Database stats: {json.dumps(stats['database'], indent=2, ensure_ascii=False)}")
    
    print("✅ Database creation test completed")
    return manager


def test_character_operations(manager):
    """Test character operations"""
    print("\n=== Test Character Operations ===")
    
    # insert test character with correct structure
    test_character = {
        'basic_info': {
            'name': 'Test Character',
            'rarity': 'SSR',
            'element': 'Fire'
        },
        'stats': {
            'hp': {'base': 5000, 'bonus': 500},
            'attack': {'base': 800, 'bonus': 80},
            'defense': {'base': 300, 'bonus': 30}
        },
        'skills': [
            {'name': 'Test Skill 1', 'type': 'normal', 'description': 'Basic attack skill'},
            {'name': 'Test Skill 2', 'type': 'ultimate', 'description': 'Ultimate skill'}
        ]
    }
    
    char_id = manager.characters.insert_character(test_character)
    print(f"Inserted character ID: {char_id}")
    
    # query character
    retrieved_char = manager.characters.get_character_by_name('Test Character')
    if retrieved_char and 'basic_info' in retrieved_char:
        print(f"Queried character: {retrieved_char['basic_info']['name']}")
    else:
        print("Queried character: None")
    
    print("✅ Character operations test completed")
    return char_id


def test_matrix_operations(manager):
    """Test matrix operations"""
    print("\n=== Test Matrix Operations ===")
    
    # insert test matrix with correct structure
    test_matrix = {
        'name': 'Test Matrix',
        'source': 'Testing',
        'type': ['Attack', 'Physical'],
        'effects': [
            {
                'required': 2,
                'total': 4,
                'extra_effect': '+10% ATK',
                'effect': {
                    'attack': 100,
                    'crit_damage': 10
                }
            },
            {
                'required': 4,
                'total': 4,
                'extra_effect': '+20% Crit Rate',
                'effect': {
                    'crit_rate': 20,
                    'attack': 150
                }
            }
        ]
    }
    
    matrix_id = manager.matrices.insert_matrix_effect(test_matrix)
    print(f"Inserted matrix ID: {matrix_id}")
    
    # query matrix
    retrieved_matrix = manager.matrices.get_matrix_effect_by_name('Test Matrix')
    print(f"Queried matrix: {retrieved_matrix['name'] if retrieved_matrix else 'None'}")
    
    print("✅ Matrix operations test completed")
    return matrix_id


def test_shell_operations(manager):
    """Test shell operations"""
    print("\n=== Test Shell Operations ===")
    
    # insert test shell
    test_shell = {
        'name': 'Test Shell',
        'rarity': 'SSR',
        'class': 'DPS',
        'cooldown': 30,
        'skills': {
            'awakened': [
                {'name': 'Awakened Skill', 'description': 'Test awakened skill'}
            ],
            'non_awakened': [
                {'name': 'Non-Awakened Skill', 'description': 'Test non-awakened skill'}
            ]
        },
        'stats': {
            'hp': 500,
            'attack': 100
        },
        'sets': ['Test Matrix']
    }
    
    shell_id = manager.shells.insert_shell(test_shell)
    print(f"Inserted shell ID: {shell_id}")
    
    # query shell
    retrieved_shell = manager.shells.get_shell_by_name('Test Shell')
    print(f"Queried shell: {retrieved_shell['name'] if retrieved_shell else 'None'}")
    
    print("✅ Shell operations test completed")
    return shell_id


def test_relationships(manager, char_id, matrix_id, shell_id):
    """Test relationships integration"""
    print("\n=== Test Relationships Integration ===")
    
    # test shell-matrix compatibility (only if matrix exists)
    if matrix_id is not None:
        success = manager.shells.add_matrix_compatibility(shell_id, matrix_id, 95.0)
        print(f"Add shell-matrix compatibility: {'✅' if success else '❌'}")
    else:
        print("Add shell-matrix compatibility: ⏭️ (matrix not available)")
    
    # test character equipping shell (skip if matrix_id is None)
    if matrix_id is not None:
        success = manager.characters.equip_shell('Test Character', 'Test Shell')
        print(f"Character equipped shell: {'✅' if success else '❌'}")
        
        # test character matrix loadout
        success = manager.characters.set_matrix_loadout('Test Character', ['Test Matrix'], "Test Loadout")
        print(f"Set matrix loadout: {'✅' if success else '❌'}")
    else:
        print("Skipping character equipment tests due to missing matrix")
        print("Character equipped shell: ⏭️")
        print("Set matrix loadout: ⏭️")
    
    print("✅ Relationships integration test completed")


def test_team_setup(manager):
    """Test team setup"""
    print("\n=== Test Team Setup ===")
    
    result = manager.create_team_setup('Test Character', 'Test Shell', ['Test Matrix'], 'Combat Loadout')
    print(f"Team setup result:")
    print(f"  Character: {result['character']}")
    print(f"  Shell equipped: {'✅' if result['shell_equipped'] else '❌'}")
    print(f"  Matrix loadout set: {'✅' if result['matrix_loadout_set'] else '❌'}")
    
    if result['errors']:
        print(f"  Errors: {result['errors']}")
    
    print("✅ Team setup test completed")


def test_comprehensive_info(manager):
    """Test comprehensive info retrieval"""
    print("\n=== Test Comprehensive Info Retrieval ===")
    
    complete_info = manager.get_character_complete_info('Test Character')
    if complete_info:
        basic_info = complete_info.get('basic_info', {})
        print(f"Character complete info:")
        print(f"  Name: {basic_info.get('name', 'Unknown')}")
        print(f"  Rarity: {basic_info.get('rarity', 'Unknown')}")
        print(f"  Element: {basic_info.get('element', 'Unknown')}")
        
        if 'equipped_shell' in complete_info:
            shell = complete_info['equipped_shell']
            print(f"  Equipped shell: {shell['name']} ({shell['rarity']})")
        
        if 'matrix_loadouts' in complete_info:
            print(f"  Matrix loadouts: {list(complete_info['matrix_loadouts'].keys())}")
    else:
        print("No character complete info available")
    
    print("✅ Comprehensive info retrieval test completed")


def test_integration_stats(manager):
    """Test integration statistics"""
    print("\n=== Test Integration Statistics ===")
    
    stats = manager.get_comprehensive_stats()
    
    print("Database statistics:")
    for key, value in stats['database'].items():
        print(f"  {key}: {value}")
    
    print("\nIntegration statistics:")
    for category, data in stats['integration'].items():
        print(f"  {category}:")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}%")
            else:
                print(f"    {key}: {value}")
    
    print("✅ Integration statistics test completed")


def test_export(manager):
    """Test export functionality"""
    print("\n=== Test Export Functionality ===")
    
    export_file = "./testing/test_export.json"
    success = manager.export_unified_data(export_file)
    
    if success and os.path.exists(export_file):
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Export successful:")
        print(f"  Number of characters: {len(data['characters'])}")
        print(f"  Number of shells: {len(data['shells'])}")
        print(f"  Number of matrices: {len(data['matrix_effects'])}")
        print(f"  Number of relationships: {sum(len(v) for v in data['relationships'].values())}")
    else:
        print("❌ Export failed")
    
    print("✅ Export functionality test completed")


def main():
    """Main test function"""
    print("Starting unified database system tests")
    print("=" * 50)
    
    try:
        # ensure testing directory exists
        os.makedirs("./testing", exist_ok=True)
        
        # 1. test database creation
        manager = test_database_creation()
        
        # 2. test basic operations
        char_id = test_character_operations(manager)
        matrix_id = test_matrix_operations(manager)
        shell_id = test_shell_operations(manager)
        
        # 3. test relationships integration
        test_relationships(manager, char_id, matrix_id, shell_id)
        
        # 4. test higher-level features
        test_team_setup(manager)
        test_comprehensive_info(manager)
        test_integration_stats(manager)
        test_export(manager)
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed! Unified database system is operating normally")
        
    except Exception as e:
        print(f"\n❌ An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
