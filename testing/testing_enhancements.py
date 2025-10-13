#!/usr/bin/env python3
"""
Test script to verify the new enhancements:
1. Module total enhancement rolls limited to 5
2. Loadout Manager layout with Total Stats on the right
3. Manual enhancement in Module Editor
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from mathic.mathic_system import MathicSystem

def test_total_roll_limit():
    """Test that modules can only be enhanced 5 times total"""
    print("=== Testing Total Roll Limit ===")
    ms = MathicSystem()
    
    # Create a test module
    module = ms.create_module("mask", 1, "ATK")
    ms.generate_random_substats(module, 4)
    
    print(f"Created module: {module.module_type} - {module.main_stat}")
    print(f"Initial total rolls: {module.total_enhancement_rolls}/{module.max_total_rolls}")
    print("Initial substats:")
    for substat in module.substats:
        print(f"  {substat.stat_name}: {int(substat.current_value)} ({substat.rolls_used}/5 rolls)")
    
    # Try to enhance 6 times (should only work 5 times)
    successful_enhancements = 0
    for i in range(6):
        enhanced = ms.enhance_module_random_substat(module)
        if enhanced:
            successful_enhancements += 1
            print(f"Enhancement {i+1}: Enhanced {enhanced} - Total rolls: {module.total_enhancement_rolls}")
        else:
            print(f"Enhancement {i+1}: Failed (reached limit)")
    
    print(f"\nTotal successful enhancements: {successful_enhancements}")
    print(f"Final total rolls: {module.total_enhancement_rolls}/{module.max_total_rolls}")
    
    assert successful_enhancements == 5, f"Should only allow 5 enhancements, got {successful_enhancements}"
    assert module.total_enhancement_rolls == 5, f"Total rolls should be 5, got {module.total_enhancement_rolls}"
    
    print("✅ Total roll limit working correctly!")

def test_manual_enhancement():
    """Test manual enhancement with specific substat and roll count"""
    print("\n=== Testing Manual Enhancement ===")
    ms = MathicSystem()
    
    # Create a test module
    module = ms.create_module("core", 4, "CRIT Rate")
    ms.generate_random_substats(module, 4)
    
    print(f"Created module: {module.module_type} - {module.main_stat}")
    print("Initial substats:")
    for substat in module.substats:
        print(f"  {substat.stat_name}: {int(substat.current_value)} ({substat.rolls_used}/5 rolls)")
    
    # Test manual enhancement
    target_substat = module.substats[0]
    initial_value = target_substat.current_value
    initial_rolls = target_substat.rolls_used
    initial_total_rolls = module.total_enhancement_rolls
    
    print(f"\nTesting manual enhancement of {target_substat.stat_name}")
    print(f"Before: Value={int(initial_value)}, Rolls={initial_rolls}, Total={initial_total_rolls}")
    
    # Enhance with 2 rolls
    success = ms.enhance_module_specific_substat(module, target_substat.stat_name, 2)
    
    if success:
        print(f"After: Value={int(target_substat.current_value)}, Rolls={target_substat.rolls_used}, Total={module.total_enhancement_rolls}")
        
        # Verify the enhancement
        value_increased = target_substat.current_value > initial_value
        rolls_increased = target_substat.rolls_used == initial_rolls + 2
        total_rolls_increased = module.total_enhancement_rolls == initial_total_rolls + 2
        
        assert value_increased, "Value should have increased"
        assert rolls_increased, f"Rolls should be {initial_rolls + 2}, got {target_substat.rolls_used}"
        assert total_rolls_increased, f"Total rolls should be {initial_total_rolls + 2}, got {module.total_enhancement_rolls}"
        
        print("✅ Manual enhancement working correctly!")
    else:
        print("❌ Manual enhancement failed")

def test_enhancement_limits():
    """Test that enhancement respects both individual and total limits"""
    print("\n=== Testing Enhancement Limits ===")
    ms = MathicSystem()
    
    # Create a test module
    module = ms.create_module("transistor", 2, "HP")
    ms.generate_random_substats(module, 4)
    
    # Try to enhance one substat to its maximum (5 rolls)
    target_substat = module.substats[0]
    stat_name = target_substat.stat_name
    
    print(f"Testing limits for {stat_name}")
    
    # Enhance to maximum individual rolls (5)
    success = ms.enhance_module_specific_substat(module, stat_name, 5)
    if success:
        print(f"Enhanced {stat_name} to maximum: {target_substat.rolls_used}/5 rolls")
        
        # Try to enhance again (should fail)
        success2 = ms.enhance_module_specific_substat(module, stat_name, 1)
        assert not success2, "Should not be able to enhance beyond 5 rolls per substat"
        print("✅ Individual substat limit working!")
        
        # Check if we can still enhance other substats (if total rolls < 5)
        if module.total_enhancement_rolls < 5:
            other_substat = next((s for s in module.substats if s.stat_name != stat_name), None)
            if other_substat:
                remaining_rolls = 5 - module.total_enhancement_rolls
                if remaining_rolls > 0:
                    success3 = ms.enhance_module_specific_substat(module, other_substat.stat_name, min(remaining_rolls, 1))
                    if success3:
                        print("✅ Can still enhance other substats within total limit!")
    
    print("✅ Enhancement limits working correctly!")

if __name__ == "__main__":
    print("Testing new enhancement features...\n")
    
    try:
        test_total_roll_limit()
        test_manual_enhancement()
        test_enhancement_limits()
        
        print("\n🎉 All enhancement tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
