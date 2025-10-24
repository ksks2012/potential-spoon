"""
Windowing package for the Etheria Simulation Suite
Contains MVC architecture components
"""

# Import from new structure
from .models import (
    BaseModel, CharacterModel, MathicModel, ShellModel, AppState
)

from .views import (
    BaseView, CharacterListView, ShellListView, ModuleEditorView, 
    EnhanceSimulatorView, LoadoutManagerView, SystemOverviewView, MainView
)

from .controllers import (
    BaseController, CharacterController, ShellController, 
    ModuleEditorController, EnhanceSimulatorController,
    LoadoutManagerController, SystemOverviewController, ApplicationController
)

__all__ = [
    # Models
    'BaseModel', 'CharacterModel', 'MathicModel', 'ShellModel', 'AppState',
    
    # Views
    'BaseView', 'CharacterListView', 'ShellListView', 'ModuleEditorView',
    'EnhanceSimulatorView', 'LoadoutManagerView', 'SystemOverviewView', 'MainView',
    
    # Controllers
    'BaseController', 'CharacterController', 'ShellController',
    'ModuleEditorController', 'EnhanceSimulatorController',
    'LoadoutManagerController', 'SystemOverviewController', 'ApplicationController'
]
