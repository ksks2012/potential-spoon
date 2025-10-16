#!/usr/bin/env python3
"""
Models for the Etheria Simulation Suite
Contains data models and business logic separated from UI
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from db.db_routing import CharacterDatabase
from html_parser.parse_char import CharacterParser
from mathic.mathic_system import MathicSystem


class CharacterModel:
    """Model for character data management"""
    
    def __init__(self):
        self.db = CharacterDatabase()
        self._characters = []
        self._selected_character = None
        
    def get_all_characters(self):
        """Get all characters from database"""
        self._characters = self.db.get_all_characters()
        return self._characters
    
    def search_characters(self, name_like=None):
        """Search characters by name"""
        return self.db.search_characters(name_like=name_like)
    
    def filter_characters(self, rarity=None, element=None):
        """Filter characters by rarity and element"""
        search_params = {}
        if rarity and rarity != "All":
            search_params['rarity'] = rarity
        if element and element != "All":
            search_params['element'] = element
        
        if search_params:
            return self.db.get_characters_by_criteria(**search_params)
        else:
            return self.get_all_characters()
    
    def get_character_by_name(self, name):
        """Get character details by name"""
        return self.db.get_character_by_name(name)
    
    def delete_character(self, name):
        """Delete character from database"""
        return self.db.delete_character(name)
    
    def import_character_from_html(self, file_path):
        """Import character data from HTML file"""
        parser = CharacterParser(file_path)
        character_data = parser.parse_all()
        
        if character_data:
            success = self.db.store_character(character_data)
            if success:
                return True, f"Successfully imported {character_data['basic_info']['name']}"
            else:
                return False, "Failed to store character data"
        else:
            return False, "No character data found in HTML file"
    
    def import_from_json(self, file_path):
        """Import character data from JSON file"""
        return self.db.import_from_json(file_path)
    
    def export_to_json(self, character_name, file_path):
        """Export character data to JSON file"""
        return self.db.export_to_json(character_name, file_path)


class MathicModel:
    """Model for mathic system management"""
    
    def __init__(self):
        # Get correct config path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "mathic", "mathic_config.json")
        
        self.mathic_system = MathicSystem(config_path=config_path)
        self._selected_module_id = None
        self._selected_loadout_name = None
        
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
        if module_id in self.mathic_system.modules:
            del self.mathic_system.modules[module_id]
            return True
        return False
    
    def update_module(self, module_id, main_stat_value=None, substats_data=None):
        """Update module with new data"""
        if module_id not in self.mathic_system.modules:
            return False, "Module not found"
        
        module = self.mathic_system.modules[module_id]
        
        try:
            # Update main stat value if provided
            if main_stat_value is not None:
                module.main_stat_value = float(main_stat_value)
            
            # Update substats if provided
            if substats_data:
                from mathic.mathic_system import Substat
                module.substats = []
                for substat_data in substats_data:
                    if substat_data['stat_name']:
                        substat = Substat(
                            stat_name=substat_data['stat_name'],
                            current_value=substat_data['current_value'],
                            rolls_used=substat_data['rolls_used']
                        )
                        module.substats.append(substat)
            
            return True, "Module updated successfully"
            
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def enhance_module_random(self, module_id):
        """Randomly enhance a module"""
        if module_id not in self.mathic_system.modules:
            return None
        
        module = self.mathic_system.modules[module_id]
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
            return {}
        
        module = self.mathic_system.modules[module_id]
        return self.mathic_system.calculate_module_value(module)
    
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
    
    def get_available_substats(self, exclude_main_stat=None):
        """Get available substat options"""
        available_stats = list(self.mathic_system.config.get("substats", {}).keys())
        
        if exclude_main_stat and exclude_main_stat in available_stats:
            available_stats.remove(exclude_main_stat)
            
            # Remove percentage version if flat version is main stat (and vice versa)
            main_stat_base = exclude_main_stat.replace('%', '')
            for stat in available_stats[:]:
                stat_base = stat.replace('%', '')
                if stat_base == main_stat_base and stat != exclude_main_stat:
                    available_stats.remove(stat)
        
        return [""] + available_stats
    
    def get_substat_value_options(self, stat_name, rolls):
        """Get possible values for substat based on rolls"""
        if not stat_name or stat_name == "":
            return []
        
        if stat_name in self.mathic_system.config["substats"]:
            stat_config = self.mathic_system.config["substats"][stat_name]
            roll_range = stat_config["roll_range"]
            min_roll, max_roll = roll_range
            
            # Calculate possible values based on rolls
            possible_values = []
            for roll_value in range(min_roll, max_roll + 1):
                total_value = roll_value * rolls
                possible_values.append(str(total_value))
            
            return possible_values
        
        return []
    
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
                
                # Generate substats for each module
                modules = [mask, transistor, wristwheel, core1, core2]
                for module in modules:
                    if module:
                        self.mathic_system.generate_random_substats(module, 4)
                
                # Create sample loadouts
                self.mathic_system.create_mathic_loadout("DPS Build")
                self.mathic_system.create_mathic_loadout("Tank Build")
                
            except Exception as e:
                print(f"Error creating sample modules: {e}")


class AppState:
    """Model for application state management"""
    
    def __init__(self):
        self.status_message = "Ready"
        self.current_character = None
        self.current_module_id = None
        self.current_loadout = None
        self.selected_tab = 0
        
    def set_status(self, message):
        """Set status message"""
        self.status_message = message
    
    def get_status(self):
        """Get current status message"""
        return self.status_message
    
    def set_current_character(self, character_name):
        """Set currently selected character"""
        self.current_character = character_name
    
    def set_current_module(self, module_id):
        """Set currently selected module"""
        self.current_module_id = module_id
    
    def set_current_loadout(self, loadout_name):
        """Set currently selected loadout"""
        self.current_loadout = loadout_name
