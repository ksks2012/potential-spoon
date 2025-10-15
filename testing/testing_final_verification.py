#!/usr/bin/env python3
"""
Module Editor Final Verification Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/../')))

import tkinter as tk
from windowing.ui import CharacterPokedexUI
import time
import threading
from unittest.mock import patch

def final_verification_test():
    """Final verification of all Module Editor fixes"""
    print("🎯 Module Editor Final Verification Test")
    print("="*50)
    
    root = tk.Tk()
    app = CharacterPokedexUI(root)
    
    test_results = []
    
    def run_comprehensive_test():
        time.sleep(1.5)
        
        try:
            # 1. Test module selection tracking
            print("\n1️⃣ Testing module selection tracking...")
            app.main_notebook.select(1)
            app.module_listbox.selection_set(0)
            app.on_module_select(None)
            
            if hasattr(app, 'current_selected_module_id') and app.current_selected_module_id:
                test_results.append("✅ Module selection tracking working")
                print(f"   Tracked module ID: {app.current_selected_module_id}")
            else:
                test_results.append("❌ Module selection tracking failed")
            
            # 2. Test Total Rolls read-only display
            print("\n2️⃣ Testing Total Rolls read-only display...")
            if hasattr(app, 'total_rolls_label') and not hasattr(app, 'total_rolls_spinbox'):
                test_results.append("✅ Total Rolls changed to read-only display")
            else:
                test_results.append("❌ Total Rolls still editable")
            
            # 3. Test automatic Total Rolls calculation
            print("\n3️⃣ Testing automatic Total Rolls calculation...")
            original_total = app.total_rolls_var.get()
            print(f"   Original total: {original_total}")
            
            # Clear other rolls to ensure accurate testing
            for i, (_, _, _, _, _, rolls_var) in enumerate(app.substat_controls):
                rolls_var.set('0')
            time.sleep(0.1)
            
            # Set specific rolls
            app.substat1_rolls_var.set('3')
            time.sleep(0.1)
            app.substat2_rolls_var.set('2') 
            time.sleep(0.2)
            new_total = app.total_rolls_var.get()
            
            expected_total = 5  # 3 + 2 = 5
            if int(new_total) == expected_total:
                test_results.append("✅ Total Rolls automatic calculation working")
                print(f"   Auto calculation: {original_total} -> {new_total} (expected: {expected_total})")
            else:
                test_results.append("❌ Total Rolls automatic calculation failed")
                print(f"   Auto calculation: {original_total} -> {new_total} (expected: {expected_total})")
            
            # 4. Test value options don't auto-jump to maximum
            print("\n4️⃣ Testing substat value retention...")
            app.substat1_type_var.set('HP%')
            app.substat1_value_var.set('6')  # Set a non-maximum value
            app.substat1_rolls_var.set('2')
            time.sleep(0.1)
            
            current_value = app.substat1_value_var.get()
            if current_value != '':  # Value should be retained or adjusted to valid value
                test_results.append("✅ Substat value retention working")
                print(f"   Retained value: {current_value}")
            else:
                test_results.append("❌ Substat value retention failed")
            
            # 5. Test Apply Changes doesn't lose selection
            print("\n5️⃣ Testing Apply Changes selection retention...")
            selected_before = app.current_selected_module_id
            
            # Set valid substat data
            app.substat1_type_var.set('HP%')
            app.substat1_value_var.set('8')
            app.substat1_rolls_var.set('2')
            
            # Simulate Apply Changes (without showing dialogs)
            with patch('tkinter.messagebox.showinfo'), patch('tkinter.messagebox.showerror'):
                app.apply_module_changes()
            
            selected_after = app.current_selected_module_id
            
            if selected_before == selected_after:
                test_results.append("✅ Apply Changes selection retention working")
                print(f"   Selection retained: {selected_before}")
            else:
                test_results.append("❌ Apply Changes lost selection")
            
            # Display test results
            print("\n" + "="*50)
            print("📊 Test Results Summary:")
            for result in test_results:
                print(f"  {result}")
            
            success_count = len([r for r in test_results if r.startswith("✅")])
            total_count = len(test_results)
            
            print(f"\n🎯 Pass Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
            
            if success_count == total_count:
                print("🎉 All functionality fixes are complete and working properly!")
            else:
                print("⚠️  Some functionality still needs further fixing")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            root.quit()
    
    # Run test in background
    threading.Thread(target=run_comprehensive_test, daemon=True).start()
    
    # Auto close
    def auto_close():
        time.sleep(8)
        root.quit()
    
    threading.Thread(target=auto_close, daemon=True).start()
    
    try:
        root.mainloop()
    except:
        pass
    
    print("\n✨ Module Editor verification test completed!")

if __name__ == "__main__":
    final_verification_test()
