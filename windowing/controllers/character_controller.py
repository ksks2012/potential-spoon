#!/usr/bin/env python3
"""
Character Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox, filedialog
from .base_controller import BaseController


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
    def on_character_select(self):
        """Handle character selection"""
        try:
            character_name = self.view.get_selected_character()
            if character_name:
                character_data = self.model.get_character_by_name(character_name)
                self.view.update_character_details(character_data)
                self.app_state.set_current_character(character_name)
                self.app_state.set_status(f"Selected character: {character_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load character details: {e}")
    
    def import_html(self):
        """Import character data from HTML file"""
        file_path = filedialog.askopenfilename(
            title="Select HTML file",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            success, message = self.model.import_character_from_html(file_path)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_character_list()
            else:
                messagebox.showerror("Error", message)
            self.app_state.set_status(message)
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
    
    def import_json(self):
        """Import character data from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Implementation would depend on JSON import functionality
            messagebox.showinfo("Info", "JSON import not yet implemented")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
    
    def export_json(self):
        """Export selected character data to JSON file"""
        character_name = self.view.get_selected_character()
        if not character_name:
            messagebox.showwarning("Warning", "Please select a character first")
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
            success, message = self.model.export_character(character_name, file_path)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
            self.app_state.set_status(message)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def delete_character(self):
        """Delete selected character"""
        character_name = self.view.get_selected_character()
        if not character_name:
            messagebox.showwarning("Warning", "Please select a character first")
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
                    messagebox.showerror("Error", f"Failed to delete character '{character_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {e}")
