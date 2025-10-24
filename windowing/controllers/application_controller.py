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
        
        # Create sub-controllers (only if views are available)
        self.character_controller = None
        self.shell_controller = None
        self.module_editor_controller = None
        self.enhance_simulator_controller = None
        self.loadout_manager_controller = None
        self.system_overview_controller = None
        
        # Initialize character controller if view is available
        character_view = views.get_character_view()
        if character_view:
            self.character_controller = CharacterController(
                models['character'], 
                character_view, 
                app_state
            )
        
        # Initialize other controllers if views are available
        shell_view = views.get_shell_view()
        if shell_view:
            self.shell_controller = ShellController(
                models['shell'], 
                shell_view, 
                app_state
            )
        
        module_editor_view = views.get_module_editor_view()
        if module_editor_view:
            self.module_editor_controller = ModuleEditorController(
                models['mathic'], 
                module_editor_view, 
                app_state
            )
        
        enhance_simulator_view = views.get_enhance_simulator_view()
        if enhance_simulator_view:
            self.enhance_simulator_controller = EnhanceSimulatorController(
                models['mathic'], 
                enhance_simulator_view, 
                app_state
            )
        
        loadout_manager_view = views.get_loadout_manager_view()
        if loadout_manager_view:
            self.loadout_manager_controller = LoadoutManagerController(
                models['mathic'], 
                loadout_manager_view, 
                app_state
            )
        
        system_overview_view = views.get_system_overview_view()
        if system_overview_view:
            self.system_overview_controller = SystemOverviewController(
                models['mathic'], 
                system_overview_view, 
                app_state
            )
        
        # Bind action buttons
        self._bind_character_actions()
    
    def initialize(self):
        """Initialize all controllers"""
        if self.character_controller:
            self.character_controller.initialize()
        if self.shell_controller:
            self.shell_controller.initialize()
        if self.module_editor_controller:
            self.module_editor_controller.initialize()
        if self.enhance_simulator_controller:
            self.enhance_simulator_controller.initialize()
        if self.loadout_manager_controller:
            self.loadout_manager_controller.initialize()
        if self.system_overview_controller:
            self.system_overview_controller.initialize()
        
        # Update status display
        if hasattr(self.views, 'set_status'):
            self.views.set_status(self.app_state.get_status())
    
    def _bind_character_actions(self):
        """Bind character action buttons to controller methods"""
        if self.character_controller and hasattr(self.views, 'import_html_btn'):
            # Bind character action buttons
            self.views.import_html_btn.configure(command=self.character_controller.import_html)
            self.views.import_json_btn.configure(command=self.character_controller.import_json) 
            self.views.export_json_btn.configure(command=self.character_controller.export_json)
            self.views.delete_character_btn.configure(command=self.character_controller.delete_character)
            self.views.refresh_list_btn.configure(command=self.character_controller.refresh_character_list)
    
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
        """Notify all controllers of data changes"""
        # Implementation for notifying controllers of data changes
        pass
