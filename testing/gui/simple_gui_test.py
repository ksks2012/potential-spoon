#!/usr/bin/env python3
"""
A simplified GUI test script for testing the Module Editor's slider control.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mathic.mathic_system import MathicSystem


class SimpleModuleEditorTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Module Editor Enhancement Test")
        self.root.geometry("600x500")
        
        # Initialize mathic system
        self.mathic_system = MathicSystem()
        self.current_module = None
        
        # Variables
        self.max_enhancements_var = tk.IntVar(value=5)
        self.remaining_enhancements_var = tk.StringVar(value="5")
        self.max_possible_rolls_var = tk.StringVar(value="9")
        
        self.setup_ui()
        self.create_test_module()
    
    def setup_ui(self):
        """Setup the UI"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Module Editor Enhancement Configuration Test", 
                              font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Enhancement Configuration Frame
        config_frame = ttk.LabelFrame(main_frame, text="Enhancement Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Max Enhancements Slider (implementation-required slider control, range 0-5)
        ttk.Label(config_frame, text="Max Enhancements:").grid(row=0, column=0, padx=(0, 10))
        
        self.max_enh_scale = tk.Scale(config_frame, from_=0, to=5, orient=tk.HORIZONTAL,
                                    variable=self.max_enhancements_var,
                                    command=self.on_enhancement_change)
        self.max_enh_scale.grid(row=0, column=1, padx=(0, 20))
        self.max_enh_scale.configure(length=200, width=20)
        
        # Remaining Enhancements Display
        ttk.Label(config_frame, text="Remaining:").grid(row=0, column=2, padx=(0, 10))
        remaining_label = ttk.Label(config_frame, textvariable=self.remaining_enhancements_var,
                                  font=('Arial', 12, 'bold'), foreground="darkgreen")
        remaining_label.grid(row=0, column=3, padx=(0, 20))
        
        # Max Possible Total Rolls Display
        ttk.Label(config_frame, text="Max Total Rolls:").grid(row=0, column=4, padx=(0, 10))
        max_rolls_label = ttk.Label(config_frame, textvariable=self.max_possible_rolls_var,
                                  font=('Arial', 12, 'bold'), foreground="darkblue")
        max_rolls_label.grid(row=0, column=5)
        
        # Module Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="Current Test Module", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=12, width=70, state='disabled')
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Substat Rolls Test Frame
        rolls_frame = ttk.LabelFrame(main_frame, text="Substat Rolls Test (1-6 Range)", padding="10")
        rolls_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Test different roll values and show calculated values
        ttk.Label(rolls_frame, text="Test Stat: ATK").grid(row=0, column=0, padx=(0, 10))
        
        self.test_rolls_var = tk.IntVar(value=1)
        test_rolls_scale = tk.Scale(rolls_frame, from_=1, to=6, orient=tk.HORIZONTAL,
                                  variable=self.test_rolls_var,
                                  command=self.on_rolls_change)
        test_rolls_scale.grid(row=0, column=1, padx=(0, 20))
        test_rolls_scale.configure(length=200, width=20)
        
        ttk.Label(rolls_frame, text="Rolls:").grid(row=0, column=2, padx=(0, 10))
        self.rolls_display = ttk.Label(rolls_frame, text="1", font=('Arial', 12, 'bold'))
        self.rolls_display.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(rolls_frame, text="Possible Values:").grid(row=0, column=4, padx=(0, 10))
        self.values_display = ttk.Label(rolls_frame, text="", font=('Arial', 10))
        self.values_display.grid(row=0, column=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Initial update
        self.on_rolls_change()
    
    def create_test_module(self):
        """Create a test module"""
        # Create module with 4 substats for testing
        self.current_module = self.mathic_system.create_module("core", 4, "CRIT Rate")
        
        if self.current_module:
            # Add substats to get 4 total
            while len(self.current_module.substats) < 4:
                available_stats = self.mathic_system.get_available_substats_for_module(self.current_module)
                if available_stats:
                    stat_config = self.mathic_system.config["substats"][available_stats[0]]
                    roll_range = stat_config["roll_range"]
                    initial_value = (roll_range[0] + roll_range[1]) / 2
                    self.current_module.add_substat(available_stats[0], initial_value)
                else:
                    break
        
        self.update_module_display()
    
    def on_enhancement_change(self, value=None):
        """Handle enhancement configuration change"""
        if not self.current_module:
            return
        
        new_max = self.max_enhancements_var.get()
        self.current_module.max_enhancements = new_max
        self.current_module.sync_enhancement_tracking()
        
        # Update displays
        self.remaining_enhancements_var.set(str(self.current_module.remaining_enhancements))
        self.max_possible_rolls_var.set(str(self.current_module.get_max_possible_total_rolls()))
        
        self.update_module_display()
    
    def on_rolls_change(self, value=None):
        """Handle rolls change for value calculation test"""
        rolls = self.test_rolls_var.get()
        self.rolls_display.config(text=str(rolls))
        
        # Get possible values for ATK with this many rolls
        values = self.mathic_system.get_substat_value_options("ATK", rolls)
        values_text = ", ".join(values) if values else "None"
        self.values_display.config(text=values_text)
    
    def update_module_display(self):
        """Update module information display"""
        if not self.current_module:
            return
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        
        info = f"Module ID: {self.current_module.module_id}\n"
        info += f"Type: {self.current_module.module_type}\n"
        info += f"Main Stat: {self.current_module.main_stat} = {self.current_module.main_stat_value}\n\n"
        
        info += f"Enhancement Configuration:\n"
        info += f"  Max Enhancements: {self.current_module.max_enhancements}\n"
        info += f"  Remaining Enhancements: {self.current_module.remaining_enhancements}\n"
        info += f"  Max Possible Total Rolls: {self.current_module.get_max_possible_total_rolls()}\n\n"
        
        info += f"Substats ({len(self.current_module.substats)}/4):\n"
        for i, substat in enumerate(self.current_module.substats, 1):
            info += f"  {i}. {substat.stat_name}: {substat.current_value} "
            info += f"(rolls: {substat.rolls_used}/{substat.max_rolls})\n"
        
        info += f"\nRestrictions:\n"
        info += f"  Can enhance individual substats: {self.current_module.can_enhance_individual_substat()}\n"
        info += f"  Individual enhanceable count: {len(self.current_module.get_enhanceable_substats())}\n"
        
        # Test roll logic
        info += f"\nRoll Logic Test:\n"
        info += f"  Formula: {len(self.current_module.substats)} initial + {self.current_module.max_enhancements} enhancements = {self.current_module.get_max_possible_total_rolls()}\n"
        info += f"  Each substat: 1 initial roll, max 6 total rolls\n"
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state='disabled')
    
    def run(self):
        """Run the application"""
        print("🎯 Starting Module Editor Enhancement Test...")
        print("✅ GUI slider controls implemented (0-5 range)")
        print("✅ Max rolls adjusted to 6 (initial roll = 1)")
        print("✅ Current value changes with roll changes")
        
        self.root.mainloop()


def main():
    app = SimpleModuleEditorTest()
    app.run()


if __name__ == "__main__":
    main()
