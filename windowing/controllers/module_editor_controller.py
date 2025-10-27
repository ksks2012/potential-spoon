#!/usr/bin/env python3
"""
Module Editor Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox
from .base_controller import BaseController


class ModuleEditorController(BaseController):
    """Controller for module editing"""
    
    def __init__(self, model, view, app_state, app_controller=None):
        super().__init__(model, view)
        self.app_state = app_state
        self.app_controller = app_controller
    
    def initialize(self):
        """Initialize module editor controller"""
        self.model.create_sample_modules()
        self.refresh_module_list()
        self.on_module_type_change()
    
    def refresh_module_list(self):
        """Refresh the module list"""
        modules = self.model.get_all_modules()
        self.view.update_display(modules)
    
    def on_module_select(self):
        """Handle module selection"""
        selected_index = self.view.get_selected_module_index()
        if selected_index is not None:
            module_ids = list(self.model.get_all_modules().keys())
            if selected_index < len(module_ids):
                module_id = module_ids[selected_index]
                module = self.model.get_module_by_id(module_id)
                self.view.current_selected_module_id = module_id
                
                # Set initialization flag to prevent roll change validation during module loading
                self.view.initializing_module = True
                
                try:
                    self.view.update_module_details(module)
                    
                    # Update enhancement configuration display
                    if hasattr(module, 'max_enhancements'):
                        self.view.max_enhancements_var.set(str(module.max_enhancements))
                    else:
                        module.max_enhancements = 5  # Set default if not present
                        self.view.max_enhancements_var.set("5")
                    
                    self.view.update_remaining_enhancements_display(module.remaining_enhancements)
                    
                    self.app_state.set_current_module(module_id)
                finally:
                    # Always clear the initialization flag
                    self.view.initializing_module = False
    
    def on_module_type_change(self, preserve_current_values=False):
        """Handle module type change"""
        form_data = self.view.get_module_form_data()
        module_type = form_data['module_type']
        current_main_stat = form_data['main_stat']
        
        # Update main stat options
        main_stat_options = self.model.get_available_main_stats(module_type)
        self.view.update_main_stat_options(main_stat_options)
        
        # Only set default if not preserving current values or current value is invalid
        if not preserve_current_values or current_main_stat not in main_stat_options:
            if main_stat_options:
                self.view.main_stat_var.set(main_stat_options[0])
                self.on_main_stat_change()
        else:
            # If preserving and current value is valid, trigger change to update dependent fields
            self.on_main_stat_change()
        
        # Update matrix options based on module type
        self.update_matrix_options()
        
        # Update substat options
        self.update_substat_options()
    
    def on_main_stat_change(self):
        """Handle main stat change - auto-fill the value"""
        form_data = self.view.get_module_form_data()
        module_type = form_data['module_type']
        main_stat = form_data['main_stat']
        
        max_value = self.model.get_max_main_stat_value(module_type, main_stat)
        if max_value > 0:
            self.view.main_stat_value_var.set(str(int(max_value)))
        
        # Update substat options to exclude main stat
        self.update_substat_options()
    
    def update_substat_options(self):
        """Update substat combo options based on main stat, module type, and existing selections"""
        form_data = self.view.get_module_form_data()
        main_stat = form_data['main_stat']
        module_type = form_data['module_type']
        substats_data = form_data.get('substats_data', [])
        
        # Get currently selected substats (excluding empty ones)
        existing_substats = []
        for data in substats_data:
            stat_name = data.get('stat_name')
            if stat_name and stat_name != "":
                existing_substats.append(stat_name)
        
        # Get base available stats excluding main stat
        available_stats = self.model.get_available_substats(
            exclude_main_stat=main_stat, 
            module_type=module_type
        )
        
        # Update each substat combo with filtered options
        self.view.update_substat_options_individually(available_stats, existing_substats)
    
    def update_matrix_options(self):
        """Update matrix options based on module type"""
        form_data = self.view.get_module_form_data()
        module_type = form_data['module_type']
        
        # Get available matrices for this module type
        available_matrices = self.model.get_available_matrices_for_module(module_type)
        
        # Add empty option for no matrix
        matrix_options = [""] + available_matrices
        self.view.update_matrix_options(matrix_options)
    
    def on_matrix_change(self):
        """Handle matrix selection change"""
        # This can be extended if needed for validation or other logic
        pass
    
    def on_matrix_count_change(self):
        """Handle matrix count change"""
        try:
            matrix_info = self.view.get_matrix_info()
            count = matrix_info['matrix_count']
            
            # Validate count range
            if count < 1:
                self.view.matrix_count_var.set("1")
            elif count > 3:
                self.view.matrix_count_var.set("3")
        except ValueError:
            self.view.matrix_count_var.set("3")
    
    def clear_matrix(self):
        """Clear matrix selection"""
        self.view.matrix_var.set("")
        self.view.matrix_count_var.set("3")
    
    def on_substat_type_change(self, substat_index):
        """Handle substat type change - update value options and total rolls"""
        # Clear value when changing substat type
        if hasattr(self.view, 'substat_controls') and 1 <= substat_index <= 4:
            _, _, _, _, value_var, _ = self.view.substat_controls[substat_index - 1]
            value_var.set("")
        
        # Update substat options for all combos to reflect new selections
        self.update_substat_options()
        
        self.update_substat_value_options(substat_index)
        self.view.update_total_rolls_display()
    
    def on_substat_rolls_change(self, substat_index):
        """Handle substat rolls change - update value options and validate restrictions"""
        # Prevent infinite loops during adjustment or messagebox display
        if getattr(self.view, 'adjusting_rolls', False):
            return
        
        # Skip validation during module selection/initialization
        if getattr(self.view, 'initializing_module', False):
            self.update_substat_value_options(substat_index)
            self.view.update_total_rolls_display()
            return
        
        # Final protection: prevent excessive reentrancy depth
        if getattr(self.view, 'rolls_change_depth', 0) > 0:
            return
        
        # Set reentrancy counter
        self.view.rolls_change_depth = getattr(self.view, 'rolls_change_depth', 0) + 1
        
        try:
            # Get current form data
            form_data = self.view.get_module_form_data()
            substats_data = form_data['substats_data']
            
            # Count valid substats (non-empty stat names)
            valid_substats_count = sum(1 for data in substats_data if data.get('stat_name') and data.get('stat_name') != "")
            # Check substat count restriction for roll adjustments
            if valid_substats_count < 4:
                changed_data = substats_data[substat_index - 1]
                current_rolls = changed_data.get('rolls', 0)
                stat_name = changed_data.get('stat_name', "")
                
                # Only block roll adjustments if the substat is not empty and user tries to set > 1 roll
                if stat_name and stat_name != "" and current_rolls != 1:
                    self.view.adjusting_rolls = True
                    
                    # Update the UI with adjusted value directly without triggering events
                    rolls_var = self.view.substat_controls[substat_index - 1][5]
                    
                    # Temporarily remove trace to prevent recursive calls
                    trace_id = rolls_var.trace_info()
                    for trace in trace_id:
                        rolls_var.trace_vdelete('w', trace[1])
                    
                    # Set to 1 roll
                    rolls_var.set("1")
                    
                    # Re-add the trace
                    rolls_var.trace('w', 
                                   lambda *args, idx=substat_index: self.on_substat_rolls_change(idx))
                    
                    # Schedule warning message for substat count restriction
                    self.schedule_substat_count_warning()
                    
                    # Reset the flag
                    self.view.adjusting_rolls = False
                
                # Skip total roll validation when < 4 substats
                pass
            else:
                # Normal total roll validation when 4 substats
                total_rolls = sum(data.get('rolls', 0) for data in substats_data if data.get('stat_name'))
                
                # Get current module to check dynamic max total rolls
                module = None
                if hasattr(self.view, 'current_selected_module_id') and self.view.current_selected_module_id:
                    module = self.model.get_module_by_id(self.view.current_selected_module_id)
                
                # Calculate max allowed total rolls
                if module:
                    max_total_rolls = module.get_max_possible_total_rolls()
                else:
                    max_total_rolls = 9  # Default: 4 initial + 5 max enhancements
                
                if total_rolls > max_total_rolls:
                    # Block further processing to prevent infinite loop
                    self.view.adjusting_rolls = True
                    
                    # Calculate how much to reduce
                    excess = total_rolls - max_total_rolls
                    changed_data = substats_data[substat_index - 1]
                    original_rolls = changed_data.get('rolls', 0)
                    adjusted_rolls = max(1, original_rolls - excess)  # Minimum 1 roll
                    
                    # Update the UI with adjusted value directly without triggering events
                    rolls_var = self.view.substat_controls[substat_index - 1][5]
                    
                    # Temporarily remove trace to prevent recursive calls
                    trace_id = rolls_var.trace_info()
                    for trace in trace_id:
                        rolls_var.trace_vdelete('w', trace[1])
                    
                    # Set the adjusted value
                    rolls_var.set(str(adjusted_rolls))
                    
                    # Re-add the trace
                    rolls_var.trace('w', 
                                   lambda *args, idx=substat_index: self.on_substat_rolls_change(idx))
                    
                    # Schedule warning message
                    self.schedule_warning_message(substat_index, adjusted_rolls)
                    
                    # Reset the flag
                    self.view.adjusting_rolls = False
            
        except ValueError:
            pass
        except Exception as e:
            print(f"Error in on_substat_rolls_change: {e}")
        finally:
            self.view.rolls_change_depth = getattr(self.view, 'rolls_change_depth', 0) - 1
        
        # Update value options and total display
        self.update_substat_value_options(substat_index)
        self.view.update_total_rolls_display()
    
    def schedule_warning_message(self, substat_index, adjusted_value):
        """Schedule a warning message, batching multiple rapid adjustments"""
        # Cancel any existing pending warning
        if getattr(self.view, 'pending_warning', None) and self.view.root:
            self.view.root.after_cancel(self.view.pending_warning)
        
        # Schedule new warning with a small delay to batch rapid changes
        def show_warning():
            # Get current module to show accurate limit
            module = None
            if hasattr(self.view, 'current_selected_module_id') and self.view.current_selected_module_id:
                module = self.model.get_module_by_id(self.view.current_selected_module_id)
            
            if module:
                max_total = module.get_max_possible_total_rolls()
                messagebox.showwarning(
                    "Rolls Limit",
                    f"Total rolls cannot exceed {max_total} (4 initial + {module.max_enhancements} enhancements). "
                    f"Substat {substat_index} rolls adjusted to {adjusted_value}."
                )
            else:
                messagebox.showwarning(
                    "Rolls Limit",
                    f"Total rolls limit exceeded. Substat {substat_index} rolls adjusted to {adjusted_value}."
                )
            self.view.pending_warning = None
        
        if self.view.root:
            self.view.pending_warning = self.view.root.after(100, show_warning)  # 100ms delay
    
    def schedule_substat_count_warning(self):
        """Schedule a warning message for substat count restriction"""
        # Cancel any existing pending warning
        if getattr(self.view, 'pending_count_warning', None) and self.view.root:
            self.view.root.after_cancel(self.view.pending_count_warning)
        
        # Schedule new warning with a small delay to batch rapid changes
        def show_warning():
            messagebox.showwarning(
                "Substat Count Restriction",
                "You cannot adjust roll counts until there are 4 substats. Each substat may only have 1 roll."
            )
            self.view.pending_count_warning = None
        
        if self.view.root:
            self.view.pending_count_warning = self.view.root.after(100, show_warning)  # 100ms delay
    
    def on_max_enhancements_change(self):
        """Handle max enhancements configuration change"""
        if not hasattr(self.view, 'current_selected_module_id') or self.view.current_selected_module_id is None:
            return
        
        module_id = self.view.current_selected_module_id
        module = self.model.get_module_by_id(module_id)
        if not module:
            return
        
        try:
            form_data = self.view.get_module_form_data()
            new_max_enhancements = form_data['max_enhancements']
            
            # Validate range
            if new_max_enhancements < 0 or new_max_enhancements > 5:
                self.view.max_enhancements_var.set("5")
                return
            
            # Update module configuration
            module.max_enhancements = new_max_enhancements
            
            # Recalculate remaining enhancements
            module.sync_enhancement_tracking()
            
            # Update display
            self.view.update_remaining_enhancements_display(module.remaining_enhancements)
            
            # Validate current roll configuration
            self._validate_total_roll_limits(module)
            
            # Save changes
            self.model.mathic_system.db.save_module(module)
            
        except (ValueError, AttributeError) as e:
            print(f"Error updating max enhancements: {e}")
    
    def _validate_total_roll_limits(self, module):
        """Validate and adjust rolls if they exceed new limits"""
        max_possible_total = module.get_max_possible_total_rolls()
        current_total = sum(substat.rolls_used for substat in module.substats)
        
        if current_total > max_possible_total:
            # Need to reduce rolls - show warning and suggest action
            messagebox.showwarning(
                "Roll Limit Exceeded",
                f"Current total rolls ({current_total}) exceed new maximum ({max_possible_total}). "
                f"Please manually adjust substat rolls or increase max enhancements."
            )
    
    def update_substat_value_options(self, substat_index):
        """Update value options based on substat type and roll count"""
        if substat_index < 1 or substat_index > 4 or not hasattr(self.view, 'substat_controls'):
            return
        
        form_data = self.view.get_module_form_data()
        substat_data = form_data['substats_data'][substat_index - 1]
        
        stat_name = substat_data['stat_name']
        rolls = substat_data['rolls']
        
        if stat_name and stat_name != "" and rolls > 0:
            value_options = self.model.get_substat_value_options(stat_name, rolls)
            self.view.update_substat_value_options(substat_index, value_options)
        else:
            self.view.update_substat_value_options(substat_index, [])
            # Clear value if no rolls or no stat name
            if hasattr(self.view, 'substat_controls'):
                _, _, _, _, value_var, _ = self.view.substat_controls[substat_index - 1]
                if rolls == 0:
                    value_var.set("")
    
    def apply_module_changes(self):
        """Apply the changes made in the editing controls"""
        if not hasattr(self.view, 'current_selected_module_id') or self.view.current_selected_module_id is None:
            messagebox.showwarning("Warning", "Please select a module to edit")
            return
        
        module_id = self.view.current_selected_module_id
        if not self.model.get_module_by_id(module_id):
            messagebox.showerror("Error", "Selected module not found")
            return
        
        try:
            form_data = self.view.get_module_form_data()
            matrix_info = self.view.get_matrix_info()
            
            # Apply matrix changes if matrix is selected
            if matrix_info['matrix']:
                success, message = self.model.set_module_matrix(
                    module_id,
                    matrix_info['matrix'],
                    matrix_info['matrix_count']
                )
                if not success:
                    messagebox.showerror("Matrix Error", message)
                    return
            else:
                # Clear matrix if none selected
                self.model.clear_module_matrix(module_id)
            
            success, message = self.model.update_module(
                module_id,
                main_stat_value=form_data['main_stat_value'],
                substats_data=form_data['substats_data']
            )
            
            if success:
                messagebox.showinfo("Success", message)
                # Refresh displays
                self.refresh_module_list()

                # Restore selection by module_id
                try:
                    if hasattr(self.view, 'module_ids') and module_id in self.view.module_ids:
                        idx = self.view.module_ids.index(module_id)
                        self.view.module_listbox.selection_set(idx)
                        self.view.module_listbox.activate(idx)
                except Exception:
                    pass

                # Update module details
                module = self.model.get_module_by_id(module_id)
                self.view.update_module_details(module)
                
                # Notify other controllers about module changes (including matrix changes)
                if self.app_controller:
                    self.app_controller.notify_module_update(module_id)
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply changes: {str(e)}")
    
    def new_module(self):
        """Create a new module using values from the editing panel"""
        form_data = self.view.get_module_form_data()
        module_type = form_data['module_type']
        main_stat = form_data['main_stat']
        
        if not main_stat:
            messagebox.showwarning("Warning", "Please select a main stat")
            return
        
        try:
            # Get next available slot for this type
            slot_restrictions = {
                "mask": [1],
                "transistor": [2], 
                "wristwheel": [3],
                "core": [4, 5, 6]
            }
            
            available_slots = slot_restrictions.get(module_type, [1])
            slot = available_slots[0]  # Use first available slot for simplicity
            
            module = self.model.create_module(module_type, slot, main_stat)
            if module:
                messagebox.showinfo("Success", f"Created new {module_type} module")
                self.refresh_module_list()
            else:
                messagebox.showerror("Error", "Failed to create module")
                
        except Exception as e:
            messagebox.showerror("Error", f"Module creation failed: {str(e)}")
    
    def delete_module(self):
        """Delete selected module"""
        selected_index = self.view.get_selected_module_index()
        if selected_index is None:
            messagebox.showwarning("Warning", "Please select a module to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this module?"):
            try:
                module_ids = list(self.model.get_all_modules().keys())
                if selected_index < len(module_ids):
                    module_id = module_ids[selected_index]
                    success = self.model.delete_module(module_id)
                    if success:
                        messagebox.showinfo("Success", "Module deleted successfully")
                        self.refresh_module_list()
                        # Clear selection
                        self.view.current_selected_module_id = None
                    else:
                        messagebox.showerror("Error", "Failed to delete module")
            except Exception as e:
                messagebox.showerror("Error", f"Deletion failed: {str(e)}")
    
    def enhance_module_manual(self):
        """Open manual enhancement dialog"""
        selected_index = self.view.get_selected_module_index()
        if selected_index is None:
            messagebox.showwarning("Warning", "Please select a module to enhance")
            return
        
        module_ids = list(self.model.get_all_modules().keys())
        if selected_index < len(module_ids):
            module_id = module_ids[selected_index]
            module = self.model.get_module_by_id(module_id)
            
            messagebox.showinfo("Manual Enhancement", 
                              f"Use the editing controls to manually adjust {module.module_type} substats.\n"
                              f"Current rolls: {module.total_enhancement_rolls}/{module.max_total_rolls}")
