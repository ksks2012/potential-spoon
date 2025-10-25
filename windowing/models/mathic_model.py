#!/usr/bin/env python3
"""
Mathic Model for the Etheria Simulation Suite
"""

import sys
import os
from typing import Dict, List, Optional, Tuple, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from mathic.mathic_system import MathicSystem
from .base_model import BaseModel


class MathicModel(BaseModel):
    """Model for mathic system management"""
    
    def __init__(self):
        super().__init__()
        # Get correct config path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(project_root, "mathic", "mathic_config.json")
        
        self.mathic_system = MathicSystem(config_path=config_path)
        self._selected_module_id = None
        self._selected_loadout_name = None
        
    def initialize(self):
        """Initialize the mathic model"""
        # Create sample modules if none exist
        self.create_sample_modules()
    
    def get_all_modules(self):
        """Get all modules"""
        return self.mathic_system.modules
    
    def get_module_by_id(self, module_id):
        """Get module by ID"""
        return self.mathic_system.modules.get(module_id)
    
    def create_module(self, module_type, slot, main_stat):
        """Create a new module"""
        return self.mathic_system.create_module(module_type, slot, main_stat)
    
    def delete_module(self, module_id):
        """Delete a module"""
        return self.mathic_system.delete_module(module_id)
    
    def update_module(self, module_id, main_stat_value=None, substats_data=None):
        """Update module with new data"""
        module = self.mathic_system.get_module_by_id(module_id)
        if not module:
            return False, "Module not found"
        
        try:
            # Update main stat value if provided
            if main_stat_value is not None:
                module.main_stat_value = float(main_stat_value)
            
            # Update substats if provided
            if substats_data:
                from mathic.mathic_system import Substat
                module.substats = []
                module.total_enhancement_rolls = 0  # Reset roll count
                for substat_data in substats_data:
                    stat_name = substat_data.get('stat_name')
                    value = substat_data.get('value')
                    rolls = substat_data.get('rolls', 1)
                    
                    if stat_name and stat_name != "" and value is not None:
                        try:
                            substat = Substat(stat_name, float(value), rolls)
                            module.substats.append(substat)
                            module.total_enhancement_rolls += rolls
                        except (ValueError, TypeError):
                            continue
            
            # Save changes to database
            if self.mathic_system.db.save_module(module):
                return True, "Module updated successfully"
            else:
                return False, "Failed to save module to database"
            
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def enhance_module_random(self, module_id):
        """Randomly enhance a module"""
        module = self.mathic_system.get_module_by_id(module_id)
        if not module:
            return None
        
        return self.mathic_system.enhance_module_random_substat(module)
    
    def enhance_module_multiple(self, module_id, times):
        """Enhance module multiple times"""
        results = []
        for i in range(times):
            enhanced_stat = self.enhance_module_random(module_id)
            if enhanced_stat:
                results.append(enhanced_stat)
            else:
                break
        return results
    
    def calculate_substat_probabilities(self, module_id):
        """Calculate enhancement probabilities for module"""
        if module_id not in self.mathic_system.modules:
            return {}
        
        module = self.mathic_system.modules[module_id]
        return self.mathic_system.calculate_substat_probabilities(module)
    
    def calculate_module_value(self, module_id):
        """Calculate module value analysis"""
        if module_id not in self.mathic_system.modules:
            return {
                "total_value": 0.0, 
                "efficiency": 0.0, 
                "roll_efficiency": 0.0,
                "details": {},
                "defense_score": 0.0,
                "support_score": 0.0,
                "offense_score": 0.0
            }
        
        try:
            module = self.mathic_system.modules[module_id]
            return self.mathic_system.calculate_module_value(module)
        except Exception as e:
            print(f"Error calculating module value for {module_id}: {e}")
            return {
                "total_value": 0.0, 
                "efficiency": 0.0, 
                "roll_efficiency": 0.0,
                "details": {},
                "defense_score": 0.0,
                "support_score": 0.0,
                "offense_score": 0.0
            }
    
    def get_all_loadouts(self):
        """Get all loadouts"""
        return list(self.mathic_system.mathic_loadouts.keys())
    
    def create_loadout(self, name):
        """Create a new loadout"""
        if name not in self.mathic_system.mathic_loadouts:
            self.mathic_system.create_mathic_loadout(name)
            return True
        return False
    
    def delete_loadout(self, name):
        """Delete a loadout"""
        if name in self.mathic_system.mathic_loadouts:
            del self.mathic_system.mathic_loadouts[name]
            return True
        return False
    
    def assign_module_to_loadout(self, loadout_name, slot_id, module_id):
        """Assign module to loadout slot"""
        if module_id == "None":
            module_id = None
        self.mathic_system.assign_module_to_loadout(loadout_name, slot_id, module_id)
    
    def get_loadout_modules(self, loadout_name):
        """Get modules assigned to loadout"""
        return self.mathic_system.get_loadout_modules(loadout_name)
    
    def get_available_main_stats(self, module_type):
        """Get available main stats for module type"""
        if module_type in self.mathic_system.config.get("module_types", {}):
            return self.mathic_system.config["module_types"][module_type]["main_stat_options"]
        return []
    
    def get_max_main_stat_value(self, module_type, main_stat):
        """Get maximum main stat value"""
        if (module_type in self.mathic_system.config.get("module_types", {}) and 
            main_stat in self.mathic_system.config["module_types"][module_type]["max_main_stats"]):
            return self.mathic_system.config["module_types"][module_type]["max_main_stats"][main_stat]
        return 0
    
    def get_available_substats(self, exclude_main_stat=None, module_type=None):
        """Get available substat options"""
        available_stats = list(self.mathic_system.config.get("substats", {}).keys())
        
        # Remove restricted substats for this module type
        if module_type:
            module_type_config = self.mathic_system.config.get("module_types", {}).get(module_type, {})
            restricted_substats = module_type_config.get("restricted_substats", [])
            for restricted_stat in restricted_substats:
                if restricted_stat in available_stats:
                    available_stats.remove(restricted_stat)
        
        if exclude_main_stat and exclude_main_stat in available_stats:
            available_stats.remove(exclude_main_stat)
            
            # Remove percentage version if flat version is main stat (and vice versa)
            main_stat_base = exclude_main_stat.replace('%', '')
            for stat in available_stats[:]:
                stat_base = stat.replace('%', '')
                if stat_base == main_stat_base and stat != exclude_main_stat:
                    available_stats.remove(stat)
        
        return [""] + available_stats
    
    def get_substat_value_options(self, stat_name: str, rolls: int) -> List[str]:
        """Get possible substat values for given stat and rolls"""
        return self.mathic_system.get_substat_value_options(stat_name, rolls)
        
    def get_available_matrices_for_module(self, module_type):
        """Get available matrices for a specific module type"""
        return self.mathic_system.get_available_matrices_for_module(module_type)
    
    def set_module_matrix(self, module_id, matrix_name, matrix_count=3):
        """Set matrix for a module"""
        return self.mathic_system.set_module_matrix(module_id, matrix_name, matrix_count)
    
    def clear_module_matrix(self, module_id):
        """Clear matrix from a module"""
        return self.mathic_system.clear_module_matrix(module_id)
    
    def validate_total_rolls(self, substats_data):
        """Validate that total rolls don't exceed 5"""
        total_rolls = sum(data.get('rolls', 0) for data in substats_data if data.get('stat_name'))
        return total_rolls <= 5, total_rolls
    
    def adjust_rolls_to_limit(self, substats_data, changed_index):
        """Adjust rolls to stay within limit of 5"""
        total_rolls = sum(data.get('rolls', 0) for data in substats_data if data.get('stat_name'))
        
        if total_rolls <= 5:
            return substats_data, None
        
        # Reduce the changed substat to fit within limit
        excess = total_rolls - 5
        changed_data = substats_data[changed_index]
        original_rolls = changed_data.get('rolls', 0)
        adjusted_rolls = max(0, original_rolls - excess)
        
        substats_data[changed_index]['rolls'] = adjusted_rolls
        
        return substats_data, adjusted_rolls
    
    def create_sample_modules(self):
        """Create sample modules for demonstration"""
        if not self.mathic_system.modules:
            try:
                # Create sample modules
                mask = self.mathic_system.create_module("mask", 1, "ATK")
                transistor = self.mathic_system.create_module("transistor", 2, "HP")
                wristwheel = self.mathic_system.create_module("wristwheel", 3, "DEF")
                core1 = self.mathic_system.create_module("core", 4, "CRIT Rate")
                core2 = self.mathic_system.create_module("core", 5, "CRIT DMG")
                
                # Generate substats for each module would go here
                # But depends on the mathic system implementation
                
            except Exception as e:
                print(f"Error creating sample modules: {e}")
    
    def get_system_overview_data(self):
        """Get system overview statistics"""
        modules = self.mathic_system.modules
        loadouts = self.mathic_system.mathic_loadouts
        
        overview_data = {
            'module_count': len(modules),
            'loadout_count': len(loadouts),
            'type_counts': {},
            'avg_level': 0,
            'max_level': 0,
            'loadout_info': {}
        }
        
        if modules:
            # Calculate module type distribution and level statistics
            level_sum = 0
            max_level = 0
            
            for module in modules.values():
                module_type = module.module_type
                overview_data['type_counts'][module_type] = overview_data['type_counts'].get(module_type, 0) + 1
                level_sum += module.level
                max_level = max(max_level, module.level)
            
            overview_data['avg_level'] = level_sum / len(modules)
            overview_data['max_level'] = max_level
        
        # Calculate loadout equipment information
        for loadout_name, loadout in loadouts.items():
            equipped_count = sum(1 for module_id in loadout.values() if module_id)
            overview_data['loadout_info'][loadout_name] = equipped_count
        
        return overview_data
