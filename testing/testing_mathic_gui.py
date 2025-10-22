#!/usr/bin/env python3
"""
GUI Integration Test for Enhancement Probabilities Display
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from mathic.mathic_system import MathicSystem
from windowing.views import EnhanceSimulatorView

class TestGUIIntegration:
    """Test class for GUI integration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhancement Probabilities Display Test")
        self.root.geometry("800x600")
        
        # Initialize MathicSystem
        config_path = os.path.join(project_root, "mathic", "mathic_config.json")
        self.mathic_system = MathicSystem(config_path)
        
        # Create test modules
        self.create_test_modules()
        
        # Setup GUI
        self.setup_gui()
    
    def create_test_modules(self):
        """Create test modules with different enhancement states"""
        # Module 1: Fresh module (0/5 total rolls)
        self.module1 = self.mathic_system.create_module('core', 1, 'ATK%')
        self.mathic_system.generate_random_substats(self.module1, 4)
        
        # Module 2: Partially enhanced (3/5 total rolls)
        self.module2 = self.mathic_system.create_module('core', 2, 'CRIT Rate')
        self.mathic_system.generate_random_substats(self.module2, 4)
        self.module2.total_enhancement_rolls = 3
        
        # Module 3: At limit (5/5 total rolls)
        self.module3 = self.mathic_system.create_module('core', 3, 'CRIT DMG')
        self.mathic_system.generate_random_substats(self.module3, 4)
        self.module3.total_enhancement_rolls = 5
        
        # Module 4: Some substats maxed
        self.module4 = self.mathic_system.create_module('core', 4, 'HP%')
        self.mathic_system.generate_random_substats(self.module4, 4)
        self.module4.substats[0].rolls_used = 5  # Max first substat
        self.module4.substats[1].rolls_used = 5  # Max second substat
        self.module4.total_enhancement_rolls = 2
    
    def setup_gui(self):
        """Setup GUI components"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhancement Probabilities Display Test", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Module selection
        ttk.Label(main_frame, text="Select Module:").grid(row=1, column=0, sticky=tk.W)
        
        self.module_var = tk.StringVar()
        module_combo = ttk.Combobox(main_frame, textvariable=self.module_var, state="readonly", width=40)
        module_combo['values'] = [
            f"Module 1 (Fresh): {self.module1.module_id} - 0/5 rolls",
            f"Module 2 (Partial): {self.module2.module_id} - 3/5 rolls", 
            f"Module 3 (Full): {self.module3.module_id} - 5/5 rolls",
            f"Module 4 (Mixed): {self.module4.module_id} - 2/5 rolls, 2 maxed substats"
        ]
        module_combo.grid(row=1, column=1, pady=10, padx=(10, 0))
        module_combo.bind('<<ComboboxSelected>>', self.on_module_select)
        
        # Enhancement Probabilities display
        prob_frame = ttk.LabelFrame(main_frame, text="Enhancement Probabilities", padding="10")
        prob_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.probability_tree = ttk.Treeview(prob_frame, columns=('Probability',), show='tree headings', height=8)
        self.probability_tree.heading('#0', text='Substat')
        self.probability_tree.heading('Probability', text='Probability (%)')
        self.probability_tree.column('#0', width=200)
        self.probability_tree.column('Probability', width=120)
        self.probability_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Module details display
        details_frame = ttk.LabelFrame(main_frame, text="Module Details", padding="10")
        details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.details_text = tk.Text(details_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        details_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Select a module to view its Enhancement Probabilities.\n" +
                                    "Notice how probabilities change based on total_enhancement_rolls.",
                               justify=tk.CENTER)
        instructions.grid(row=4, column=0, columnspan=2, pady=10)
    
    def on_module_select(self, event=None):
        """Handle module selection"""
        selection = self.module_var.get()
        if not selection:
            return
        
        # Determine which module was selected
        module = None
        if "Module 1" in selection:
            module = self.module1
        elif "Module 2" in selection:
            module = self.module2
        elif "Module 3" in selection:
            module = self.module3
        elif "Module 4" in selection:
            module = self.module4
        
        if module:
            self.update_displays(module)
    
    def update_displays(self, module):
        """Update probability and details displays"""
        # Update probability display
        self.update_probability_display(module)
        
        # Update details display
        self.update_details_display(module)
    
    def update_probability_display(self, module):
        """Update probability display (same as GUI view)"""
        # Clear existing items
        for item in self.probability_tree.get_children():
            self.probability_tree.delete(item)
        
        # Calculate probabilities
        probabilities = self.mathic_system.calculate_substat_probabilities(module)
        
        if probabilities:
            for stat_name, prob in probabilities.items():
                self.probability_tree.insert('', tk.END, text=stat_name, 
                                            values=(f"{prob*100:.1f}%",))
        else:
            self.probability_tree.insert('', tk.END, text="No enhancements possible", 
                                        values=("0.0%",))
    
    def update_details_display(self, module):
        """Update module details display"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details_text = f"MODULE: {module.module_id}\n"
        details_text += f"Type: {module.module_type}\n"
        details_text += f"Main Stat: {module.main_stat} = {module.main_stat_value}\n"
        details_text += f"Level: {module.level}\n"
        details_text += f"Total Enhancement Rolls: {module.total_enhancement_rolls}/{module.max_total_rolls}\n"
        details_text += f"Can be enhanced: {module.can_be_enhanced()}\n\n"
        
        details_text += "SUBSTATS:\n"
        if module.substats:
            for i, substat in enumerate(module.substats, 1):
                max_val = self.mathic_system.config["substats"][substat.stat_name]["max_value"]
                efficiency = substat.get_efficiency_percentage(max_val)
                can_enhance = substat.can_enhance()
                details_text += f"{i}. {substat.stat_name}: {int(substat.current_value)} "
                details_text += f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}% eff, "
                details_text += f"{'Can enhance' if can_enhance else 'MAXED'})\n"
        else:
            details_text += "No substats yet\n"
        
        # Add enhanceable substats info
        enhanceable = module.get_enhanceable_substats()
        details_text += f"\nEnhanceable Substats: {len(enhanceable)}\n"
        for substat in enhanceable:
            details_text += f"  - {substat.stat_name}\n"
        
        self.details_text.insert(1.0, details_text)
        self.details_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the test GUI"""
        print("GUI Integration Test for Enhancement Probabilities")
        print("=" * 60)
        print("✅ Test modules created:")
        print(f"   Module 1: Fresh (0/5 rolls)")
        print(f"   Module 2: Partial (3/5 rolls)")
        print(f"   Module 3: Full (5/5 rolls)")  
        print(f"   Module 4: Mixed (2/5 rolls, some substats maxed)")
        print("\n🎯 Key points to verify:")
        print("   - Module 1: Shows equal probabilities for all substats")
        print("   - Module 2: Shows equal probabilities (still can enhance)")
        print("   - Module 3: Shows 'No enhancement possible' (total rolls maxed)")
        print("   - Module 4: Shows only non-maxed substats in probabilities")
        print(f"\n🚀 Starting GUI test...")
        
        self.root.mainloop()

def main():
    """Run the GUI integration test"""
    try:
        test = TestGUIIntegration()
        test.run()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
