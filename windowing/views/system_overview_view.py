#!/usr/bin/env python3
"""
System Overview View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView


class SystemOverviewView(BaseView):
    """View for system overview"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.overview_text = None
        
    def create_widgets(self):
        """Create system overview widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.overview_text = tk.Text(self.parent, wrap=tk.WORD, state=tk.DISABLED)
        self.overview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                               padx=(10, 0), pady=10)
        
        overview_scroll = ttk.Scrollbar(self.parent, orient=tk.VERTICAL,
                                      command=self.overview_text.yview)
        overview_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S), 
                           padx=(0, 10), pady=10)
        self.overview_text.configure(yscrollcommand=overview_scroll.set)
        
        # Scrollbar column should not expand
        self.parent.columnconfigure(1, weight=0)
        
        return self.parent
    
    def update_display(self, overview_data):
        """Update system overview display"""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        
        overview = "Mathic System Overview\n" + "="*50 + "\n\n"
        
        # Module and loadout counts
        module_count = overview_data.get('module_count', 0)
        loadout_count = overview_data.get('loadout_count', 0)
        
        overview += f"Total Modules: {module_count}\n"
        overview += f"Total Loadouts: {loadout_count}\n\n"
        
        if module_count > 0:
            # Module type distribution
            type_counts = overview_data.get('type_counts', {})
            overview += "Module Distribution:\n"
            for module_type, count in sorted(type_counts.items()):
                overview += f"  {module_type}: {count}\n"
            
            # Enhancement statistics
            avg_level = overview_data.get('avg_level', 0)
            max_level = overview_data.get('max_level', 0)
            overview += f"\nEnhancement Stats:\n"
            overview += f"  Average Level: {avg_level:.1f}\n"
            overview += f"  Highest Level: {max_level}\n\n"
            
            # Loadout information
            loadout_info = overview_data.get('loadout_info', {})
            overview += "Loadouts:\n"
            for loadout_name, equipped_count in loadout_info.items():
                overview += f"  {loadout_name}: {equipped_count}/6 slots\n"
        else:
            overview += "No modules created yet.\n"
            overview += "Use the Module Editor to create your first module!\n"
        
        self.overview_text.insert(1.0, overview)
        self.overview_text.config(state=tk.DISABLED)
