#!/usr/bin/env python3
"""
System Overview Controller for the Etheria Simulation Suite
"""

from tkinter import messagebox
from .base_controller import BaseController


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
