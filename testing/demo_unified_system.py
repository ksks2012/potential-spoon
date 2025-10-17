#!/usr/bin/env python3
"""
Etheria Unified Database System Demo
Full demonstration of unified database features
"""

import sys
import os

# Set correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.etheria_manager import EtheriaManager
import json


def setup_demo_data(manager):
    """Create demo data"""
    print("=== Setup Demo Data ===")
    
    # Create characters
    characters = [
        {
            'basic_info': {
                'name': 'Plume',
                'rarity': 'SSR',
                'element': 'Fire'
            },
            'stats': {
                'hp': {'base': 5000, 'bonus': 500},
                'attack': {'base': 850, 'bonus': 85},
                'defense': {'base': 300, 'bonus': 30}
            },
            'skills': [
                {'name': 'Flame Strike', 'type': 'normal', 'description': 'Basic fire attack'},
                {'name': 'Inferno Burst', 'type': 'ultimate', 'description': 'Ultimate fire ability'}
            ]
        },
        {
            'basic_info': {
                'name': 'Yeli',
                'rarity': 'SSR',
                'element': 'Ice'
            },
            'stats': {
                'hp': {'base': 4800, 'bonus': 480},
                'attack': {'base': 900, 'bonus': 90},
                'defense': {'base': 280, 'bonus': 28}
            },
            'skills': [
                {'name': 'Ice Shard', 'type': 'normal', 'description': 'Basic ice attack'},
                {'name': 'Frozen Domain', 'type': 'ultimate', 'description': 'Ultimate ice ability'}
            ]
        }
    ]
    
    # Create matrix effects
    matrices = [
        {
            'name': 'Flame Resonance',
            'source': 'Demo Data',
            'type': ['Fire', 'Attack'],
            'effects': [
                {
                    'required': 2,
                    'total': 4,
                    'extra_effect': '+15% Fire DMG',
                    'effect': {
                        'fire_damage': 15,
                        'attack': 50
                    }
                },
                {
                    'required': 4,
                    'total': 4,
                    'extra_effect': '+25% Crit Rate when using Fire skills',
                    'effect': {
                        'crit_rate': 25,
                        'fire_damage': 25
                    }
                }
            ]
        },
        {
            'name': 'Ice Crystal',
            'source': 'Demo Data',
            'type': ['Ice', 'Control'],
            'effects': [
                {
                    'required': 2,
                    'total': 4,
                    'extra_effect': '+12% Ice DMG',
                    'effect': {
                        'ice_damage': 12,
                        'defense': 40
                    }
                },
                {
                    'required': 4,
                    'total': 4,
                    'extra_effect': '+20% Freeze chance',
                    'effect': {
                        'freeze_chance': 20,
                        'ice_damage': 20
                    }
                }
            ]
        },
        {
            'name': 'Universal Boost',
            'source': 'Demo Data',
            'type': ['Universal', 'Support'],
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
    ]
    
    # Create shells
    shells = [
        {
            'name': 'Fire Dragon Shell',
            'rarity': 'SSR',
            'class': 'DPS',
            'cooldown': 35,
            'skills': {
                'awakened': [
                    {'name': 'Dragon Breath', 'description': 'Unleash powerful fire breath dealing massive damage'}
                ],
                'non_awakened': [
                    {'name': 'Fire Claw', 'description': 'Slash with fire-enhanced claws'}
                ]
            },
            'stats': {
                'hp': 600,
                'attack': 150,
                'fire_damage': 25
            },
            'sets': ['Flame Resonance', 'Universal Boost']
        },
        {
            'name': 'Ice Phoenix Shell',
            'rarity': 'SSR', 
            'class': 'Support',
            'cooldown': 30,
            'skills': {
                'awakened': [
                    {'name': 'Phoenix Revival', 'description': 'Revive and heal team with ice energy'}
                ],
                'non_awakened': [
                    {'name': 'Ice Shield', 'description': 'Create protective ice barriers'}
                ]
            },
            'stats': {
                'hp': 800,
                'defense': 120,
                'ice_damage': 20
            },
            'sets': ['Ice Crystal', 'Universal Boost']
        }
    ]
    
    # Insert all data
    char_ids = []
    for char_data in characters:
        char_id = manager.characters.insert_character(char_data)
        char_ids.append(char_id)
        print(f"  Character '{char_data['basic_info']['name']}' created (ID: {char_id})")
    
    matrix_ids = []
    for matrix_data in matrices:
        matrix_id = manager.matrices.insert_matrix_effect(matrix_data)
        matrix_ids.append(matrix_id)
        print(f"  Matrix '{matrix_data['name']}' created (ID: {matrix_id})")
    
    shell_ids = []
    for shell_data in shells:
        shell_id = manager.shells.insert_shell(shell_data)
        shell_ids.append(shell_id)
        print(f"  Shell '{shell_data['name']}' created (ID: {shell_id})")
    
    print("✅ Demo data setup complete\n")
    return char_ids, matrix_ids, shell_ids


def demonstrate_team_management(manager):
    """Demonstrate team management features"""
    print("=== Team Management Demo ===")
    
    # Equip Plume with Fire Dragon Shell and flame matrices
    print("Configuring Plume's combat equipment:")
    plume_setup = manager.create_team_setup(
        'Plume',
        'Fire Dragon Shell', 
        ['Flame Resonance', 'Universal Boost'],
        'Fire DPS Build'
    )
    
    print(f"  Shell equipped: {'✅' if plume_setup['shell_equipped'] else '❌'}")
    print(f"  Matrix loadout set: {'✅' if plume_setup['matrix_loadout_set'] else '❌'}")
    
    # Equip Yeli with Ice Phoenix Shell and ice matrices
    print("\nConfiguring Yeli's support equipment:")
    yeli_setup = manager.create_team_setup(
        'Yeli',
        'Ice Phoenix Shell',
        ['Ice Crystal', 'Universal Boost'],
        'Ice Support Build'
    )
    
    print(f"  Shell equipped: {'✅' if yeli_setup['shell_equipped'] else '❌'}")
    print(f"  Matrix loadout set: {'✅' if yeli_setup['matrix_loadout_set'] else '❌'}")
    
    print("✅ Team configuration complete\n")


def show_character_complete_info(manager):
    """Show complete character information"""
    print("=== Character Complete Information ===")
    
    characters = ['Plume', 'Yeli']
    
    for char_name in characters:
        print(f"\nComplete info for {char_name}:")
        char_info = manager.get_character_complete_info(char_name)
        
        if char_info:
            basic_info = char_info.get('basic_info', {})
            print(f"  Rarity: {basic_info.get('rarity', 'Unknown')}")
            print(f"  Element: {basic_info.get('element', 'Unknown')}")
            
            if 'equipped_shell' in char_info:
                shell = char_info['equipped_shell']
                print(f"  Equipped shell: {shell['name']} ({shell['rarity']}, {shell['class']})")
            
            if 'matrix_loadouts' in char_info:
                for loadout_name, matrices in char_info['matrix_loadouts'].items():
                    print(f"  Matrix loadout '{loadout_name}':")
                    for matrix_info in matrices:
                        print(f"    - Position {matrix_info['position']}: {matrix_info['matrix']}")
    
    print("✅ Character display complete\n")


def show_integration_analytics(manager):
    """Show integration analytics"""
    print("=== Integration Analytics Report ===")
    
    stats = manager.get_comprehensive_stats()
    
    # Basic stats
    print("Database overview:")
    db_stats = stats['database']
    print(f"  Total characters: {db_stats['total_characters']}")
    print(f"  Total shells: {db_stats['total_shells']}")
    print(f"  Total matrix effects: {db_stats['total_matrix_effects']}")
    print(f"  Shell-matrix relationships: {db_stats['shell_matrix_relationships']}")
    
    # Integration stats
    print("\nIntegration metrics:")
    integration = stats['integration']
    
    shell_matrix = integration['shell_matrix']
    print(f"  Shell-matrix coverage: {shell_matrix['shell_coverage']:.1f}%")
    print(f"  Matrix usage rate: {shell_matrix['matrix_usage']:.1f}%")
    
    char_shell = integration['character_shell']  
    print(f"  Character equipment rate: {char_shell['equipment_rate']:.1f}%")
    
    # Matrix usage analysis
    print("\nMatrix usage analysis:")
    matrix_usage = stats.get('matrix_usage_by_shells', {})
    if matrix_usage:
        for matrix_name, usage_count in matrix_usage.items():
            print(f"  {matrix_name}: used by {usage_count} shells")
    else:
        print("  No matrix usage statistics available")
    
    print("✅ Analytics report complete\n")


def export_demonstration(manager):
    """Demonstrate export functionality"""
    print("=== Data Export Demo ===")
    
    export_file = "./testing/demo_export.json"
    success = manager.export_unified_data(export_file)
    
    if success:
        print(f"✅ Data exported to {export_file}")
        
        # Show export file size and basic stats
        file_size = os.path.getsize(export_file) / 1024  # KB
        print(f"  File size: {file_size:.2f} KB")
        
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Export contents:")
        print(f"    Characters: {len(data['characters'])}")
        print(f"    Shells: {len(data['shells'])}")
        print(f"    Matrix effects: {len(data['matrix_effects'])}")
        print(f"    Relationship records: {sum(len(v) for v in data['relationships'].values())}")
    else:
        print("❌ Export failed")
    
    print()


def main():
    """Main demo routine"""
    print("Etheria Unified Database System Demo")
    print("=" * 50)
    
    try:
        # Ensure testing directory exists
        os.makedirs("./testing", exist_ok=True)
        
        # Use demo database
        demo_db_path = "./testing/demo_unified.db"
        if os.path.exists(demo_db_path):
            os.remove(demo_db_path)
        
        # Initialize manager
        manager = EtheriaManager(demo_db_path)
        
        # Run demo flow
        setup_demo_data(manager)
        demonstrate_team_management(manager)  
        show_character_complete_info(manager)
        show_integration_analytics(manager)
        export_demonstration(manager)
        
        print("=" * 50)
        print("🎉 Unified database system demo complete!")
        print("🔧 The system includes the following features:")
        print("   ✅ Unified database schema")
        print("   ✅ Character, shell, matrix management")
        print("   ✅ Relationship integration and foreign key constraints")
        print("   ✅ Team configuration management")
        print("   ✅ Complete information queries")
        print("   ✅ Integration analytics reports")
        print("   ✅ Data export functionality")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ An error occurred during the demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
