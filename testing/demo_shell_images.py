#!/usr/bin/env python3
"""
Demo script for Shell Pokedex with Shell Images
Interactive demonstration of shell image display functionality
"""

import sys
import os
sys.path.insert(0, '.')

import tkinter as tk
from tkinter import ttk
from windowing.models import ShellModel
from windowing.views import ShellListView

def main():
    """Demo application for shell images"""
    try:
        # Initialize model
        shell_model = ShellModel()
        
        # Create GUI
        root = tk.Tk()
        root.title("Shell Pokedex with Shell Images - Demo")
        root.geometry("1000x700")
        
        # Add title
        title_label = ttk.Label(root, text="Shell Pokedex with Shell Images", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(root, 
                                text="Click on any shell in the list to see its image and details",
                                font=("Arial", 10))
        instructions.pack(pady=5)
        
        # Create shell view
        shell_frame = ttk.Frame(root, padding="10")
        shell_frame.pack(fill=tk.BOTH, expand=True)
        
        shell_view = ShellListView(shell_frame)
        shell_view.create_widgets()
        
        # Load shells
        all_shells = shell_model.get_all_shells()
        shell_view.update_display(all_shells)
        
        print(f"🎉 Shell Pokedex Demo Started!")
        print(f"📊 Loaded {len(all_shells)} shells with images")
        print(f"💡 Click on any shell to see its 64x64 pixel image!")
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
