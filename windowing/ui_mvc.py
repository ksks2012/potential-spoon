#!/usr/bin/env python3
"""
Main application entry point using MVC architecture
Etheria Simulation Suite - Refactored Version
"""

import tkinter as tk
import sys
import os

# Add project root and windowing directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
windowing_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(windowing_dir)

from windowing.models import CharacterModel, MathicModel, ShellModel, AppState
from windowing.views import MainView
from windowing.controllers import ApplicationController


class EtheriaApplication:
    """Main application class that initializes and coordinates MVC components"""
    
    def __init__(self):
        # Create root window
        self.root = tk.Tk()
        
        # Initialize models
        print("Initializing models...")
        self.models = {
            'character': CharacterModel(),
            'mathic': MathicModel(),
            'shell': ShellModel(),
        }
        
        # Initialize app state
        self.app_state = AppState()
        
        # Initialize all models
        print("Loading data...")
        for name, model in self.models.items():
            print(f"Initializing {name} model...")
            model.initialize()
        self.app_state.initialize()
        
        # Initialize main view
        print("Creating user interface...")
        self.main_view = MainView(self.root)
        self.main_view.create_widgets()
        
        # Initialize application controller
        print("Setting up controllers...")
        self.app_controller = ApplicationController(
            self.models, 
            self.main_view, 
            self.app_state
        )
        
        # Setup periodic status updates
        self._setup_status_updates()
        
        print("Application initialized successfully!")
    
    def _setup_status_updates(self):
        """Setup periodic status updates from app state to view"""
        def update_status():
            current_status = self.app_state.get_status()
            self.main_view.set_status(current_status)
            # Schedule next update
            self.root.after(100, update_status)  # Update every 100ms
        
        # Start status updates
        update_status()
    
    def run(self):
        """Run the application"""
        try:
            # Initialize all controllers
            print("Initializing controllers...")
            self.app_controller.initialize()
            
            # Show startup info
            print(f"Character data: {len(self.models['character']._characters)} characters loaded")
            print(f"Mathic modules: {len(self.models['mathic'].get_all_modules())} modules loaded")
            print(f"Shell data: {len(self.models['shell']._shells)} shells loaded")
            print("Starting application...")
            
            # Start the main event loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\nApplication closed by user")
        except Exception as e:
            print(f"Application error: {e}")
            import traceback
            traceback.print_exc()
    
    def get_models(self):
        """Get application models"""
        return self.models
    
    def get_views(self):
        """Get main view"""
        return self.main_view
    
    def get_controller(self):
        """Get application controller"""
        return self.app_controller


def main():
    """Main function to run the application"""
    try:
        # Create and run application
        app = EtheriaApplication()
        app.run()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
