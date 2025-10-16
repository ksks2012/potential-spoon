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
    
    def on_module_type_change(self):
        """Handle module type change"""
        form_data = self.view.get_module_form_data()
        module_type = form_data['module_type']
        
        # Update main stat options
        main_stat_options = self.model.get_available_main_stats(module_type)
        self.view.update_main_stat_options(main_stat_options)
        
        if main_stat_options:
            self.view.main_stat_var.set(main_stat_options[0])
            self.on_main_stat_change()
        
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
        """Update substat combo options based on main stat"""
        form_data = self.view.get_module_form_data()
        main_stat = form_data['main_stat']
        
        available_stats = self.model.get_available_substats(exclude_main_stat=main_stat)
        self.view.update_substat_options(available_stats)
    
    def on_substat_type_change(self, substat_index):
        """Handle substat type change - update value options and total rolls"""
        self.update_substat_value_options(substat_index)
        self.view.update_total_rolls_display()
    
    def on_substat_rolls_change(self, substat_index):
        """Handle substat rolls change - update value options and validate total rolls"""
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
            
            # Calculate what the new total would be
            total_rolls = sum(data.get('rolls', 0) for data in substats_data if data.get('stat_name'))
            
            if total_rolls > 5:
                # Block further processing to prevent infinite loop
                self.view.adjusting_rolls = True
                
                # Calculate how much to reduce
                excess = total_rolls - 5
                changed_data = substats_data[substat_index - 1]
                original_rolls = changed_data.get('rolls', 0)
                adjusted_rolls = max(0, original_rolls - excess)
                
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
    
    def update_substat_value_options(self, substat_index):
        """Update value options based on substat type and roll count"""
        if substat_index < 1 or substat_index > 4 or not hasattr(self.view, 'substat_controls'):
            return
        
        form_data = self.view.get_module_form_data()
        substat_data = form_data['substats_data'][substat_index - 1]
        
        stat_name = substat_data['stat_name']
        rolls = substat_data['rolls']
        
        if stat_name and stat_name != "":
            value_options = self.model.get_substat_value_options(stat_name, rolls)
            self.view.update_substat_value_options(substat_index, value_options)
        else:
            self.view.update_substat_value_options(substat_index, [])
    
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
        
        self.module_editor_controller = ModuleEditorController(
            models['mathic'], 
            views.get_module_editor_view(), 
            app_state
        )
        
        # Bind action buttons
        self._bind_character_actions()
    
    def initialize(self):
        """Initialize all controllers"""
        self.character_controller.initialize()
        self.module_editor_controller.initialize()
        
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
    
    def get_module_editor_controller(self):
        """Get module editor controller"""
        return self.module_editor_controller
