#!/usr/bin/env python3
"""
Application State for the Etheria Simulation Suite
"""

from .base_model import BaseModel


class AppState(BaseModel):
    """Model for application state management"""
    
    def __init__(self):
        super().__init__()
        self.status_message = "Ready"
        self.current_character = None
        self.current_module_id = None
        self.current_loadout = None
        self.selected_tab = 0
        
    def initialize(self):
        """Initialize the app state"""
        self.status_message = "Application initialized"
    
    def set_status(self, message):
        """Set status message"""
        self.status_message = message
    
    def get_status(self):
        """Get current status message"""
        return self.status_message
    
    def set_current_character(self, character_name):
        """Set currently selected character"""
        self.current_character = character_name
    
    def set_current_module(self, module_id):
        """Set currently selected module"""
        self.current_module_id = module_id
    
    def set_current_loadout(self, loadout_name):
        """Set currently selected loadout"""
        self.current_loadout = loadout_name
