#!/usr/bin/env python3
"""
Base View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from abc import ABC, abstractmethod


class BaseView(ABC):
    """Abstract base class for all views"""
    
    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        
    def set_controller(self, controller):
        """Set the controller for this view"""
        self.controller = controller
    
    @abstractmethod
    def create_widgets(self):
        """Create and layout widgets"""
        pass
    
    @abstractmethod
    def update_display(self, data):
        """Update display with new data"""
        pass
