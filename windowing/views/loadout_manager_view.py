#!/usr/bin/env python3
"""
Loadout Manager View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView


class LoadoutManagerView(BaseView):
    """View for loadout manager"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.loadout_var = tk.StringVar()
        
        # UI elements
        self.loadout_combo = None
        self.slot_frames = {}
        self.slot_combos = {}
        self.slot_vars = {}
        self.slot_main_stat_labels = {}
        self.slot_substats_labels = {}
        self.stats_summary_text = None
        
    def create_widgets(self):
        """Create loadout manager widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=2)  # Left side for slots
        self.parent.columnconfigure(1, weight=1)  # Right side for stats
        self.parent.rowconfigure(1, weight=1)
        
        # Top frame - Loadout selection
        self._create_loadout_selection()
        
        # Loadout slots frame (left side)
        self._create_equipment_slots()
        
        # Stats summary frame (right side)
        self._create_stats_summary()
        
        return self.parent
    
    def _create_loadout_selection(self):
        """Create loadout selection controls"""
        top_frame = ttk.Frame(self.parent)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
        
        ttk.Label(top_frame, text="Loadout:").grid(row=0, column=0, padx=(0, 5))
        self.loadout_combo = ttk.Combobox(top_frame, textvariable=self.loadout_var,
                                        state="readonly", width=20)
        self.loadout_combo.grid(row=0, column=1, padx=(0, 10))
        self.loadout_combo.bind('<<ComboboxSelected>>', 
                               lambda e: self.controller.on_loadout_select() if self.controller else None)
        
        ttk.Button(top_frame, text="New Loadout", 
                  command=lambda: self.controller.new_loadout() if self.controller else None).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(top_frame, text="Delete Loadout", 
                  command=lambda: self.controller.delete_loadout() if self.controller else None).grid(row=0, column=3)
    
    def _create_equipment_slots(self):
        """Create equipment slots display"""
        slots_frame = ttk.LabelFrame(self.parent, text="Equipment Slots", padding="10")
        slots_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=5)
        
        # Create 6 slots in 2x3 layout
        slot_positions = [
            (0, 0), (1, 0), (2, 0),  # Column 1: slots 1, 2, 3
            (0, 1), (1, 1), (2, 1)   # Column 2: slots 4, 5, 6
        ]
        
        for i in range(6):
            slot_id = i + 1
            row, col = slot_positions[i]
            
            slot_frame = ttk.LabelFrame(slots_frame, text=f"Slot {slot_id}", padding="10")
            slot_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=5, pady=5)
            
            self.slot_frames[slot_id] = slot_frame
            
            # Module selection
            self.slot_vars[slot_id] = tk.StringVar()
            self.slot_combos[slot_id] = ttk.Combobox(slot_frame, 
                                                   textvariable=self.slot_vars[slot_id],
                                                   state="readonly", width=15)
            self.slot_combos[slot_id].grid(row=0, column=0, pady=(0, 5))
            self.slot_combos[slot_id].bind('<<ComboboxSelected>>', 
                                         lambda e, s=slot_id: self.controller.on_slot_module_change(s) if self.controller else None)
            
            # Main stat display
            main_stat_frame = ttk.Frame(slot_frame)
            main_stat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
            
            ttk.Label(main_stat_frame, text="Main Stat:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
            self.slot_main_stat_labels[slot_id] = ttk.Label(main_stat_frame, text="", 
                                                           font=("Arial", 10, "bold"), foreground="darkred")
            self.slot_main_stat_labels[slot_id].grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
            
            # Substats display area
            substats_frame = ttk.Frame(slot_frame)
            substats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            
            # Substats header
            ttk.Label(substats_frame, text="Substats:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
            
            # Create 4 labels for substats in vertical layout
            self.slot_substats_labels[slot_id] = []
            for j in range(4):
                substat_label = ttk.Label(substats_frame, text="", font=("Arial", 9), foreground="darkblue")
                substat_label.grid(row=j+1, column=0, sticky=tk.W, pady=1)
                self.slot_substats_labels[slot_id].append(substat_label)
        
        # Configure grid weights for 2x3 layout
        slots_frame.columnconfigure(0, weight=1)
        slots_frame.columnconfigure(1, weight=1)
        slots_frame.rowconfigure(0, weight=1)
        slots_frame.rowconfigure(1, weight=1)
        slots_frame.rowconfigure(2, weight=1)
    
    def _create_stats_summary(self):
        """Create stats summary display"""
        stats_frame = ttk.LabelFrame(self.parent, text="Total Stats", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=5)
        
        self.stats_summary_text = tk.Text(stats_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
    
    def update_display(self, data):
        """Update loadout list"""
        loadouts = data if isinstance(data, list) else list(data.keys())
        self.loadout_combo.configure(values=loadouts)
        if loadouts and not self.loadout_var.get():
            self.loadout_var.set(loadouts[0])
            if self.controller:
                self.controller.on_loadout_select()
    
    def update_slot_module_options(self, slot_restrictions, modules):
        """Update module options for all slots with type restrictions"""
        for slot_id in range(1, 7):
            allowed_types = slot_restrictions.get(slot_id, [])
            
            # Filter modules by allowed types for this slot
            slot_module_options = ["None"]
            for mid, mod in modules.items():
                if mod.module_type in allowed_types:
                    slot_module_options.append(f"{mid}: {mod.module_type} - {mod.main_stat}")
            
            self.slot_combos[slot_id].configure(values=slot_module_options)
    
    def update_loadout_display(self, loadout, modules):
        """Update loadout slots display"""
        for slot_id in range(1, 7):
            module_id = loadout.get(slot_id)
            if module_id and module_id in modules:
                module = modules[module_id]
                self.slot_vars[slot_id].set(f"{module_id}: {module.module_type} - {module.main_stat}")
                
                # Update main stat display
                main_stat_text = f"{module.main_stat}: +{int(module.main_stat_value)}"
                self.slot_main_stat_labels[slot_id].config(text=main_stat_text)
                
                # Update substats display
                for i, substat_label in enumerate(self.slot_substats_labels[slot_id]):
                    if i < len(module.substats):
                        substat = module.substats[i]
                        if substat.stat_name:  # Only show non-empty substats
                            text = f"{substat.stat_name}: +{int(substat.current_value)}"
                            substat_label.config(text=text)
                        else:
                            substat_label.config(text="")
                    else:
                        substat_label.config(text="")
            else:
                self.slot_vars[slot_id].set("None")
                # Clear main stat display
                self.slot_main_stat_labels[slot_id].config(text="")
                # Clear substats display
                for substat_label in self.slot_substats_labels[slot_id]:
                    substat_label.config(text="")
    
    def update_stats_summary(self, total_stats):
        """Update total stats display"""
        self.stats_summary_text.config(state=tk.NORMAL)
        self.stats_summary_text.delete(1.0, tk.END)
        
        if total_stats:
            stats_text = "Total Stats:\n" + "="*30 + "\n"
            
            # Separate flat and percentage stats
            flat_stats = ["ATK", "HP", "DEF"]
            percent_stats = ["ATK%", "HP%", "DEF%", "CRIT Rate", "CRIT DMG", 
                           "Effect ACC", "Effect RES", "SPD"]
            
            stats_text += "\nFlat Stats:\n"
            for stat in flat_stats:
                if stat in total_stats:
                    stats_text += f"  {stat}: +{int(total_stats[stat])}\n"
            
            stats_text += "\nPercentage Stats:\n"
            for stat in percent_stats:
                if stat in total_stats:
                    stats_text += f"  {stat}: +{total_stats[stat]:.1f}%\n"
        else:
            stats_text = "No modules equipped"
        
        self.stats_summary_text.insert(1.0, stats_text)
        self.stats_summary_text.config(state=tk.DISABLED)
    
    def get_selected_loadout(self):
        """Get currently selected loadout name"""
        return self.loadout_var.get()
    
    def get_slot_selection(self, slot_id):
        """Get module selection for specific slot"""
        return self.slot_vars[slot_id].get()
