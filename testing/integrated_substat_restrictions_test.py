#!/usr/bin/env python3
"""
Comprehensive Substat Restrictions Testing Suite
Integrates all substat restriction tests and demonstrations
"""

import sys
import os
import tkinter as tk
from unittest.mock import patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mathic.mathic_system import MathicSystem


class SubstatRestrictionsTestSuite:
    """Comprehensive test suite for substat restrictions"""
    
    def __init__(self):
        self.system = MathicSystem()
        self.test_cases = [
            {
                'module_type': 'mask',
                'main_stat': 'ATK',
                'expected_restricted': ['ATK', 'Effect RES', 'HP%', 'DEF%']
            },
            {
                'module_type': 'transistor',
                'main_stat': 'HP',
                'expected_restricted': ['ATK%', 'DEF%', 'HP', 'Effect ACC']
            },
            {
                'module_type': 'wristwheel',
                'main_stat': 'DEF',
                'expected_restricted': ['HP%', 'ATK%', 'CRIT DMG', 'DEF']
            },
            {
                'module_type': 'core',
                'main_stat': 'CRIT Rate',
                'expected_restricted': []  # Core should have no restrictions
            }
        ]
        self.results = []
    
    def run_all_tests(self):
        """Run all integrated tests"""
        print("🧪 Comprehensive Substat Restrictions Test Suite")
        print("=" * 70)
        
        # Run each test component
        self.test_configuration_setup()
        self.test_backend_restrictions()
        self.test_gui_model_integration()
        self.test_full_application()
        self.test_mathic_system_integration()
        self.demonstrate_feature()
        
        # Final summary
        self.print_summary()
    
    def test_configuration_setup(self):
        """Test 1: Verify configuration is properly set up"""
        print("\n📋 Test 1: Configuration Setup")
        print("-" * 40)
        
        config = self.system.config
        module_types = config.get("module_types", {})
        
        config_passed = True
        for case in self.test_cases:
            module_type = case['module_type']
            expected_restrictions = case['expected_restricted']
            
            if module_type in module_types:
                actual_restrictions = module_types[module_type].get("restricted_substats", [])
                if set(actual_restrictions) == set(expected_restrictions):
                    print(f"   ✅ {module_type.capitalize()}: {len(actual_restrictions)} restrictions configured")
                else:
                    print(f"   ❌ {module_type.capitalize()}: Configuration mismatch")
                    print(f"      Expected: {expected_restrictions}")
                    print(f"      Actual: {actual_restrictions}")
                    config_passed = False
            else:
                print(f"   ❌ {module_type.capitalize()}: Not found in configuration")
                config_passed = False
        
        self.results.append(("Configuration Setup", config_passed))
        print(f"\n   Result: {'✅ PASS' if config_passed else '❌ FAIL'}")
    
    def test_backend_restrictions(self):
        """Test 2: Backend system enforcement"""
        print("\n🔧 Test 2: Backend System Enforcement")
        print("-" * 40)
        
        backend_passed = True
        for i, case in enumerate(self.test_cases, 1):
            print(f"\n   {i}. Testing {case['module_type'].upper()} module:")
            
            # Create module
            module = self.system.create_module(
                case['module_type'], 
                1, 
                case['main_stat']
            )
            
            if module:
                available_substats = self.system.get_available_substats_for_module(module)
                print(f"      Available substats: {len(available_substats)}")
                
                # Check restrictions are applied
                restricted_stats = case['expected_restricted']
                violations = [stat for stat in restricted_stats if stat in available_substats]
                
                if violations:
                    print(f"      ❌ FAIL: Found restricted stats: {violations}")
                    backend_passed = False
                else:
                    print(f"      ✅ PASS: All {len(restricted_stats)} restrictions applied")
            else:
                print(f"      ❌ FAIL: Could not create {case['module_type']} module")
                backend_passed = False
        
        self.results.append(("Backend Enforcement", backend_passed))
        print(f"\n   Result: {'✅ PASS' if backend_passed else '❌ FAIL'}")
    
    def test_gui_model_integration(self):
        """Test 3: GUI Model Integration"""
        print("\n🎮 Test 3: GUI Model Integration")
        print("-" * 40)
        
        try:
            from windowing.models import MathicModel
            
            model = MathicModel()
            gui_passed = True
            
            for case in self.test_cases:
                module_type = case['module_type']
                main_stat = case['main_stat']
                expected_restrictions = case['expected_restricted']
                
                available = model.get_available_substats(
                    exclude_main_stat=main_stat,
                    module_type=module_type
                )
                available_clean = [s for s in available if s]
                
                print(f"   {module_type.capitalize()}: {len(available_clean)} substats available")
                
                # Check restrictions
                violations = [s for s in expected_restrictions if s in available_clean]
                if violations:
                    print(f"      ❌ FAIL: Found restricted substats: {violations}")
                    gui_passed = False
                else:
                    print(f"      ✅ PASS: Restrictions applied correctly")
            
            self.results.append(("GUI Model Integration", gui_passed))
            print(f"\n   Result: {'✅ PASS' if gui_passed else '❌ FAIL'}")
            
        except ImportError as e:
            print(f"   ❌ Could not import GUI models: {e}")
            self.results.append(("GUI Model Integration", False))
    
    def test_full_application(self):
        """Test 4: Full Application Integration"""
        print("\n🚀 Test 4: Full Application Integration")
        print("-" * 40)
        
        try:
            from windowing.ui_mvc import EtheriaApplication
            
            # Create application
            app = EtheriaApplication()
            print("   ✅ Application created successfully")
            
            # Get models for testing
            models = app.get_models()
            mathic_model = models['mathic']
            
            # Test each module type
            app_passed = True
            for case in self.test_cases:
                module_type = case['module_type']
                main_stat = case['main_stat']
                restrictions = case['expected_restricted']
                
                available = mathic_model.get_available_substats(
                    exclude_main_stat=main_stat,
                    module_type=module_type
                )
                available_clean = [s for s in available if s]
                
                violations = [r for r in restrictions if r in available_clean]
                passed = len(violations) == 0
                
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"   {module_type.capitalize()}: {status} ({len(available_clean)} substats)")
                
                if not passed:
                    app_passed = False
            
            self.results.append(("Full Application", app_passed))
            print(f"\n   Result: {'✅ PASS' if app_passed else '❌ FAIL'}")
            
        except Exception as e:
            print(f"   ❌ Application test failed: {e}")
            self.results.append(("Full Application", False))
    
    def test_mathic_system_integration(self):
        """Test 5: Mathic System Integration"""
        print("\n⚙️  Test 5: Mathic System Integration")
        print("-" * 40)
        
        integration_passed = True
        
        for case in self.test_cases:
            module_type = case['module_type']
            main_stat = case['main_stat']
            
            print(f"\n   Testing {module_type} module creation:")
            
            # Create module
            module = self.system.create_module(module_type, 1, main_stat)
            if module:
                print(f"      ✅ Module created: {module.module_id}")
                
                # Check available substats
                available = self.system.get_available_substats_for_module(module)
                print(f"      Available substats: {len(available)}")
                
                # Test adding a substat
                if available:
                    test_substat = available[0]
                    success = module.add_substat(test_substat, 10)
                    if success:
                        print(f"      ✅ Added substat: {test_substat}")
                    else:
                        print(f"      ❌ Failed to add substat: {test_substat}")
                        integration_passed = False
            else:
                print(f"      ❌ Failed to create {module_type} module")
                integration_passed = False
        
        self.results.append(("System Integration", integration_passed))
        print(f"\n   Result: {'✅ PASS' if integration_passed else '❌ FAIL'}")
    
    def demonstrate_feature(self):
        """Demonstration: Show the implemented feature"""
        print("\n🎯 Feature Demonstration")
        print("-" * 40)
        
        print("\n   📋 Configuration Summary:")
        all_substats = list(self.system.config.get("substats", {}).keys())
        print(f"      Total substats available: {len(all_substats)}")
        
        print("\n   🔒 Module Type Restrictions:")
        module_types = self.system.config.get("module_types", {})
        
        for module_type, config in module_types.items():
            restrictions = config.get("restricted_substats", [])
            main_stats = config.get("main_stat_options", [])
            
            print(f"\n      {module_type.upper()}:")
            print(f"         Main stat options: {main_stats}")
            print(f"         Restricted substats: {restrictions}")
            
            # Show available substats
            if main_stats:
                module = self.system.create_module(module_type, 1, main_stats[0])
                if module:
                    available = self.system.get_available_substats_for_module(module)
                    print(f"         Available substats: {len(available)}")
        
        print("\n   🎉 Feature Implementation Details:")
        print("      • Configuration-driven restrictions")
        print("      • Backend and frontend enforcement")
        print("      • Automatic GUI dropdown updates")
        print("      • Comprehensive test coverage")
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 70)
        
        passed_count = sum(1 for _, passed in self.results if passed)
        total_count = len(self.results)
        
        for test_name, passed in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 Overall Result: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED! Substat restrictions are fully implemented!")
        else:
            print("⚠️  Some tests failed. Please review the implementation.")
        
        print("\n🔧 Implementation Features:")
        print("   • Mask: Cannot have ATK, Effect RES, HP%, DEF%")
        print("   • Transistor: Cannot have ATK%, DEF%, HP, Effect ACC")
        print("   • Wristwheel: Cannot have HP%, ATK%, CRIT DMG, DEF")
        print("   • Core: No restrictions (all substats available)")
        
        print(f"\n{'='*70}")


def main():
    """Main function to run the comprehensive test suite"""
    suite = SubstatRestrictionsTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()
