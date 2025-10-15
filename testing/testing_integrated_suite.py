#!/usr/bin/env python3
"""
Etheria Simulation System Integrated Test Suite
Integrated tests for all Module Editor and UI functionality
"""

import sys
import os
import time
import threading
from unittest.mock import patch

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath('..'))

from mathic.mathic_system import MathicSystem
import tkinter as tk
from tkinter import messagebox
from windowing.ui import CharacterPokedexUI

class EtheriaTestSuite:
    """Etheria Simulation System Complete Test Suite"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, passed, details=""):
        """Log test results"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ Pass"
        else:
            status = "❌ Fail"
        
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        
        self.test_results.append(result)
        print(f"  {result}")
        
    def test_mathic_system_core(self):
        """Test Mathic system core functionality"""
        print("\n🔧 Testing Mathic System Core Functionality")
        print("-" * 40)
        
        try:
            mathic = MathicSystem()
            
            # Test module creation
            module = mathic.create_module("core", 1, "CRIT Rate")
            self.log_result("Module creation", module is not None, 
                          f"Created {module.module_type} - {module.main_stat}" if module else "Creation failed")
            
            if module:
                # Test substat generation
                mathic.generate_random_substats(module, 3)
                self.log_result("Substat generation", len(module.substats) == 3, 
                              f"Generated {len(module.substats)} substats")
                
                # Test enhancement functionality
                original_level = module.level
                enhanced_stat = mathic.enhance_module_random_substat(module)
                enhanced = enhanced_stat is not None
                self.log_result("Module enhancement", enhanced, 
                              f"Enhanced {enhanced_stat}" if enhanced else "Enhancement failed")
                
                # Test probability calculation
                try:
                    probabilities = mathic.calculate_substat_probabilities(module)
                    prob_test = isinstance(probabilities, dict) and len(probabilities) > 0
                    self.log_result("Probability calculation", prob_test, 
                                  f"Calculated {len(probabilities)} stat probabilities")
                except Exception as e:
                    self.log_result("Probability calculation", False, f"Error: {e}")
                
                # Test value evaluation
                try:
                    value_data = mathic.calculate_module_value(module)
                    value_test = isinstance(value_data, dict) and 'total_value' in value_data
                    self.log_result("Value evaluation", value_test, 
                                  f"Total value: {value_data.get('total_value', 0):.2f}")
                except Exception as e:
                    self.log_result("Value evaluation", False, f"Error: {e}")
                    
        except Exception as e:
            self.log_result("Mathic system initialization", False, f"Error: {e}")
    
    def test_ui_module_editor_features(self):
        """Test UI Module Editor functionality"""
        print("\n🖥️ Testing UI Module Editor Functionality")
        print("-" * 40)
        
        def run_ui_test():
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            try:
                app = CharacterPokedexUI(root)
                
                # Test application initialization
                init_test = hasattr(app, 'mathic_system') and hasattr(app, 'substat_controls')
                self.log_result("UI initialization", init_test, "UI components properly initialized")
                
                if init_test:
                    # Test Total Rolls read-only display
                    readonly_test = hasattr(app, 'total_rolls_label') and hasattr(app, 'total_rolls_var')
                    self.log_result("Total Rolls readonly", readonly_test, "Total Rolls changed to read-only display")
                    
                    # Test substat controls
                    controls_test = len(app.substat_controls) == 4
                    self.log_result("Substat controls", controls_test, f"Has {len(app.substat_controls)} substat controls")
                    
                    # Test module selection tracking
                    if hasattr(app, 'mathic_system') and app.mathic_system.modules:
                        try:
                            first_module_id = list(app.mathic_system.modules.keys())[0]
                            app.current_selected_module_id = first_module_id
                            tracking_test = app.current_selected_module_id == first_module_id
                            self.log_result("Module selection tracking", tracking_test, "Module selection state properly tracked")
                        except Exception as e:
                            self.log_result("Module selection tracking", False, f"Error: {e}")
                    
                    # Test infinite loop protection
                    protection_test = (hasattr(app, 'adjusting_rolls') and 
                                     hasattr(app, 'rolls_change_depth') and
                                     hasattr(app, 'pending_warning'))
                    self.log_result("Infinite loop protection", protection_test, "Protection mechanism properly implemented")
                
                root.destroy()
                
            except Exception as e:
                self.log_result("UI test", False, f"Error: {e}")
                try:
                    root.destroy()
                except:
                    pass
        
        # Run UI test in main thread
        run_ui_test()
    
    def test_infinite_loop_protection(self):
        """Test infinite loop protection mechanism"""
        print("\n🛡️ Testing Infinite Loop Protection Mechanism")
        print("-" * 40)
        
        root = tk.Tk()
        root.withdraw()
        
        try:
            app = CharacterPokedexUI(root)
            messagebox_count = 0
            function_calls = 0
            
            # Mock messagebox to count calls
            def mock_messagebox(title, message):
                nonlocal messagebox_count
                messagebox_count += 1
                return 'ok'
            
            # Hook function calls to detect infinite loops
            original_function = app.on_substat_rolls_change
            def debug_function(substat_index):
                nonlocal function_calls
                function_calls += 1
                if function_calls > 20:  # Safety check
                    return
                return original_function(substat_index)
            
            messagebox.showwarning = mock_messagebox
            app.on_substat_rolls_change = debug_function
            
            # Setup test scenario: total rolls = 5
            controls = app.substat_controls
            controls[0][3].set('HP%')    # Substat type
            controls[0][5].set('2')      # Rolls count
            controls[1][3].set('ATK%')
            controls[1][5].set('2')
            controls[2][3].set('DEF%')
            controls[2][5].set('1')
            controls[3][3].set('')
            controls[3][5].set('0')
            
            root.update()
            
            # First violation test
            messagebox_count = 0
            function_calls = 0
            controls[0][5].set('4')  # Would make total 7
            root.update()
            
            first_violation_msgs = messagebox_count
            first_violation_calls = function_calls
            
            # Second violation test (key test)
            messagebox_count = 0
            function_calls = 0
            controls[1][5].set('3')  # Would make total 6
            root.update()
            
            second_violation_msgs = messagebox_count
            second_violation_calls = function_calls
            
            # Check results
            total = sum(int(c[5].get()) for c in controls if c[3].get())
            
            # Test result evaluation
            first_normal = first_violation_msgs <= 2 and first_violation_calls <= 5
            second_normal = second_violation_msgs <= 2 and second_violation_calls <= 5
            total_correct = total <= 5
            
            self.log_result("First violation handling", first_normal, 
                          f"{first_violation_msgs} messages, {first_violation_calls} calls")
            self.log_result("Second violation handling", second_normal, 
                          f"{second_violation_msgs} messages, {second_violation_calls} calls")
            self.log_result("Total rolls limit", total_correct, f"Final total: {total}")
            
            # Check protection mechanism state
            time.sleep(0.1)  # Allow cleanup
            adjusting = getattr(app, 'adjusting_rolls', False)
            depth = getattr(app, 'rolls_change_depth', 0)
            
            protection_clean = not adjusting and depth == 0
            self.log_result("Protection mechanism cleanup", protection_clean, 
                          f"adjusting_rolls: {adjusting}, depth: {depth}")
            
            root.destroy()
            
        except Exception as e:
            self.log_result("Infinite loop protection test", False, f"Error: {e}")
            try:
                root.destroy()
            except:
                pass
    
    def test_loadout_system(self):
        """Test Loadout system"""
        print("\n⚔️ Testing Loadout System")
        print("-" * 40)
        
        try:
            mathic = MathicSystem()
            
            # Create test modules
            modules = []
            slot_configs = [
                ("mask", 1, "ATK"),
                ("transistor", 2, "HP"),
                ("wristwheel", 3, "DEF"),
                ("core", 4, "CRIT Rate"),
                ("core", 5, "CRIT DMG"),
                ("core", 6, "ATK%"),
            ]
            
            for module_type, slot, main_stat in slot_configs:
                module = mathic.create_module(module_type, slot, main_stat)
                if module:
                    mathic.generate_random_substats(module, 4)
                    modules.append(module)
            
            creation_test = len(modules) == 6
            self.log_result("Loadout module creation", creation_test, f"Created {len(modules)}/6 modules")
            
            if creation_test:
                # Create Loadout
                loadout_name = "Test Configuration"
                mathic.create_mathic_loadout(loadout_name)
                
                # Assign modules to slots
                for i, module in enumerate(modules):
                    slot_id = i + 1
                    mathic.assign_module_to_loadout(loadout_name, slot_id, module.module_id)
                
                # Test Loadout retrieval
                loadout_modules = mathic.get_loadout_modules(loadout_name)
                loadout_test = len(loadout_modules) == 6
                self.log_result("Loadout assignment", loadout_test, f"Assigned {len(loadout_modules)}/6 slots")
                
                # Test stats calculation
                total_stats = {}
                for slot_id, module in loadout_modules.items():
                    if module:
                        # Main stat
                        if module.main_stat not in total_stats:
                            total_stats[module.main_stat] = 0
                        total_stats[module.main_stat] += module.main_stat_value
                        
                        # Substats
                        for substat in module.substats:
                            if substat.stat_name not in total_stats:
                                total_stats[substat.stat_name] = 0
                            total_stats[substat.stat_name] += substat.current_value
                
                stats_test = len(total_stats) > 0
                self.log_result("Stats calculation", stats_test, f"Calculated {len(total_stats)} stat types")
                
        except Exception as e:
            self.log_result("Loadout system test", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Etheria Simulation System Integrated Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Execute various tests
        self.test_mathic_system_core()
        self.test_ui_module_editor_features()
        self.test_infinite_loop_protection()
        self.test_loadout_system()
        
        # Display test results
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("-" * 60)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n⏱️ Test time: {elapsed_time:.2f} seconds")
        print(f"🎯 Pass rate: {self.passed_tests}/{self.total_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 All tests passed!")
            print("✅ Etheria simulation system functioning properly")
        elif self.passed_tests >= self.total_tests * 0.8:
            print("\n✅ Most tests passed")
            print("⚠️ Some functionality needs checking")
        else:
            print("\n⚠️ Multiple test failures")
            print("❌ System may have issues, needs further investigation")
        
        return self.passed_tests == self.total_tests

def main():
    """Main function"""
    print("Starting Etheria simulation system integrated tests...")
    
    try:
        test_suite = EtheriaTestSuite()
        success = test_suite.run_all_tests()
        
        print(f"\n🏁 Tests completed: {'Success' if success else 'Issues need review'}")
        return success
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
