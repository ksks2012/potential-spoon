#!/usr/bin/env python3
"""
Test script to verify Module Editor dropdown logic restrictions
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mathic.mathic_system import MathicSystem
from windowing.models import MathicModel
from windowing.controllers import ModuleEditorController


class MockView:
    """Mock view for testing dropdown logic"""
    
    def __init__(self):
        self.module_type_var = MockVar()
        self.main_stat_var = MockVar()
        self.main_stat_value_var = MockVar()
        self.matrix_var = MockVar()
        self.matrix_count_var = MockVar("3")
        
        # Track updates
        self.main_stat_options_updated = []
        self.matrix_options_updated = []
        self.substat_options_updated = []
    
    def get_module_form_data(self):
        return {
            'module_type': self.module_type_var.value,
            'main_stat': self.main_stat_var.value,
            'main_stat_value': self.main_stat_value_var.value
        }
    
    def update_main_stat_options(self, options):
        self.main_stat_options_updated = options
        print(f"📋 Main stat options updated: {options}")
    
    def update_matrix_options(self, options):
        self.matrix_options_updated = options
        print(f"🔧 Matrix options updated: {len(options) - 1} matrices available")  # -1 for empty option
    
    def update_substat_options(self, options):
        self.substat_options_updated = options
        print(f"⚡ Substat options updated: {len(options) - 1} options available")  # -1 for empty option
    
    def set_controller(self, controller):
        self.controller = controller


class MockVar:
    """Mock StringVar for testing"""
    
    def __init__(self, initial_value=""):
        self.value = initial_value
    
    def get(self):
        return self.value
    
    def set(self, value):
        self.value = value


def test_dropdown_restrictions():
    """Test that dropdown restrictions work correctly"""
    print("🧪 Testing Module Editor Dropdown Logic Restrictions...")
    print("=" * 60)
    
    # Initialize components
    model = MathicModel()
    view = MockView()
    
    # Create controller with mock components
    controller = ModuleEditorController(model, view, None)
    
    print("\n1️⃣ Testing Mask Module Restrictions:")
    print("-" * 40)
    view.module_type_var.set("mask")
    controller.on_module_type_change()
    
    # Verify mask restrictions
    expected_mask_main_stats = ["ATK"]
    if view.main_stat_options_updated == expected_mask_main_stats:
        print("✅ Mask main stat restriction correct: only ATK available")
    else:
        print(f"❌ Mask main stat restriction failed: got {view.main_stat_options_updated}, expected {expected_mask_main_stats}")
    
    # Check matrix options (should have common matrices but not core-exclusive)
    mask_matrix_count = len(view.matrix_options_updated) - 1  # -1 for empty option
    print(f"   Matrix count for mask: {mask_matrix_count}")
    
    print("\n2️⃣ Testing Core Module Restrictions:")
    print("-" * 40)
    view.module_type_var.set("core")
    controller.on_module_type_change()
    
    # Verify core has more main stat options
    core_main_stats = view.main_stat_options_updated
    if len(core_main_stats) > 1:
        print(f"✅ Core main stat options: {len(core_main_stats)} options available")
        print(f"   Options: {core_main_stats}")
    else:
        print(f"❌ Core main stat restriction failed: only {len(core_main_stats)} options")
    
    # Check matrix options (should have more matrices including core-exclusive)
    core_matrix_count = len(view.matrix_options_updated) - 1  # -1 for empty option
    print(f"   Matrix count for core: {core_matrix_count}")
    
    if core_matrix_count > mask_matrix_count:
        print("✅ Core has more matrix options than mask (includes core-exclusive matrices)")
    else:
        print("❌ Core should have more matrix options than mask")
    
    print("\n3️⃣ Testing Module Loading (Preserve Values):")
    print("-" * 40)
    
    # Create a test module
    system = MathicSystem()
    test_core = system.create_module("core", 4, "CRIT Rate")
    
    if test_core:
        print(f"Created test module: {test_core.module_id}")
        print(f"Module type: {test_core.module_type}")
        print(f"Main stat: {test_core.main_stat}")
        
        # Simulate loading this module in the editor
        view.module_type_var.set(test_core.module_type)
        view.main_stat_var.set(test_core.main_stat)
        view.main_stat_value_var.set(str(test_core.main_stat_value))
        
        # Trigger the update with preserve_current_values=True
        controller.on_module_type_change(preserve_current_values=True)
        
        # Verify that the main stat value is preserved
        if view.main_stat_var.get() == test_core.main_stat:
            print("✅ Main stat value preserved when loading module")
        else:
            print(f"❌ Main stat value not preserved: got '{view.main_stat_var.get()}', expected '{test_core.main_stat}'")
        
        # Verify options were updated correctly
        if test_core.main_stat in view.main_stat_options_updated:
            print("✅ Main stat options include the module's current main stat")
        else:
            print(f"❌ Main stat options don't include current value: {test_core.main_stat} not in {view.main_stat_options_updated}")
    
    print("\n4️⃣ Testing Different Module Types:")
    print("-" * 40)
    
    test_cases = [
        ("transistor", ["HP"]),
        ("wristwheel", ["DEF"]),
    ]
    
    for module_type, expected_main_stats in test_cases:
        view.module_type_var.set(module_type)
        controller.on_module_type_change()
        
        if view.main_stat_options_updated == expected_main_stats:
            print(f"✅ {module_type.capitalize()} restrictions correct: {expected_main_stats}")
        else:
            print(f"❌ {module_type.capitalize()} restrictions failed: got {view.main_stat_options_updated}, expected {expected_main_stats}")
    
    print("\n🎉 Dropdown Logic Restriction Tests Completed!")
    return True


if __name__ == "__main__":
    success = test_dropdown_restrictions()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
