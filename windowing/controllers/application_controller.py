#!/usr/bin/env python3
"""
Application Controller for the Etheria Simulation Suite
"""

from .character_controller import CharacterController
from .shell_controller import ShellController
from .module_editor_controller import ModuleEditorController
from .enhance_simulator_controller import EnhanceSimulatorController
from .loadout_manager_controller import LoadoutManagerController
from .system_overview_controller import SystemOverviewController


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
