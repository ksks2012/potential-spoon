#!/usr/bin/env python3
"""
Enhance Simulator View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView


class EnhanceSimulatorView(BaseView):
    """View for enhance simulator"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.enhance_module_var = tk.StringVar()
        
        # UI elements
        self.enhance_module_combo = None
        self.current_module_text = None
        self.enhancement_log = None
        self.probability_tree = None
        self.value_analysis_text = None
        
    def create_widgets(self):
        """Create enhance simulator widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(1, weight=1)
        
        # Top frame - Module selection
        top_frame = ttk.Frame(self.parent)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(top_frame, text="Select Module for Enhancement:").grid(row=0, column=0, padx=(0, 10))
        self.enhance_module_combo = ttk.Combobox(top_frame, textvariable=self.enhance_module_var,
                                               state="readonly", width=30)
        self.enhance_module_combo.grid(row=0, column=1, padx=(0, 10))
        self.enhance_module_combo.bind('<<ComboboxSelected>>', 
                                     lambda e: self.controller.on_enhance_module_select() if self.controller else None)
        
        ttk.Button(top_frame, text="Refresh Modules", 
                  command=lambda: self.controller.refresh_enhance_modules() if self.controller else None).grid(row=0, column=2)
        
        # Left panel - Enhancement controls
        self._create_enhancement_controls()
        
        # Right panel - Statistics and analysis
        self._create_statistics_panel()
        
        return self.parent
    
    def _create_enhancement_controls(self):
        """Create enhancement controls panel"""
        left_panel = ttk.LabelFrame(self.parent, text="Enhancement Controls", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Current module info
        current_info_frame = ttk.LabelFrame(left_panel, text="Current Module", padding="10")
        current_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.current_module_text = tk.Text(current_info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.current_module_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Enhancement buttons
        enhance_buttons_frame = ttk.Frame(left_panel)
        enhance_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(enhance_buttons_frame, text="Enhance Once", 
                  command=lambda: self.controller.enhance_once() if self.controller else None).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance 5 Times", 
                  command=lambda: self.controller.enhance_five_times() if self.controller else None).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance to Max", 
                  command=lambda: self.controller.enhance_to_max() if self.controller else None).grid(row=0, column=2)
        
        # Enhancement log
        log_frame = ttk.LabelFrame(left_panel, text="Enhancement Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.enhancement_log = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.enhancement_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.enhancement_log.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.enhancement_log.configure(yscrollcommand=log_scroll.set)
        
        # Configure grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        current_info_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _create_statistics_panel(self):
        """Create statistics and analysis panel"""
        right_panel = ttk.LabelFrame(self.parent, text="Statistics & Analysis", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Substat probabilities
        prob_frame = ttk.LabelFrame(right_panel, text="Enhancement Probabilities", padding="10")
        prob_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.probability_tree = ttk.Treeview(prob_frame, columns=('Probability',), show='tree headings', height=8)
        self.probability_tree.heading('#0', text='Substat')
        self.probability_tree.heading('Probability', text='Probability (%)')
        self.probability_tree.column('#0', width=150)
        self.probability_tree.column('Probability', width=100)
        self.probability_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        prob_scroll = ttk.Scrollbar(prob_frame, orient=tk.VERTICAL, command=self.probability_tree.yview)
        prob_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.probability_tree.configure(yscrollcommand=prob_scroll.set)
        
        # Module value analysis
        value_frame = ttk.LabelFrame(right_panel, text="Module Value Analysis", padding="10")
        value_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.value_analysis_text = tk.Text(value_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
        self.value_analysis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        value_scroll = ttk.Scrollbar(value_frame, orient=tk.VERTICAL, command=self.value_analysis_text.yview)
        value_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.value_analysis_text.configure(yscrollcommand=value_scroll.set)
        
        # Configure grid weights
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        prob_frame.columnconfigure(0, weight=1)
        value_frame.columnconfigure(0, weight=1)
        value_frame.rowconfigure(0, weight=1)
    
    def update_display(self, data):
        """Update module list for enhance simulator"""
        module_options = []
        for module_id, module in data.items():
            display_text = f"{module_id}: {module.module_type} - {module.main_stat}"
            module_options.append(display_text)
        
        self.enhance_module_combo.configure(values=module_options)
        if module_options and not self.enhance_module_var.get():
            self.enhance_module_var.set(module_options[0])
            if self.controller:
                self.controller.on_enhance_module_select()
    
    def update_current_module_display(self, module, config):
        """Update current module information display"""
        self.current_module_text.config(state=tk.NORMAL)
        self.current_module_text.delete(1.0, tk.END)
        
        # Sync enhancement tracking before display to ensure accuracy
        module.sync_enhancement_tracking()
        
        info_text = f"Module: {module.module_type}\n"
        info_text += f"Main Stat: {module.main_stat} ({int(module.main_stat_value)})\n"
        info_text += f"Level: {module.level} (Used: {module.total_enhancement_rolls} / Remaining: {module.remaining_enhancements})\n"
        info_text += f"Substats: {len(module.substats)}/4\n"
        
        if module.substats:
            info_text += "Current Substats:\n"
            for i, substat in enumerate(module.substats, 1):
                max_val = config["substats"][substat.stat_name]["max_value"]
                efficiency = substat.get_efficiency_percentage(max_val)
                info_text += f"{i}. {substat.stat_name}: {int(substat.current_value)} "
                info_text += f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}%)\n"
        else:
            info_text += "No substats yet\n"
        
        self.current_module_text.insert(1.0, info_text)
        self.current_module_text.config(state=tk.DISABLED)
    
    def update_probability_display(self, probabilities):
        """Update probability display for next enhancement"""
        # Clear existing items
        for item in self.probability_tree.get_children():
            self.probability_tree.delete(item)
        
        if probabilities:
            for stat_name, prob in probabilities.items():
                self.probability_tree.insert('', tk.END, text=stat_name, 
                                            values=(f"{prob*100:.1f}%,"))
        else:
            self.probability_tree.insert('', tk.END, text="No enhancements possible", 
                                        values=("0.0%,"))
    
    def update_value_analysis_display(self, value_data):
        """Update module value analysis display with categorized scoring"""
        self.value_analysis_text.config(state=tk.NORMAL)
        self.value_analysis_text.delete(1.0, tk.END)
        
        analysis_text = "MODULE VALUE ANALYSIS\n"
        analysis_text += "="*30 + "\n"
        
        # Overall scores
        analysis_text += f"Total Value Score: {value_data['total_value']:.2f}\n"
        analysis_text += f"Overall Efficiency: {value_data['efficiency']:.1f}%\n"
        analysis_text += f"Roll Efficiency: {value_data['roll_efficiency']:.1f}%\n"
        
        # Category scores
        analysis_text += "CATEGORY SCORES\n"
        analysis_text += "-" * 20 + "\n"
        analysis_text += f"Defense Score:  {value_data.get('defense_score', 0):.2f}\n"
        analysis_text += f"Support Score:  {value_data.get('support_score', 0):.2f}\n"
        analysis_text += f"Offense Score:  {value_data.get('offense_score', 0):.2f}\n"
        
        # Determine primary category
        scores = {
            'Defense': value_data.get('defense_score', 0),
            'Support': value_data.get('support_score', 0),
            'Offense': value_data.get('offense_score', 0)
        }
        primary_category = max(scores, key=scores.get) if max(scores.values()) > 0 else "General"
        analysis_text += f"Primary Focus: {primary_category}\n"
        
        if value_data.get('details'):
            analysis_text += "SUBSTAT BREAKDOWN\n"
            analysis_text += "-" * 20 + "\n"
            
            # Group substats by category for better display
            categories = {"defense": [], "support": [], "offense": [], "general": []}
            
            for stat_name, details in value_data['details'].items():
                category = details.get('category_type', 'general')
                categories[category].append((stat_name, details))
            
            # Display each category
            category_names = {"defense": "Defense Stats", "support": "Support Stats", 
                            "offense": "Offense Stats", "general": "Other Stats"}
            
            for category, stats in categories.items():
                if stats:
                    analysis_text += f"\n{category_names[category]}:\n"
                    for stat_name, details in stats:
                        analysis_text += f"  {stat_name}:\n"
                        analysis_text += f"    Value: {int(details['current_value'])}\n"
                        analysis_text += f"    Efficiency: {details['efficiency']:.1f}%\n"
                        analysis_text += f"    Rolls: {details['rolls_used']}/5\n"
                        analysis_text += f"    Score: {details['substat_value']:.2f}\n"
                        analysis_text += f"    Weight: {details['category_weight']:.1f}x\n"
        
        self.value_analysis_text.insert(1.0, analysis_text)
        self.value_analysis_text.config(state=tk.DISABLED)
    
    def log_enhancement(self, message):
        """Add message to enhancement log"""
        self.enhancement_log.config(state=tk.NORMAL)
        self.enhancement_log.insert(tk.END, message + "\n")
        self.enhancement_log.config(state=tk.DISABLED)
        self.enhancement_log.see(tk.END)
    
    def get_selected_module_id(self):
        """Get currently selected module ID"""
        selection = self.enhance_module_var.get()
        if selection:
            return selection.split(":")[0]
        return None
