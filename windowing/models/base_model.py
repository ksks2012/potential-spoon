#!/usr/bin/env python3
"""
Base Model for the Etheria Simulation Suite
"""

from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Abstract base class for all models"""
    
    def __init__(self):
        pass
    
    @abstractmethod
    def initialize(self):
        """Initialize the model"""
        pass
