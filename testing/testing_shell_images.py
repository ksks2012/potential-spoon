#!/usr/bin/env python3
"""
Test script for Shell Pokedex with Shell Images
Tests the shell image loading and display functionality
"""

import sys
import os
sys.path.insert(0, '.')

import tkinter as tk
from tkinter import ttk
from windowing.models import ShellModel
from windowing.views import ShellListView
from windowing.controllers import ShellController
from PIL import Image
import glob

def test_shell_image_coverage():
    """Test shell image file coverage"""
    print("Shell Pokedex Shell Images Test")
    print("=" * 50)
    
    print("\n=== Testing Shell Image Files Coverage ===")
    
    # Get all shell names from database
    try:
        shell_model = ShellModel()
        all_shells = shell_model.get_all_shells()
        print(f"📊 Shell Database Report:")
        print(f"    Total shells in database: {len(all_shells)}")
        
        # Get all shell image files
        shell_image_path = "./img/shells/"
        image_files = glob.glob(os.path.join(shell_image_path, "shell_*.webp"))
        print(f"    Total shell images available: {len(image_files)}")
        
        # Test coverage
        coverage_report = []
        missing_images = []
        
        for shell in all_shells:
            shell_name = shell.get('name', '')
            # Convert shell name to expected file format
            file_name = f"shell_{shell_name.lower().replace(' ', '_').replace('-', '_')}.webp"
            image_path = os.path.join(shell_image_path, file_name)
            
            if os.path.exists(image_path):
                coverage_report.append(f"    ✅ {shell_name} -> {file_name}")
            else:
                missing_images.append(f"    ❌ {shell_name} -> {file_name}")
                
        print(f"\n📈 Coverage Report:")
        for report in coverage_report[:5]:  # Show first 5
            print(report)
        if len(coverage_report) > 5:
            print(f"    ... and {len(coverage_report) - 5} more")
            
        if missing_images:
            print(f"\n❌ Missing Images:")
            for missing in missing_images:
                print(missing)
        else:
            print(f"\n🎉 All shells have corresponding image files!")
            
        print(f"\n📊 Coverage Statistics:")
        print(f"    Images found: {len(coverage_report)}")
        print(f"    Missing images: {len(missing_images)}")
        print(f"    Coverage: {100 * len(coverage_report) // len(all_shells)}%")
        
        return len(missing_images) == 0
        
    except Exception as e:
        print(f"❌ Error during coverage test: {e}")
        return False

def test_shell_image_loading():
    """Test shell image loading functionality"""
    print("\n=== Testing Shell Image Loading ===")
    
    try:
        # Test image loading for sample shells
        shell_model = ShellModel()
        all_shells = shell_model.get_all_shells()
        
        # Create a test view to test image loading
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        test_frame = ttk.Frame(root)
        shell_view = ShellListView(test_frame)
        
        print(f"✅ Setting up image loading test...")
        
        # Test loading images for first few shells
        test_shells = all_shells[:3]  # Test first 3 shells
        loaded_count = 0
        
        for shell in test_shells:
            shell_name = shell.get('name', '')
            try:
                shell_image = shell_view._load_shell_image(shell_name)
                if shell_image:
                    print(f"    ✅ Successfully loaded image for: {shell_name}")
                    loaded_count += 1
                else:
                    print(f"    ❌ Failed to load image for: {shell_name}")
            except Exception as e:
                print(f"    ❌ Error loading image for {shell_name}: {e}")
        
        print(f"✅ Image loading test completed: {loaded_count}/{len(test_shells)} successful")
        
        root.destroy()
        return loaded_count > 0
        
    except Exception as e:
        print(f"❌ Error during image loading test: {e}")
        return False

def test_gui_integration():
    """Test GUI integration with shell images"""
    print("\n=== Testing GUI Integration ===")
    
    try:
        # Initialize model
        shell_model = ShellModel()
        
        # Create GUI
        root = tk.Tk()
        root.title("Shell Pokedex Image Test")
        root.geometry("800x600")
        
        # Create shell view
        shell_frame = ttk.Frame(root, padding="10")
        shell_frame.pack(fill=tk.BOTH, expand=True)
        
        shell_view = ShellListView(shell_frame)
        shell_view.create_widgets()
        
        # Initialize shells directly without controller for testing
        all_shells = shell_model.get_all_shells()
        shell_view.update_display(all_shells)
        
        print(f"✅ GUI components initialized successfully")
        print(f"✅ Shell Pokedex with Shell Images is ready!")
        print(f"📊 Summary:")
        
        print(f"   - Total shells: {len(all_shells)}")
        print(f"   - Shell image path: {shell_view.shell_image_path}")
        print(f"   - Image cache initialized: {hasattr(shell_view, 'shell_images')}")
        
        print(f"\n🎉 Shell Pokedex with Shell Images test completed successfully!")
        print(f"Click on any shell in the list to see its image in the details panel.")
        
        # Don't start mainloop in test, just validate setup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔧 Starting Shell Pokedex Shell Images Testing...")
    
    # Test 1: Coverage
    coverage_ok = test_shell_image_coverage()
    
    # Test 2: Image loading
    loading_ok = test_shell_image_loading()
    
    # Test 3: GUI integration
    gui_ok = test_gui_integration()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 FINAL TEST RESULTS:")
    print(f"   Coverage Test: {'✅ PASS' if coverage_ok else '❌ FAIL'}")
    print(f"   Image Loading: {'✅ PASS' if loading_ok else '❌ FAIL'}")
    print(f"   GUI Integration: {'✅ PASS' if gui_ok else '❌ FAIL'}")
    
    if coverage_ok and loading_ok and gui_ok:
        print(f"\n🚀 All tests passed! Shell Pokedex Shell Images is ready for use!")
    else:
        print(f"\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
