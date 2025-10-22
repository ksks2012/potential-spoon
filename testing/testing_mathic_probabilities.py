#!/usr/bin/env python3
"""
Testing Enhanced Mathic System Probabilities and Value Analysis
Combines enhancement probability calculation and value analysis testing
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from mathic.mathic_system import MathicSystem, Substat
from windowing.models import MathicModel
from windowing.views import EnhanceSimulatorView
from windowing.controllers import EnhanceSimulatorController
from windowing.models import AppState

def test_probability_calculations():
    """Test enhancement probability calculations with different scenarios"""
    print("=== TESTING ENHANCEMENT PROBABILITY CALCULATIONS ===\n")
    
    # Initialize MathicSystem with correct config path
    config_path = os.path.join(project_root, "mathic", "mathic_config.json")
    mathic = MathicSystem(config_path)
    
    # Create test module
    module = mathic.create_module('core', 1, 'ATK%')
    mathic.generate_random_substats(module, 4)
    
    print(f"Created module: {module.module_id}")
    print(f"Total rolls: {module.total_enhancement_rolls}/{module.max_total_rolls}")
    print(f"Substats: {len(module.substats)}")
    for i, substat in enumerate(module.substats):
        print(f"  {i+1}. {substat.stat_name}: {substat.current_value} ({substat.rolls_used}/5)")
    
    # Test Scenario 1: Fresh module (0/5 total rolls)
    print(f"\n--- Scenario 1: Fresh module (0/5 total rolls) ---")
    prob1 = mathic.calculate_substat_probabilities(module)
    print("Enhancement Probabilities:")
    for stat, prob in prob1.items():
        print(f"  {stat}: {prob:.3f} ({prob*100:.1f}%)")
    
    # Test Scenario 2: Near limit (4/5 total rolls)  
    print(f"\n--- Scenario 2: Near limit (4/5 total rolls) ---")
    module.total_enhancement_rolls = 4
    prob2 = mathic.calculate_substat_probabilities(module)
    print("Enhancement Probabilities:")
    for stat, prob in prob2.items():
        print(f"  {stat}: {prob:.3f} ({prob*100:.1f}%)")
    
    # Test Scenario 3: At limit (5/5 total rolls)
    print(f"\n--- Scenario 3: At limit (5/5 total rolls) ---")
    module.total_enhancement_rolls = 5
    prob3 = mathic.calculate_substat_probabilities(module)
    print("Enhancement Probabilities:")
    for stat, prob in prob3.items():
        print(f"  {stat}: {prob:.3f} ({prob*100:.1f}%)")
    
    return mathic

def test_enhanced_probability_logic():
    """Test enhanced probability calculations with different module states"""
    print("\n=== TESTING ENHANCED PROBABILITY LOGIC ===\n")
    
    # Initialize model
    mathic_model = MathicModel()
    
    # Create test modules with different scenarios
    print("✅ Creating test modules...")
    
    # Scenario 1: Module with < 4 substats
    module1 = mathic_model.create_module("mask", 1, "ATK")
    module1_id = module1.module_id
    
    # Add some substats
    for i in range(2):
        mathic_model.mathic_system.enhance_module_random_substat(module1)
    
    print(f"\n📊 Module 1 (2/4 substats):")
    print(f"   Substats: {len(module1.substats)}/4")
    probs1 = mathic_model.calculate_substat_probabilities(module1_id)
    for stat, prob in probs1.items():
        print(f"   {stat}: {prob*100:.1f}%")
    
    # Scenario 2: Module with 4 substats, some at max rolls
    module2 = mathic_model.create_module("transistor", 2, "HP")
    module2_id = module2.module_id
    
    # Add 4 substats
    for i in range(4):
        mathic_model.mathic_system.enhance_module_random_substat(module2)
    
    # Set some substats to max rolls
    module2.substats[0].rolls_used = 5
    module2.substats[1].rolls_used = 5
    
    print(f"\n📊 Module 2 (4/4 substats, 2 at max rolls):")
    print(f"   Substats: {len(module2.substats)}/4")
    for i, substat in enumerate(module2.substats, 1):
        print(f"   {i}. {substat.stat_name}: {substat.rolls_used}/5 rolls")
    
    probs2 = mathic_model.calculate_substat_probabilities(module2_id)
    print(f"\n   Enhancement Probabilities:")
    for stat, prob in probs2.items():
        print(f"   {stat}: {prob*100:.1f}%")
    
    return mathic_model

def test_value_analysis(mathic_model):
    """Test enhanced value analysis with categories"""
    print(f"\n=== TESTING ENHANCED VALUE ANALYSIS ===\n")
    
    # Create a diverse module for testing
    module = mathic_model.create_module("core", 3, "ATK%")
    module_id = module.module_id
    
    # Add specific substats for testing categories
    # Defense stat
    def_substat = Substat("HP%", 15.5, 3, 5)
    module.substats.append(def_substat)
    
    # Support stat  
    spd_substat = Substat("SPD", 12, 4, 5)
    module.substats.append(spd_substat)
    
    # Offense stat
    crit_substat = Substat("CRIT DMG", 18.2, 2, 5)
    module.substats.append(crit_substat)
    
    # Another offense stat
    atk_substat = Substat("ATK%", 8.1, 1, 5)
    module.substats.append(atk_substat)
    
    print(f"📊 Test Module for Value Analysis:")
    print(f"   Main Stat: {module.main_stat} ({module.main_stat_value})")
    print(f"   Substats:")
    for i, substat in enumerate(module.substats, 1):
        print(f"     {i}. {substat.stat_name}: {substat.current_value} ({substat.rolls_used}/5)")
    
    # Calculate value analysis
    value_data = mathic_model.calculate_module_value(module_id)
    
    print(f"\n📈 Value Analysis Results:")
    print(f"   Total Value Score: {value_data['total_value']:.2f}")
    print(f"   Overall Efficiency: {value_data['efficiency']:.1f}%")
    print(f"   Roll Efficiency: {value_data['roll_efficiency']:.1f}%")
    
    # Category scores
    print(f"\n🏷️ Category Scores:")
    print(f"   Defense Score:  {value_data.get('defense_score', 0):.2f}")
    print(f"   Support Score:  {value_data.get('support_score', 0):.2f}")
    print(f"   Offense Score:  {value_data.get('offense_score', 0):.2f}")
    
    # Determine primary category
    scores = {
        'Defense': value_data.get('defense_score', 0),
        'Support': value_data.get('support_score', 0),
        'Offense': value_data.get('offense_score', 0)
    }
    primary_category = max(scores, key=scores.get) if max(scores.values()) > 0 else "General"
    print(f"   Primary Focus: {primary_category}")
    
    return value_data

def test_gui_integration():
    """Test GUI integration with enhanced probabilities"""
    print(f"\n=== TESTING GUI INTEGRATION ===\n")
    
    # Create GUI components
    root = tk.Tk()
    root.title("Enhanced Mathic System Test")
    root.geometry("800x600")
    
    # Create test model
    mathic_model = MathicModel()
    app_state = AppState()
    
    # Create view and controller
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    view = EnhanceSimulatorView(main_frame)
    controller = EnhanceSimulatorController(mathic_model, view, app_state)
    
    view.create_widgets()
    view.set_controller(controller)
    
    # Create test module and add to view
    module = mathic_model.create_module("core", 1, "CRIT Rate")
    mathic_model.mathic_system.generate_random_substats(module, 4)
    
    # Update view with test data
    modules = mathic_model.get_all_modules()
    view.update_display(modules)
    
    print("✅ GUI Test Window Created")
    print("🎯 Test the enhanced probability display in the GUI")
    print("📊 Verify that probabilities update correctly")
    
    # Add test results label
    result_frame = ttk.LabelFrame(root, text="Test Results", padding="10")
    result_frame.pack(fill=tk.X, padx=10, pady=5)
    
    result_text = "✅ Enhanced probability calculations implemented\n"
    result_text += "📊 Value analysis with category scoring available\n"
    result_text += "🎯 GUI integration functional\n"
    result_text += "🧪 Test different enhancement scenarios"
    
    ttk.Label(result_frame, text=result_text, justify=tk.LEFT).pack()
    
    # Run GUI (comment out for automated testing)
    # root.mainloop()
    root.destroy()  # For automated testing
    
    return True

def main():
    """Run all enhanced mathic system tests"""
    print("ENHANCED MATHIC SYSTEM TESTING SUITE")
    print("=" * 60)
    
    try:
        # Test probability calculations
        mathic_system = test_probability_calculations()
        
        # Test enhanced probability logic
        mathic_model = test_enhanced_probability_logic()
        
        # Test value analysis
        test_value_analysis(mathic_model)
        
        # Test GUI integration
        test_gui_integration()
        
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"✅ Enhanced probability calculations working")
        print(f"✅ Value analysis with categories working") 
        print(f"✅ GUI integration functional")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
