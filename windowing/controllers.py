#!/usr/bin/env python3
"""
Controllers for the Etheria Simulation Suite
Contains business logic and coordinates between Models and Views
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from abc import ABC, abstractmethod


class BaseController(ABC):
    """Abstract base class for all controllers"""
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
    
    @abstractmethod
    def initialize(self):
        """Initialize the controller"""
        pass


class CharacterController(BaseController):
    """Controller for character management"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
    
    def initialize(self):
        """Initialize character controller"""
        self.refresh_character_list()
    
    def refresh_character_list(self):
        """Refresh the character list from model"""
        try:
            self.app_state.set_status("Loading characters...")
            characters = self.model.get_all_characters()
            self.view.update_display(characters)
            self.app_state.set_status(f"Loaded {len(characters)} characters")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load characters: {e}")
            self.app_state.set_status("Error loading characters")
    
    def search_characters(self):
        """Search characters by name"""
        search_term = self.view.get_search_term()
        if not search_term:
            self.refresh_character_list()
            return
        
        try:
            characters = self.model.search_characters(name_like=search_term)
            self.view.update_display(characters)
            self.app_state.set_status(f"Found {len(characters)} characters matching '{search_term}'")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
    
    def filter_characters(self):
        """Filter characters by rarity and element"""
        try:
            filters = self.view.get_filter_values()
            rarity = filters['rarity'] if filters['rarity'] != "All" else None
            element = filters['element'] if filters['element'] != "All" else None
            
            characters = self.model.filter_characters(rarity=rarity, element=element)
            self.view.update_display(characters)
            
            filter_text = f"Filters: {filters['rarity']}, {filters['element']}" if (rarity or element) else "No filters"
            self.app_state.set_status(f"Showing {len(characters)} characters. {filter_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Filtering failed: {e}")
    
    def on_character_select(self):
        """Handle character selection"""
        try:
            character_name = self.view.get_selected_character()
            if not character_name:
                self.view.clear_character_details()
                return
            
            character_data = self.model.get_character_by_name(character_name)
            self.view.update_character_details(character_data)
            self.app_state.set_current_character(character_name)
            self.app_state.set_status(f"Loaded details for {character_name}")
        except Exception as e:
            error_msg = f"Failed to load character details: {e}"
            messagebox.showerror("Error", error_msg)
            self.app_state.set_status(f"Error loading details: {e}")
    
    def import_html(self):
        """Import character data from HTML file"""
        file_path = filedialog.askopenfilename(
            title="Select HTML file",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.app_state.set_status("Parsing HTML file...")
            success, message = self.model.import_character_from_html(file_path)
            
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_character_list()
            else:
                messagebox.showerror("Error", message)
            
            self.app_state.set_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
            self.app_state.set_status("Import failed")
    
    def import_json(self):
        """Import character data from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.app_state.set_status("Importing JSON file...")
            success = self.model.import_from_json(file_path)
            
            if success:
                messagebox.showinfo("Success", "JSON file imported successfully")
                self.refresh_character_list()
            else:
                messagebox.showerror("Error", "Failed to import JSON file")
            
            self.app_state.set_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
            self.app_state.set_status("Import failed")
    
    def export_json(self):
        """Export selected character data to JSON file"""
        character_name = self.view.get_selected_character()
        if not character_name:
            messagebox.showwarning("Warning", "Please select a character to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save character data as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialvalue=f"{character_name.lower()}_data.json"
        )
        
        if not file_path:
            return
        
        try:
            self.app_state.set_status(f"Exporting {character_name}...")
            success = self.model.export_to_json(character_name, file_path)
            
            if success:
                messagebox.showinfo("Success", f"Character data exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export character data")
            
            self.app_state.set_status("Ready")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
            self.app_state.set_status("Export failed")
    
    def delete_character(self):
        """Delete selected character"""
        character_name = self.view.get_selected_character()
        if not character_name:
            messagebox.showwarning("Warning", "Please select a character to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete character '{character_name}'?\n\nThis action cannot be undone."
        )
        
        if result:
            try:
                success = self.model.delete_character(character_name)
                if success:
                    messagebox.showinfo("Success", f"Character '{character_name}' deleted successfully")
                    self.refresh_character_list()
                    self.view.clear_character_details()
                else:
                    messagebox.showerror("Error", "Failed to delete character")
            except Exception as e:
                messagebox.showerror("Error", f"Deletion failed: {e}")


class ShellController(BaseController):
    """Controller for shell management and filtering"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
    
    def initialize(self):
        """Initialize shell controller"""
        self.refresh_shell_list()
        self.setup_filter_options()
    
    def refresh_shell_list(self):
        """Refresh the shell list from model"""
        try:
            self.app_state.set_status("Loading shells...")
            shells = self.model.get_all_shells()
            self.view.update_display(shells)
            self.app_state.set_status(f"Loaded {len(shells)} shells")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shells: {e}")
            self.app_state.set_status("Error loading shells")
    
    def setup_filter_options(self):
        """Setup filter dropdown options"""
        try:
            classes = self.model.get_shell_classes()
            rarities = self.model.get_shell_rarities()
            matrices = self.model.get_all_matrix_effects()
            
            self.view.update_filter_options(classes, rarities, matrices)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load filter options: {e}")
    
    def search_shells(self):
        """Search shells by name"""
        search_term = self.view.get_search_text()
        try:
            if not search_term:
                self.refresh_shell_list()
                return
            
            self.app_state.set_status(f"Searching shells for '{search_term}'...")
            shells = self.model.search_shells(search_term)
            self.view.update_display(shells)
            self.app_state.set_status(f"Found {len(shells)} shells matching '{search_term}'")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
            self.app_state.set_status("Search error")
    
    def apply_filters(self):
        """Apply all current filters"""
        try:
            self.app_state.set_status("Applying filters...")
            
            # Get filter criteria
            search_term = self.view.get_search_text()
            shell_class = self.view.get_selected_class()
            rarity = self.view.get_selected_rarity()
            selected_matrices = self.view.get_selected_matrices()
            filter_mode = self.view.get_filter_mode()
            
            # Apply filters
            if search_term:
                # If searching, start with search results
                shells = self.model.search_shells(search_term)
            else:
                # Apply combined filters
                shells = self.model.filter_shells_combined(
                    matrix_names=selected_matrices if selected_matrices else None,
                    shell_class=shell_class,
                    rarity=rarity,
                    filter_mode=filter_mode
                )
            
            self.view.update_display(shells)
            
            # Create status message
            filter_parts = []
            if search_term:
                filter_parts.append(f"search: '{search_term}'")
            if shell_class != "All":
                filter_parts.append(f"class: {shell_class}")
            if rarity != "All":
                filter_parts.append(f"rarity: {rarity}")
            if selected_matrices:
                filter_parts.append(f"matrices: {len(selected_matrices)} selected ({filter_mode})")
            
            if filter_parts:
                filter_desc = ", ".join(filter_parts)
                self.app_state.set_status(f"Filtered {len(shells)} shells ({filter_desc})")
            else:
                self.app_state.set_status(f"Showing all {len(shells)} shells")
                
        except Exception as e:
            messagebox.showerror("Error", f"Filter failed: {e}")
            self.app_state.set_status("Filter error")
    
    def select_shell(self, shell_name):
        """Handle shell selection"""
        try:
            # Extract actual shell name from display name
            actual_name = shell_name.split(" (")[0] if " (" in shell_name else shell_name
            
            self.app_state.set_status(f"Loading details for {actual_name}...")
            shell_data = self.model.get_shell_by_name(actual_name)
            
            if shell_data:
                self.view.update_shell_details(shell_data)
                self.app_state.set_status(f"Showing details for {actual_name}")
            else:
                self.view.update_shell_details(None)
                self.app_state.set_status(f"Shell '{actual_name}' not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load shell details: {e}")
            self.app_state.set_status("Error loading shell details")
    
    def get_shell_recommendations(self, matrix_effects):
        """Get shell recommendations based on matrix effects"""
        try:
            recommendations = self.model.get_shell_recommendations(matrix_effects)
            return recommendations
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get recommendations: {e}")
            return []


class ModuleEditorController(BaseController):
    """Controller for module editing"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
    
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
                self.view.update_module_details(module)
                self.app_state.set_current_module(module_id)
    
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
        """Update substat combo options based on main stat and module type"""
        form_data = self.view.get_module_form_data()
        main_stat = form_data['main_stat']
        module_type = form_data['module_type']
        
        available_stats = self.model.get_available_substats(
            exclude_main_stat=main_stat, 
            module_type=module_type
        )
        self.view.update_substat_options(available_stats)
    
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
        
        self.update_substat_value_options(substat_index)
        self.view.update_total_rolls_display()
    
    def on_substat_rolls_change(self, substat_index):
        """Handle substat rolls change - update value options and validate restrictions"""
        # Prevent infinite loops during adjustment or messagebox display
        if getattr(self.view, 'adjusting_rolls', False):
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
                
                # Block roll adjustments and reset to 1
                if current_rolls != 1:
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
                
                if total_rolls > 5:
                    # Block further processing to prevent infinite loop
                    self.view.adjusting_rolls = True
                    
                    # Calculate how much to reduce
                    excess = total_rolls - 5
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
            messagebox.showwarning(
                "Rolls Limit",
                f"Total rolls cannot exceed 5. Substat {substat_index} rolls adjusted to {adjusted_value}."
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
                module = self.model.get_module_by_id(module_id)
                self.view.update_module_details(module)
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


class SystemOverviewController(BaseController):
    """Controller for system overview"""
    
    def __init__(self, model, view, app_state):
        super().__init__(model, view)
        self.app_state = app_state
    
    def initialize(self):
        """Initialize system overview controller"""
        self.refresh_overview()
    
    def refresh_overview(self):
        """Refresh system overview data"""
        try:
            overview_data = self.model.get_system_overview_data()
            self.view.update_display(overview_data)
            self.app_state.set_status("System overview updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh overview: {e}")
    
    def on_data_change(self):
        """Handle data changes that require overview refresh"""
        self.refresh_overview()


class ApplicationController:
    """Main application controller that coordinates all sub-controllers"""
    
    def __init__(self, models, views, app_state):
        self.models = models
        self.views = views
        self.app_state = app_state
        
        # Create sub-controllers
        self.character_controller = CharacterController(
            models['character'], 
            views.get_character_view(), 
            app_state
        )
        
        self.shell_controller = ShellController(
            models['shell'], 
            views.get_shell_view(), 
            app_state
        )
        
        self.module_editor_controller = ModuleEditorController(
            models['mathic'], 
            views.get_module_editor_view(), 
            app_state
        )
        
        self.enhance_simulator_controller = EnhanceSimulatorController(
            models['mathic'], 
            views.get_enhance_simulator_view(), 
            app_state
        )
        
        self.loadout_manager_controller = LoadoutManagerController(
            models['mathic'], 
            views.get_loadout_manager_view(), 
            app_state
        )
        
        self.system_overview_controller = SystemOverviewController(
            models['mathic'], 
            views.get_system_overview_view(), 
            app_state
        )
        
        # Bind action buttons
        self._bind_character_actions()
    
    def initialize(self):
        """Initialize all controllers"""
        self.character_controller.initialize()
        self.shell_controller.initialize()
        self.module_editor_controller.initialize()
        self.enhance_simulator_controller.initialize()
        self.loadout_manager_controller.initialize()
        self.system_overview_controller.initialize()
        
        # Update status display
        self.views.set_status(self.app_state.get_status())
    
    def _bind_character_actions(self):
        """Bind character action buttons to controller methods"""
        views = self.views
        
        views.import_html_btn.configure(command=self.character_controller.import_html)
        views.import_json_btn.configure(command=self.character_controller.import_json)
        views.export_json_btn.configure(command=self.character_controller.export_json)
        views.delete_character_btn.configure(command=self.character_controller.delete_character)
        views.refresh_list_btn.configure(command=self.character_controller.refresh_character_list)
    
    def get_character_controller(self):
        """Get character controller"""
        return self.character_controller
    
    def get_shell_controller(self):
        """Get shell controller"""
        return self.shell_controller
    
    def get_module_editor_controller(self):
        """Get module editor controller"""
        return self.module_editor_controller
    
    def get_enhance_simulator_controller(self):
        """Get enhance simulator controller"""
        return self.enhance_simulator_controller
    
    def get_loadout_manager_controller(self):
        """Get loadout manager controller"""
        return self.loadout_manager_controller
    
    def get_system_overview_controller(self):
        """Get system overview controller"""
        return self.system_overview_controller
    
    def notify_data_change(self):
        """Notify all controllers that data has changed"""
        # Refresh system overview when any mathic data changes
        self.system_overview_controller.on_data_change()
        
        # Refresh other views that might depend on the data
        self.module_editor_controller.refresh_module_list()
        self.loadout_manager_controller.refresh_loadout_list()
