#!/usr/bin/env python3
"""
Test script for Shell Pokedex Matrix Icons functionality
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from windowing.models import ShellModel
from windowing.views import ShellListView


def test_matrix_icons_display():
    """Test matrix icons display in Shell Pokedex"""
    print("=== Testing Shell Pokedex Matrix Icons ===")
    
    try:
        # Create main window
        root = tk.Tk()
        root.title("Shell Pokedex Matrix Icons Test")
        root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create ShellModel
        shell_model = ShellModel()
        
        # Create ShellListView
        shell_view = ShellListView(main_frame)
        shell_view.create_widgets()
        
        # Get matrix effects and setup filter options
        matrices = shell_model.get_all_matrix_effects()
        classes = shell_model.get_shell_classes()
        rarities = shell_model.get_shell_rarities()
        
        print(f"✅ Setting up filter options:")
        print(f"    Classes: {classes}")
        print(f"    Rarities: {rarities}")
        print(f"    Matrix Effects: {len(matrices)}")
        
        # Update filter options (this will create checkboxes with icons)
        shell_view.update_filter_options(classes, rarities, matrices)
        
        # Test image loading statistics
        loaded_images = len(shell_view.matrix_images)
        print(f"✅ Loaded {loaded_images}/{len(matrices)} matrix icons")
        
        # Show which images were loaded successfully
        successful_matrices = list(shell_view.matrix_images.keys())
        print(f"✅ Successfully loaded icons for: {successful_matrices[:5]}...")
        
        # Load shell data
        shells = shell_model.get_all_shells()
        shell_view.update_display(shells)
        print(f"✅ Loaded {len(shells)} shells")
        
        print(f"\n🎉 Shell Pokedex with Matrix Icons is ready!")
        print(f"📊 Summary:")
        print(f"   - Total shells: {len(shells)}")
        print(f"   - Matrix effects with icons: {loaded_images}/{len(matrices)}")
        print(f"   - Shell classes: {len(classes)}")
        print(f"   - Shell rarities: {len(rarities)}")
        print(f"\n✅ Matrix icons test completed successfully!")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in matrix icons test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_files_coverage():
    """Test coverage of image files for all matrix effects"""
    print("\n=== Testing Image Files Coverage ===")
    
    try:
        shell_model = ShellModel()
        matrices = shell_model.get_all_matrix_effects()
        
        img_dir = "./img/matrices/"
        if not os.path.exists(img_dir):
            print(f"❌ Image directory {img_dir} not found")
            return False
        
        available_files = os.listdir(img_dir)
        
        coverage_report = []
        missing_files = []
        
        for matrix in matrices:
            expected_file = f"set_{matrix.lower()}.webp"
            if expected_file in available_files:
                coverage_report.append(f"✅ {matrix} -> {expected_file}")
            else:
                missing_files.append(f"❌ {matrix} -> {expected_file} (missing)")
                coverage_report.append(f"❌ {matrix} -> {expected_file} (missing)")
        
        print(f"📊 Image Coverage Report:")
        for report in coverage_report:
            print(f"    {report}")
        
        print(f"\n📈 Coverage Statistics:")
        print(f"    Total matrices: {len(matrices)}")
        print(f"    Images found: {len(matrices) - len(missing_files)}")
        print(f"    Missing images: {len(missing_files)}")
        print(f"    Coverage: {((len(matrices) - len(missing_files)) / len(matrices)) * 100:.1f}%")
        
        if missing_files:
            print(f"\n⚠️  Missing image files:")
            for missing in missing_files:
                print(f"    {missing}")
        else:
            print(f"\n🎉 All matrix effects have corresponding image files!")
        
        return len(missing_files) == 0
        
    except Exception as e:
        print(f"❌ Error in coverage test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Shell Pokedex Matrix Icons Test")
    print("=" * 50)
    
    # Test image files coverage first
    coverage_ok = test_image_files_coverage()
    
    if coverage_ok:
        print(f"\n✅ All image files are available. Proceeding with GUI test...")
        
        # Test the actual GUI display
        gui_ok = test_matrix_icons_display()
        
        if gui_ok:
            print(f"\n✅ Shell Pokedex Matrix Icons test completed successfully!")
            return 0
        else:
            print(f"\n❌ GUI test failed!")
            return 1
    else:
        print(f"\n⚠️  Some image files are missing, but proceeding with GUI test anyway...")
        gui_ok = test_matrix_icons_display()
        return 0 if gui_ok else 1


if __name__ == "__main__":
    exit(main())
