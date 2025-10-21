#!/usr/bin/env python3
"""
Test script to demonstrate Module Editor display name logic
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mathic.mathic_system import MathicSystem


def test_module_display_names():
    """Test how module names are displayed in Module Editor"""
    print("🔍 Testing Module Editor Display Name Logic...")
    print("=" * 60)
    
    # Initialize system
    system = MathicSystem()
    
    # Create different types of modules
    test_modules = []
    
    # Create mask module
    mask = system.create_module("mask", 1, "ATK")
    if mask:
        system.generate_random_substats(mask, 2)
        test_modules.append(mask)
        print(f"Created: {mask.module_id}")
    
    # Create transistor module
    transistor = system.create_module("transistor", 2, "HP")
    if transistor:
        system.generate_random_substats(transistor, 3)
        # Enhance it a few times to increase level
        system.enhance_module_random_substat(transistor)
        system.enhance_module_random_substat(transistor)
        test_modules.append(transistor)
        print(f"Created: {transistor.module_id}")
    
    # Create core module
    core = system.create_module("core", 4, "CRIT Rate")
    if core:
        system.generate_random_substats(core, 4)
        # Enhance it more to show higher level
        for _ in range(3):
            system.enhance_module_random_substat(core)
        test_modules.append(core)
        print(f"Created: {core.module_id}")
    
    print("\n" + "=" * 60)
    print("Module Editor Display Format Analysis:")
    print("=" * 60)
    
    print("\n📋 Module List Display (as shown in Module Editor):")
    print("-" * 50)
    
    # This is the exact format used in ModuleEditorView.update_display()
    all_modules = system.get_all_modules()
    for module_id, module in all_modules.items():
        display_text = f"{module.module_type} - {module.main_stat} ({module.level})"
        print(f"  {display_text}")
        
        # Show breakdown
        print(f"    ├── Module Type: '{module.module_type}'")
        print(f"    ├── Main Stat: '{module.main_stat}'")
        print(f"    ├── Level: {module.level}")
        print(f"    └── Full Display: '{display_text}'")
        print()
    
    print("🔍 Display Logic Source:")
    print("-" * 30)
    print("File: windowing/views.py")
    print("Method: ModuleEditorView.update_display()")
    print("Line: ~646")
    print('Code: display_text = f"{module.module_type} - {module.main_stat} ({module.level})"')
    
    print("\n📊 Other Display Formats in Different Components:")
    print("-" * 50)
    
    print("1. Enhance Simulator:")
    for module_id, module in all_modules.items():
        display_text = f"{module_id}: {module.module_type} - {module.main_stat}"
        print(f"   {display_text}")
    
    print("\n2. Loadout Manager:")
    for module_id, module in all_modules.items():
        display_text = f"{module_id}: {module.module_type} - {module.main_stat}"
        print(f"   {display_text}")
    
    print("\n✅ Summary:")
    print("━" * 50)
    print("Module Editor module display format:")
    print("  Format: '{module_type} - {main_stat} ({level}) - {matrix} ({matrix_count})'")
    print("  Examples: 'mask - ATK (1) - None (0)', 'core - CRIT Rate (3) - (0)'")
    print("  Source: ModuleEditorView.update_display() in windowing/views.py")
    print("  Flow: Controller.refresh_module_list() → Model.get_all_modules() → View.update_display()")


if __name__ == "__main__":
    test_module_display_names()
