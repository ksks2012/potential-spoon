#!/usr/bin/env python3
"""
Shell Model for the Etheria Simulation Suite
"""

import sys
import os
from typing import Dict, List, Optional, Tuple, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from db.etheria_manager import EtheriaManager
from .base_model import BaseModel


class ShellModel(BaseModel):
    """Model for shell data management using unified database"""
    
    def __init__(self):
        super().__init__()
        self.manager = EtheriaManager()
        self._shells = []
        self._selected_shell = None
    
    def initialize(self):
        """Initialize the shell model"""
        self._shells = self.get_all_shells()
    
    def get_all_shells(self):
        """Get all shells from unified database"""
        self._shells = self.manager.shells.get_all_shells()
        return self._shells
    
    def get_shell_by_name(self, name):
        """Get shell details by name from unified database"""
        return self.manager.shells.get_shell_by_name(name)
    
    def get_all_matrix_effects(self):
        """Get all available matrix effects for filtering"""
        query = "SELECT DISTINCT name FROM matrix_effects ORDER BY name"
        results = self.manager.db.execute_query(query)
        return [row['name'] for row in results]
    
    def get_shell_classes(self):
        """Get available shell classes from database"""
        query = "SELECT DISTINCT class FROM shells ORDER BY class"
        results = self.manager.db.execute_query(query)
        return [row['class'] for row in results]
    
    def get_shell_rarities(self):
        """Get available shell rarities from database"""
        query = "SELECT DISTINCT rarity FROM shells ORDER BY rarity"
        results = self.manager.db.execute_query(query)
        return [row['rarity'] for row in results]
    
    def filter_shells_by_matrix(self, matrix_names):
        """Filter shells by matrix effects they support"""
        if not matrix_names:
            return self.get_all_shells()
        
        placeholders = ','.join('?' * len(matrix_names))
        query = f"""
            SELECT DISTINCT s.name
            FROM shells s
            JOIN shell_matrix_compatibility smc ON s.id = smc.shell_id
            JOIN matrix_effects me ON smc.matrix_id = me.id
            WHERE me.name IN ({placeholders})
            GROUP BY s.id, s.name
            HAVING COUNT(DISTINCT me.name) = ?
            ORDER BY s.name
        """
        
        params = matrix_names + [len(matrix_names)]
        results = self.manager.db.execute_query(query, params)
        
        filtered_shells = []
        for row in results:
            shell_data = self.get_shell_by_name(row['name'])
            if shell_data:
                filtered_shells.append(shell_data)
        
        return filtered_shells
    
    def filter_shells_by_matrix_any(self, matrix_names):
        """Filter shells that support ANY of the specified matrix effects"""
        if not matrix_names:
            return self.get_all_shells()
        
        placeholders = ','.join('?' * len(matrix_names))
        query = f"""
            SELECT DISTINCT s.name,
                   COUNT(DISTINCT me.name) as matching_matrices
            FROM shells s
            JOIN shell_matrix_compatibility smc ON s.id = smc.shell_id
            JOIN matrix_effects me ON smc.matrix_id = me.id
            WHERE me.name IN ({placeholders})
            GROUP BY s.id, s.name
            ORDER BY matching_matrices DESC, s.name
        """
        
        results = self.manager.db.execute_query(query, matrix_names)
        
        filtered_shells = []
        for row in results:
            shell_data = self.get_shell_by_name(row['name'])
            if shell_data:
                filtered_shells.append(shell_data)
        
        return filtered_shells
    
    def filter_shells_combined(self, matrix_names=None, shell_class=None, rarity=None, filter_mode='all'):
        """Filter shells by multiple criteria"""
        conditions = []
        params = []
        
        # Base query
        query = """
            SELECT DISTINCT s.name, s.class, s.rarity
            FROM shells s
        """
        
        # Add matrix filtering if specified
        if matrix_names:
            placeholders = ','.join('?' * len(matrix_names))
            query += """
                JOIN shell_matrix_compatibility smc ON s.id = smc.shell_id
                JOIN matrix_effects me ON smc.matrix_id = me.id
            """
            conditions.append(f"me.name IN ({placeholders})")
            params.extend(matrix_names)
        
        # Add class filter
        if shell_class and shell_class != "All":
            conditions.append("s.class = ?")
            params.append(shell_class)
        
        # Add rarity filter
        if rarity and rarity != "All":
            conditions.append("s.rarity = ?")
            params.append(rarity)
        
        # Build WHERE clause
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Add GROUP BY and HAVING for matrix filtering
        if matrix_names:
            query += " GROUP BY s.id, s.name, s.class, s.rarity"
            if filter_mode == 'all':
                query += f" HAVING COUNT(DISTINCT me.name) = {len(matrix_names)}"
            # For 'any' mode, no HAVING clause needed
        
        query += " ORDER BY s.name"
        
        results = self.manager.db.execute_query(query, params)
        
        filtered_shells = []
        for row in results:
            shell_data = self.get_shell_by_name(row['name'])
            if shell_data:
                filtered_shells.append(shell_data)
        
        return filtered_shells
    
    def get_shell_matrix_compatibility(self, shell_name):
        """Get matrix compatibility information for a shell"""
        shell_data = self.get_shell_by_name(shell_name)
        if shell_data and 'matrix_compatibility' in shell_data:
            return shell_data['matrix_compatibility']
        return {}
    
    def get_shell_recommendations(self, matrix_effects):
        """Get shell recommendations based on matrix effects"""
        return self.manager.shells.get_shell_recommendations(matrix_effects)
    
    def get_shell_stats(self):
        """Get shell statistics from unified database"""
        stats = self.manager.get_comprehensive_stats()
        return stats['database']
    
    def search_shells(self, name_like=None):
        """Search shells by name"""
        if not name_like:
            return self.get_all_shells()
        
        query = """
            SELECT name FROM shells 
            WHERE name LIKE ? 
            ORDER BY name
        """
        results = self.manager.db.execute_query(query, (f'%{name_like}%',))
        
        filtered_shells = []
        for row in results:
            shell_data = self.get_shell_by_name(row['name'])
            if shell_data:
                filtered_shells.append(shell_data)
        
        return filtered_shells
