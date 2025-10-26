#!/usr/bin/env python3
"""
Base Controller for the Etheria Simulation Suite
"""

from abc import ABC, abstractmethod


class BaseController(ABC):
    """Abstract base class for all controllers"""
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
    
    @abstractmethod
    def initialize(self):
        """Initialize the controller"""
        pass
