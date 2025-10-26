#!/usr/bin/env python3
"""
Loadout Manager Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox
from .base_controller import BaseController


class LoadoutManagerController(BaseController):
    """Controller for loadout manager"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
        
        # Slot type restrictions
        self.slot_restrictions = {
            1: ["mask"],
            2: ["transistor"], 
            3: ["wristwheel"],
            4: ["core"],
            5: ["core"],
            6: ["core"]
        }
    
    def initialize(self):
        """Initialize loadout manager controller"""
        self.refresh_loadout_list()
        self.refresh_slot_module_options()
    
    def refresh_loadout_list(self):
        """Refresh the loadout list"""
        try:
            loadouts = self.model.get_all_loadouts()
            self.view.update_display(loadouts)
            self.app_state.set_status(f"Loaded {len(loadouts)} loadouts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh loadouts: {e}")
    
    def refresh_slot_module_options(self):
        """Refresh module options for all slots with type restrictions"""
        try:
            modules = self.model.get_all_modules()
            self.view.update_slot_module_options(self.slot_restrictions, modules)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh slot options: {e}")
    
    def on_loadout_select(self):
        """Handle loadout selection"""
        loadout_name = self.view.get_selected_loadout()
        if not loadout_name:
            return
        
        try:
            loadout_modules = self.model.get_loadout_modules(loadout_name)
            modules = self.model.get_all_modules()
            
            # Update loadout display
            loadout = self.model.mathic_system.mathic_loadouts.get(loadout_name, {})
            self.view.update_loadout_display(loadout, modules)
            
            # Update stats summary
            self._update_loadout_stats(loadout_name)
            
            self.app_state.set_status(f"Selected loadout: {loadout_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load loadout: {e}")
    
    def on_slot_module_change(self, slot_id):
        """Handle slot module assignment"""
        loadout_name = self.view.get_selected_loadout()
        if not loadout_name:
            return
        
        selection = self.view.get_slot_selection(slot_id)
        
        try:
            if selection == "None":
                # Clear slot
                self.model.assign_module_to_loadout(loadout_name, slot_id, None)
                
                # Clear substats display
                for substat_label in self.view.slot_substats_labels[slot_id]:
                    substat_label.config(text="")
            else:
                # Assign module
                module_id = selection.split(":")[0]
                self.model.assign_module_to_loadout(loadout_name, slot_id, module_id)
                
                # Update substats display
                module = self.model.get_module_by_id(module_id)
                if module:
                    for i, substat_label in enumerate(self.view.slot_substats_labels[slot_id]):
                        if i < len(module.substats):
                            substat = module.substats[i]
                            text = f"{substat.stat_name}: +{int(substat.current_value)}"
                            substat_label.config(text=text)
                        else:
                            substat_label.config(text="")
            
            # Update stats summary
            self._update_loadout_stats(loadout_name)
            self.app_state.set_status(f"Updated slot {slot_id} in {loadout_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update slot: {e}")
    
    def new_loadout(self):
        """Create a new loadout"""
        from tkinter.simpledialog import askstring
        name = askstring("New Loadout", "Enter loadout name:")
        if name:
            if self.model.create_loadout(name):
                self.refresh_loadout_list()
                self.view.loadout_var.set(name)
                self.on_loadout_select()
                self.app_state.set_status(f"Created new loadout: {name}")
            else:
                messagebox.showwarning("Warning", "Loadout name already exists")
    
    def delete_loadout(self):
        """Delete selected loadout"""
        loadout_name = self.view.get_selected_loadout()
        if not loadout_name:
            return
        
        if messagebox.askyesno("Confirm", f"Delete loadout '{loadout_name}'?"):
            if self.model.delete_loadout(loadout_name):
                self.refresh_loadout_list()
                self.app_state.set_status(f"Deleted loadout: {loadout_name}")
            else:
                messagebox.showerror("Error", "Failed to delete loadout")
    
    def _update_loadout_stats(self, loadout_name):
        """Update loadout total stats display"""
        try:
            loadout_modules = self.model.get_loadout_modules(loadout_name)
            total_stats = {}
            
            # Calculate total stats
            for slot_id, module in loadout_modules.items():
                if module:
                    # Add main stat
                    if module.main_stat in total_stats:
                        total_stats[module.main_stat] += module.main_stat_value
                    else:
                        total_stats[module.main_stat] = module.main_stat_value
                    
                    # Add substats
                    for substat in module.substats:
                        if substat.stat_name:
                            if substat.stat_name in total_stats:
                                total_stats[substat.stat_name] += substat.current_value
                            else:
                                total_stats[substat.stat_name] = substat.current_value
            
            # Update display
            self.view.update_stats_summary(total_stats)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate stats: {e}")
