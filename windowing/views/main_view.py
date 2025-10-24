#!/usr/bin/env python3
"""
Main View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView
from .character_view import CharacterListView
from .shell_view import ShellListView
from .module_editor_view import ModuleEditorView
from .enhance_simulator_view import EnhanceSimulatorView
from .loadout_manager_view import LoadoutManagerView
from .system_overview_view import SystemOverviewView


class MainView(BaseView):
    """Main application view that contains all sub-views"""
    
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("Etheria Simulation Suite")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        
        # Sub-views
        self.character_view = None
        self.shell_view = None
        self.module_editor_view = None
        self.enhance_simulator_view = None
        self.loadout_manager_view = None
        self.system_overview_view = None
        
    def create_widgets(self):
        """Create main window widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Main notebook for top-level tabs
        self.main_notebook = ttk.Notebook(main_frame)
        self.main_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Character Pokedex tab
        char_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(char_frame, text="Character Pokedex")
        self.character_view = CharacterListView(char_frame)
        self.character_view.create_widgets()
        
        # Create Shell Pokedex tab
        shell_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(shell_frame, text="Shell Pokedex")
        self.shell_view = ShellListView(shell_frame)
        self.shell_view.create_widgets()
        
        # Create Mathic System tab  
        mathic_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(mathic_frame, text="Mathic System")
        self._create_mathic_tabs(mathic_frame)
        
        # Action buttons for character tab
        self._create_character_action_buttons(char_frame)
        
        # Status bar
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        return main_frame
    
    def _create_mathic_tabs(self, parent):
        """Create mathic system tabs"""
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create notebook for mathic subsystems
        mathic_notebook = ttk.Notebook(parent)
        mathic_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Module Editor tab
        module_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(module_frame, text="Module Editor")
        self.module_editor_view = ModuleEditorView(module_frame)
        self.module_editor_view.create_widgets()
        
        # Enhance Simulator tab
        enhance_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(enhance_frame, text="Enhance Simulator")
        self.enhance_simulator_view = EnhanceSimulatorView(enhance_frame)
        self.enhance_simulator_view.create_widgets()
        
        # Loadout Manager tab
        loadout_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(loadout_frame, text="Loadout Manager")
        self.loadout_manager_view = LoadoutManagerView(loadout_frame)
        self.loadout_manager_view.create_widgets()
        
        # System Overview tab
        overview_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(overview_frame, text="System Overview")
        self.system_overview_view = SystemOverviewView(overview_frame)
        self.system_overview_view.create_widgets()
    
    def _create_character_action_buttons(self, parent):
        """Create action buttons for character tab"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        self.import_html_btn = ttk.Button(button_frame, text="Import HTML")
        self.import_html_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.import_json_btn = ttk.Button(button_frame, text="Import JSON")
        self.import_json_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_json_btn = ttk.Button(button_frame, text="Export JSON")
        self.export_json_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_character_btn = ttk.Button(button_frame, text="Delete Character")
        self.delete_character_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_list_btn = ttk.Button(button_frame, text="Refresh List")
        self.refresh_list_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def update_display(self, data):
        """Update main view display"""
        # Basic implementation - individual views handle their own updates
        pass
    
    def set_status(self, message):
        """Set status message"""
        self.status_var.set(message)
    
    def get_character_view(self):
        """Get character view"""
        return self.character_view
    
    def get_shell_view(self):
        """Get shell view"""
        return self.shell_view
    
    def get_module_editor_view(self):
        """Get module editor view"""
        return self.module_editor_view
    
    def get_enhance_simulator_view(self):
        """Get enhance simulator view"""
        return self.enhance_simulator_view
    
    def get_loadout_manager_view(self):
        """Get loadout manager view"""
        return self.loadout_manager_view
    
    def get_system_overview_view(self):
        """Get system overview view"""
        return self.system_overview_view
