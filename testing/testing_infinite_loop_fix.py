#!/usr/bin/env python3
"""
Module Editor Infinite Loop Fix Verification Test
Specialized test for verifying infinite loop problem fixes
"""

import sys
import os
import time
import threading

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath('..'))

import tkinter as tk
from tkinter import messagebox
from windowing.ui import CharacterPokedexUI

def test_infinite_loop_fix():
    """Specialized test for infinite loop fix"""
    print("🛡️ Module Editor Infinite Loop Fix Verification Test")
    print("=" * 50)
    
    root = tk.Tk()
    root.withdraw()
    ui = CharacterPokedexUI(root)
    
    messagebox_count = 0
    function_calls = 0
    test_results = []
    
    def mock_messagebox(title, message):
        nonlocal messagebox_count
        messagebox_count += 1
        print(f"  📨 Message #{messagebox_count}: {title}")
        if messagebox_count > 20:  # Safety check
            print("❌ Infinite loop detected!")
        return 'ok'
    
    # Hook function calls to detect infinite loops
    original_function = ui.on_substat_rolls_change
    def debug_function(substat_index):
        nonlocal function_calls
        function_calls += 1
        if function_calls > 50:  # Safety check
            print("❌ Infinite function calls detected!")
            return
        return original_function(substat_index)
    
    messagebox.showwarning = mock_messagebox
    ui.on_substat_rolls_change = debug_function
    
    # Test 1: Original reported scenario
    print("\n🎯 Test 1: Original reported scenario")
    controls = ui.substat_controls
    
    # Setup: total = 5
    controls[0][3].set('HP%')
    controls[0][5].set('2') 
    controls[1][3].set('ATK%')
    controls[1][5].set('2')
    controls[2][3].set('DEF%')
    controls[2][5].set('1')
    controls[3][3].set('')
    controls[3][5].set('0')
    root.update()
    
    # First violation
    messagebox_count = 0
    function_calls = 0
    controls[0][5].set('4')
    root.update()
    time.sleep(0.1)
    
    first_violation_msgs = messagebox_count
    first_violation_calls = function_calls
    
    # Second violation (key test)
    messagebox_count = 0
    function_calls = 0
    controls[1][5].set('3')
    root.update()
    time.sleep(0.1)
    
    second_violation_msgs = messagebox_count
    second_violation_calls = function_calls
    
    # Check results
    total = sum(int(c[5].get()) for c in controls if c[3].get())
    test1_pass = (first_violation_msgs <= 2 and 
                  second_violation_msgs <= 2 and
                  first_violation_calls <= 5 and
                  second_violation_calls <= 5 and
                  total <= 5)
    
    test_results.append(('Original scenario', test1_pass))
    print(f"  First violation: {first_violation_msgs} messages, {first_violation_calls} calls")
    print(f"  Second violation: {second_violation_msgs} messages, {second_violation_calls} calls")
    print(f"  Final total: {total}")
    print(f"  Result: {'✅ Pass' if test1_pass else '❌ Fail'}")
    
    # Test 2: Rapid consecutive violations
    print("\n🎯 Test 2: Rapid consecutive violations")
    messagebox_count = 0
    function_calls = 0
    
    # Reset to clean state
    for i in range(4):
        controls[i][3].set('')
        controls[i][5].set('0')
    root.update()
    
    # Setup and trigger multiple rapid violations
    controls[0][3].set('ATK%')
    controls[0][5].set('3')
    controls[1][3].set('DEF%')
    controls[1][5].set('3')  # Total = 6
    controls[2][3].set('HP%')
    controls[2][5].set('2')  # Total = 8
    root.update()
    time.sleep(0.1)
    
    total = sum(int(c[5].get()) for c in controls if c[3].get())
    test2_pass = (messagebox_count <= 10 and function_calls <= 20 and total <= 5)
    
    test_results.append(('Rapid violations', test2_pass))
    print(f"  Messages: {messagebox_count}, Calls: {function_calls}, Total: {total}")
    print(f"  Result: {'✅ Pass' if test2_pass else '❌ Fail'}")
    
    # Test 3: Protection mechanism cleanup
    print("\n🎯 Test 3: Protection mechanism state cleanup")
    time.sleep(0.2)  # Allow cleanup
    
    adjusting = getattr(ui, 'adjusting_rolls', False)
    depth = getattr(ui, 'rolls_change_depth', 0)
    
    test3_pass = not adjusting and depth == 0
    test_results.append(('Protection cleanup', test3_pass))
    print(f"  adjusting_rolls: {adjusting}")
    print(f"  rolls_change_depth: {depth}")
    print(f"  Result: {'✅ Pass' if test3_pass else '❌ Fail'}")
    
    # Final evaluation
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in test_results:
        status = '✅ Pass' if passed else '❌ Fail'
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        print("✅ Original infinite loop issue: Resolved")
        print("✅ First violation handling: Normal")
        print("✅ Second violation handling: Normal")
        print("✅ Rapid violation handling: Normal")
        print("✅ Protection mechanism: Normal")
        print("✅ Value adjustment logic: Normal")
        print("\n🛡️ Infinite loop error completely fixed!")
    else:
        print("⚠️ Some issues still need attention")
        print("Fix may require further adjustments.")
    
    root.destroy()
    return all_passed

def quick_test():
    """Quick test - no GUI interaction required"""
    print("\n⚡ Quick Infinite Loop Protection Test")
    print("-" * 30)
    
    try:
        root = tk.Tk()
        root.withdraw()
        ui = CharacterPokedexUI(root)
        
        # Check if protection mechanisms exist
        protection_flags = [
            hasattr(ui, 'adjusting_rolls'),
            hasattr(ui, 'rolls_change_depth'),
            hasattr(ui, 'pending_warning')
        ]
        
        protection_count = sum(protection_flags)
        print(f"  Protection flags: {protection_count}/3 exist")
        
        # Check initial state
        adjusting = getattr(ui, 'adjusting_rolls', None)
        depth = getattr(ui, 'rolls_change_depth', None)
        pending = getattr(ui, 'pending_warning', None)
        
        initial_state_ok = (adjusting == False and depth == 0 and pending is None)
        print(f"  Initial state: {'✅ Normal' if initial_state_ok else '❌ Abnormal'}")
        
        # Check if functions exist
        functions_exist = [
            hasattr(ui, 'on_substat_rolls_change'),
            hasattr(ui, 'schedule_warning_message'),
            hasattr(ui, 'update_total_rolls_display')
        ]
        
        functions_count = sum(functions_exist)
        print(f"  Key functions: {functions_count}/3 exist")
        
        root.destroy()
        
        overall_ok = protection_count == 3 and initial_state_ok and functions_count == 3
        print(f"  Overall status: {'✅ Ready' if overall_ok else '❌ Issues found'}")
        
        return overall_ok
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Main function"""
    print("Starting infinite loop fix verification...")
    
    try:
        # Run quick test first
        quick_ok = quick_test()
        
        if quick_ok:
            # Run full test
            success = test_infinite_loop_fix()
        else:
            print("\n❌ Quick test failed, skipping full test")
            success = False
            
        print(f"\n🏁 Verification result: {'✅ Fix successful' if success else '⚠️ Needs review'}")
        return success
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
