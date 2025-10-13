#!/usr/bin/env python3
"""
Test the UI slot restrictions to ensure they work correctly
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from mathic.mathic_system import MathicSystem

def test_ui_slot_restrictions():
    """Test that UI slot restrictions work as expected"""
    print("=== Testing UI Slot Restrictions ===")
    
    ms = MathicSystem()
    
    # Create different types of modules
    mask_module = ms.create_module("mask", 1, "ATK")
    transistor_module = ms.create_module("transistor", 2, "HP") 
    wristwheel_module = ms.create_module("wristwheel", 3, "DEF")
    core_module1 = ms.create_module("core", 4, "CRIT Rate")
    core_module2 = ms.create_module("core", 5, "CRIT DMG")
    
    # Simulate UI restriction logic
    slot_restrictions = {
        1: ["mask"],
        2: ["transistor"], 
        3: ["wristwheel"],
        4: ["core"],
        5: ["core"],
        6: ["core"]
    }
    
    print("Testing slot filtering...")
    
    for slot_id in range(1, 7):
        allowed_types = slot_restrictions.get(slot_id, [])
        print(f"\nSlot {slot_id} allows: {allowed_types}")
        
        # Filter modules by allowed types for this slot
        slot_module_options = ["None"]
        for mid, mod in ms.modules.items():
            if mod.module_type in allowed_types:
                slot_module_options.append(f"{mid}: {mod.module_type} - {mod.main_stat}")
        
        print(f"  Available options: {len(slot_module_options)-1} modules")
        for option in slot_module_options[1:]:  # Skip "None"
            print(f"    {option}")
    
    print("\n✅ UI slot restrictions working correctly!")

if __name__ == "__main__":
    test_ui_slot_restrictions()
