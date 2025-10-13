#!/usr/bin/env python3
"""
Mathic System Test Script
Test all mathic system functionality with rt-sandbox venv
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathic.mathic_system import MathicSystem


def test_mathic_system():
    """Test the mathic system functionality"""
    
    print("="*60)
    print("MATHIC SYSTEM TEST")
    print("="*60)
    
    # Initialize system
    mathic_system = MathicSystem()
    print("✓ Mathic system initialized")
    
    # Test module creation
    print("\n--- Testing Module Creation ---")
    
    # Create different types of modules with proper parameters (module_type, slot_position, main_stat)
    mask = mathic_system.create_module("mask", 1, "ATK")
    transistor = mathic_system.create_module("transistor", 2, "HP")  
    wristwheel = mathic_system.create_module("wristwheel", 3, "DEF")
    core = mathic_system.create_module("core", 4, "CRIT Rate")
    
    if mask:
        print(f"✓ Created Mask: {mask.module_id}")
    else:
        print("✗ Failed to create Mask")
    
    if transistor:
        print(f"✓ Created Transistor: {transistor.module_id}")
    else:
        print("✗ Failed to create Transistor")
        
    if wristwheel:
        print(f"✓ Created Wristwheel: {wristwheel.module_id}")
    else:
        print("✗ Failed to create Wristwheel")
        
    if core:
        print(f"✓ Created Core: {core.module_id}")
    else:
        print("✗ Failed to create Core")
    
    # Test module retrieval and display
    print("\n--- Module Details ---")
    
    if mask:
        print(f"\nMask Module:")
        print(f"  Type: {mask.module_type}")
        print(f"  Main Stat: {mask.main_stat} = {mask.main_stat_value}")
        print(f"  Level: {mask.level}")
        print(f"  Substats ({len(mask.substats)}):")
        for i, substat in enumerate(mask.substats):
            if substat.stat_name:
                print(f"    {i+1}. {substat.stat_name}: {substat.current_value:.1f} ({substat.rolls_used} rolls)")
    else:
        print("No mask module to display")
    
    # Test enhancement
    print("\n--- Testing Enhancement ---")
    
    if mask:
        original_level = mask.level
        enhanced_stat = mathic_system.enhance_module_random_substat(mask)
        
        if enhanced_stat:
            print(f"✓ Enhanced mask from level {original_level} to {mask.level}")
            print(f"  Enhanced stat: {enhanced_stat}")
            print("Updated substats:")
            for i, substat in enumerate(mask.substats):
                if substat.stat_name:
                    print(f"    {i+1}. {substat.stat_name}: {substat.current_value:.1f} ({substat.rolls_used} rolls)")
        else:
            print("✗ Enhancement failed or no more enhancements possible")
    
    # Test mathic loadout
    print("\n--- Testing Mathic Loadout ---")
    
    loadout = mathic_system.create_mathic_loadout("Test Loadout")
    print(f"✓ Created mathic loadout with {len(loadout)} slots")
    
    # Equip modules
    if mask:
        success1 = mathic_system.assign_module_to_loadout("Test Loadout", 1, mask.module_id)
        print(f"✓ Assigned mask to slot 1: {success1}")
    
    if transistor:
        success2 = mathic_system.assign_module_to_loadout("Test Loadout", 2, transistor.module_id)
        print(f"✓ Assigned transistor to slot 2: {success2}")
    
    if wristwheel:
        success3 = mathic_system.assign_module_to_loadout("Test Loadout", 3, wristwheel.module_id)
        print(f"✓ Assigned wristwheel to slot 3: {success3}")
    
    if core:
        success4 = mathic_system.assign_module_to_loadout("Test Loadout", 4, core.module_id)
        print(f"✓ Assigned core to slot 4: {success4}")
    
    # Display loadout modules
    loadout_modules = mathic_system.get_loadout_modules("Test Loadout")
    print("\nLoadout modules:")
    for slot_id, module in loadout_modules.items():
        if module:
            print(f"  Slot {slot_id}: {module.module_type} ({module.main_stat})")
        else:
            print(f"  Slot {slot_id}: Empty")
    
    # Test save/load functionality
    print("\n--- Testing Save/Load ---")
    
    try:
        save_success = mathic_system.save_to_file("./mathic/test_system.json")
        print(f"✓ Saved system to file: {save_success}")
        
        # Create new system and load
        new_system = MathicSystem("./mathic/mathic_config.json")
        load_success = new_system.load_from_file("./mathic/test_system.json")
        
        if load_success:
            print(f"✓ Loaded system from file: {load_success}")
            print(f"  Loaded {len(new_system.modules)} modules")
            print(f"  Loaded {len(new_system.mathic_loadouts)} loadouts")
        else:
            print("✗ Failed to load system")
            
    except Exception as e:
        print(f"✗ Save/Load failed: {e}")
    
    # Statistics summary
    print("\n--- System Statistics ---")
    
    print(f"Total Modules: {len(mathic_system.modules)}")
    print(f"Total Loadouts: {len(mathic_system.mathic_loadouts)}")
    
    # Count by type
    type_counts = {}
    for module in mathic_system.modules.values():
        module_type = module.module_type
        type_counts[module_type] = type_counts.get(module_type, 0) + 1
    
    print("Modules by type:")
    for module_type, count in type_counts.items():
        print(f"  {module_type}: {count}")
    
    print("\n" + "="*60)
    print("MATHIC SYSTEM TEST COMPLETED")
    print("="*60)


if __name__ == "__main__":
    test_mathic_system()
