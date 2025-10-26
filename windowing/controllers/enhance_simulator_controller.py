#!/usr/bin/env python3
"""
Enhance Simulator Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox
from .base_controller import BaseController


class EnhanceSimulatorController(BaseController):
    """Controller for enhance simulator"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
    
    def initialize(self):
        """Initialize enhance simulator controller"""
        self.refresh_enhance_modules()
    
    def refresh_enhance_modules(self):
        """Refresh the module list for enhance simulator"""
        try:
            modules = self.model.get_all_modules()
            self.view.update_display(modules)
            self.app_state.set_status(f"Loaded {len(modules)} modules for enhancement")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh modules: {e}")
    
    def on_enhance_module_select(self):
        """Handle module selection in enhance simulator"""
        module_id = self.view.get_selected_module_id()
        if not module_id:
            return
        
        try:
            module = self.model.get_module_by_id(module_id)
            if module:
                # Update current module display
                self.view.update_current_module_display(module, self.model.mathic_system.config)
                
                # Update probability display
                probabilities = self.model.calculate_substat_probabilities(module_id)
                self.view.update_probability_display(probabilities)
                
                # Update value analysis display
                value_data = self.model.calculate_module_value(module_id)
                self.view.update_value_analysis_display(value_data)
                
                self.app_state.set_status(f"Selected module {module_id} for enhancement")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load module details: {e}")
    
    def enhance_once(self):
        """Enhance the selected module once"""
        self._perform_enhancement(1)
    
    def enhance_five_times(self):
        """Enhance the selected module 5 times"""
        self._perform_enhancement(5)
    
    def enhance_to_max(self):
        """Enhance the selected module to maximum"""
        module_id = self.view.get_selected_module_id()
        if not module_id:
            messagebox.showwarning("Warning", "Please select a module")
            return
        
        module = self.model.get_module_by_id(module_id)
        if module:
            remaining_rolls = module.max_total_rolls - module.total_enhancement_rolls
            if remaining_rolls > 0:
                self._perform_enhancement(remaining_rolls)
            else:
                messagebox.showinfo("Info", "Module is already at maximum enhancement")
    
    def _perform_enhancement(self, times):
        """Perform enhancement multiple times and log results"""
        module_id = self.view.get_selected_module_id()
        if not module_id:
            messagebox.showwarning("Warning", "Please select a module")
            return
        
        module = self.model.get_module_by_id(module_id)
        if not module:
            messagebox.showerror("Error", "Module not found")
            return
        
        # Check if enhancement is possible
        if not module.can_be_enhanced():
            messagebox.showinfo("Info", "Module cannot be enhanced further")
            return
        
        # Log enhancement start
        self.view.log_enhancement(f"\n--- Starting {times} enhancement(s) for {module.module_type} ---")
        
        success_count = 0
        for i in range(times):
            if not module.can_be_enhanced():
                self.view.log_enhancement(f"Enhancement {i+1}: Module fully enhanced")
                break
            
            enhanced_stat = self.model.enhance_module_random(module_id)
            if enhanced_stat:
                success_count += 1
                if enhanced_stat.startswith("New substat:"):
                    self.view.log_enhancement(f"Enhancement {i+1}: {enhanced_stat}")
                else:
                    # Get the updated substat for logging
                    updated_module = self.model.get_module_by_id(module_id)
                    substat = None
                    for s in updated_module.substats:
                        if s.stat_name == enhanced_stat:
                            substat = s
                            break
                    
                    if substat:
                        self.view.log_enhancement(
                            f"Enhancement {i+1}: Enhanced {enhanced_stat} "
                            f"(Current: {int(substat.current_value)}, "
                            f"Rolls: {substat.rolls_used}/5)")
            else:
                self.view.log_enhancement(f"Enhancement {i+1}: Failed")
                break
        
        self.view.log_enhancement(f"Completed {success_count}/{times} enhancements")
        updated_module = self.model.get_module_by_id(module_id)
        self.view.log_enhancement(f"Module level: {updated_module.level} "
                                 f"(Rolls: {updated_module.total_enhancement_rolls}/{updated_module.max_total_rolls})")
        
        # Refresh displays
        self.on_enhance_module_select()
        self.app_state.set_status(f"Enhanced module {times} times, {success_count} successful")
