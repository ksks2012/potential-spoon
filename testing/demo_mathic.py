#!/usr/bin/env python3
"""
Comprehensive Mathic System Demo
Shows off all features including random generation and enhancement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mathic.mathic_system import MathicSystem
import json


def demo_mathic_system():
    """Comprehensive demo of the mathic system"""
    
    print("="*70)
    print("MATHIC SYSTEM COMPREHENSIVE DEMO")
    print("="*70)
    
    # Initialize system
    mathic_system = MathicSystem()
    print("✓ Mathic system initialized")
    
    # Show configuration
    print("\n📋 System Configuration:")
    print(f"Module types: {list(mathic_system.config.get('module_types', {}).keys())}")
    
    slots_config = mathic_system.config.get('mathic_slots', [])
    print(f"Available slots: {[slot['slot_id'] for slot in slots_config]}")
    
    # Create random modules for a complete loadout
    print("\n🎲 Creating Random Epic Modules:")
    
    modules = []
    slot_info = [
        (1, "mask", "ATK"),
        (2, "transistor", "HP"),  
        (3, "wristwheel", "DEF"),
        (4, "core", "CRIT Rate"),
        (5, "mask", "ATK%"),
        (6, "core", "CRIT DMG")
    ]
    
    for slot, module_type, main_stat in slot_info:
        module = mathic_system.create_module(module_type, slot, main_stat)
        if module:
            modules.append(module)
            print(f"  Slot {slot}: {module_type} ({main_stat}) - {module.module_id}")
        
        # Generate random substats
        if module and len(module.substats) == 0:
            # Add some random substats for demo
            available_substats = list(mathic_system.config.get("substats", {}).keys())
            available_substats = [s for s in available_substats if s != main_stat]
            
            import random
            random.shuffle(available_substats)
            selected_substats = available_substats[:4]  # 4 substats max
            
            from mathic.mathic_system import Substat
            for stat_name in selected_substats:
                stat_config = mathic_system.config["substats"][stat_name]
                initial_value = random.uniform(stat_config["roll_range"][0], stat_config["roll_range"][1])
                
                substat = Substat(
                    stat_name=stat_name,
                    current_value=initial_value,
                    rolls_used=1,
                    max_rolls=5
                )
                module.substats.append(substat)
    
    print(f"✓ Created {len(modules)} modules with random substats")
    
    # Show detailed module stats
    print("\n📊 Module Details:")
    for i, module in enumerate(modules):
        print(f"\n  Module {i+1} - {module.module_type.upper()}:")
        print(f"    Main Stat: {module.main_stat} = {module.main_stat_value}")
        print(f"    Level: {module.level}")
        print(f"    Substats:")
        for j, substat in enumerate(module.substats):
            if substat.stat_name:
                efficiency = substat.get_efficiency_percentage(
                    mathic_system.config["substats"][substat.stat_name]["max_value"]
                )
                print(f"      {j+1}. {substat.stat_name}: {substat.current_value:.1f} "
                      f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}% eff)")
    
    # Test enhancement system
    print("\n⚡ Testing Enhancement System:")
    
    for i, module in enumerate(modules[:3]):  # Enhance first 3 modules
        print(f"\n  Enhancing {module.module_type}...")
        
        for enhancement in range(3):  # 3 enhancement attempts
            enhanced_stat = mathic_system.enhance_module_random_substat(module)
            if enhanced_stat:
                print(f"    +{enhancement+1}: Enhanced {enhanced_stat} "
                      f"(Module level: {module.level})")
            else:
                print(f"    +{enhancement+1}: No enhancement possible")
                break
    
    # Create and populate loadout
    print("\n🎒 Creating Complete Loadout:")
    
    loadout = mathic_system.create_mathic_loadout("Epic Build")
    print("✓ Created 'Epic Build' loadout")
    
    # Assign all modules
    for i, module in enumerate(modules):
        slot_id = i + 1
        success = mathic_system.assign_module_to_loadout("Epic Build", slot_id, module.module_id)
        if success:
            print(f"✓ Assigned {module.module_type} to slot {slot_id}")
    
    # Calculate total stats
    print("\n📈 Loadout Total Stats:")
    
    loadout_modules = mathic_system.get_loadout_modules("Epic Build")
    
    total_stats = {}
    for slot_id, module in loadout_modules.items():
        if module:
            # Add main stat
            if module.main_stat in total_stats:
                total_stats[module.main_stat] += module.main_stat_value
            else:
                total_stats[module.main_stat] = module.main_stat_value
            
            # Add substats
            for substat in module.substats:
                if substat.stat_name:
                    if substat.stat_name in total_stats:
                        total_stats[substat.stat_name] += substat.current_value
                    else:
                        total_stats[substat.stat_name] = substat.current_value
    
    # Display stats nicely
    flat_stats = ["ATK", "HP", "DEF"]
    percent_stats = ["ATK%", "HP%", "DEF%", "CRIT Rate", "CRIT DMG", "Effect ACC", "Effect RES", "SPD"]
    
    print("  Flat Stats:")
    for stat in flat_stats:
        if stat in total_stats:
            print(f"    {stat}: +{int(total_stats[stat])}")
    
    print("  Percentage Stats:")
    for stat in percent_stats:
        if stat in total_stats:
            print(f"    {stat}: +{total_stats[stat]:.1f}%")
    
    # Test save system
    print("\n💾 Testing Save/Load System:")
    
    save_file = "./mathic/demo_save.json"
    success = mathic_system.save_to_file(save_file)
    
    if success:
        print(f"✓ Saved complete system to {save_file}")
        
        # Show file size
        file_size = os.path.getsize(save_file)
        print(f"  File size: {file_size} bytes")
        
        # Load into new system
        new_system = MathicSystem()
        load_success = new_system.load_from_file(save_file)
        
        if load_success:
            print(f"✓ Successfully loaded system")
            print(f"  Modules loaded: {len(new_system.modules)}")
            print(f"  Loadouts loaded: {len(new_system.mathic_loadouts)}")
        else:
            print("✗ Failed to load system")
    else:
        print("✗ Failed to save system")
    
    # Performance statistics
    print("\n📊 System Statistics:")
    print(f"Total modules created: {len(mathic_system.modules)}")
    print(f"Total loadouts: {len(mathic_system.mathic_loadouts)}")
    
    # Count enhancement levels
    enhancement_levels = [module.level for module in mathic_system.modules.values()]
    if enhancement_levels:
        print(f"Enhancement levels: min={min(enhancement_levels)}, max={max(enhancement_levels)}, avg={sum(enhancement_levels)/len(enhancement_levels):.1f}")
    
    # Count substats
    total_substats = sum(len([s for s in module.substats if s.stat_name]) 
                        for module in mathic_system.modules.values())
    print(f"Total substats: {total_substats}")
    
    print("\n" + "="*70)
    print("MATHIC SYSTEM DEMO COMPLETED SUCCESSFULLY!")
    print("="*70)


if __name__ == "__main__":
    demo_mathic_system()
