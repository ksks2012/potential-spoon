#!/usr/bin/env python3
"""
Shell Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox
from .base_controller import BaseController


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
