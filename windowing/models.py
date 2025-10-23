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

from db.etheria_manager import EtheriaManager
from html_parser.parse_char import CharacterParser
from mathic.mathic_system import MathicSystem


class CharacterModel:
    """Model for character data management using unified database"""
    
    def __init__(self):
        self.manager = EtheriaManager()
        self._characters = []
        self._selected_character = None
        
    def get_all_characters(self):
        """Get all characters from unified database"""
        self._characters = self.manager.characters.get_all_characters()
        return self._characters
    
    def search_characters(self, name_like=None):
        """Search characters by name using unified database"""
        if not name_like:
            return self.get_all_characters()
        
        # Use direct SQL query through manager
        query = """
            SELECT * FROM characters 
            WHERE name LIKE ? 
            ORDER BY name
        """
        results = self.manager.db.execute_query(query, (f'%{name_like}%',))
        return results
    
    def filter_characters(self, rarity=None, element=None):
        """Filter characters by rarity and element using unified database"""
        conditions = []
        params = []
        
        if rarity and rarity != "All":
            conditions.append("rarity = ?")
            params.append(rarity)
        if element and element != "All":
            conditions.append("element = ?")
            params.append(element)
        
        if conditions:
            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT * FROM characters 
                WHERE {where_clause}
                ORDER BY name
            """
            return self.manager.db.execute_query(query, params)
        else:
            return self.get_all_characters()
    
    def get_character_by_name(self, name):
        """Get character details by name from unified database"""
        return self.manager.characters.get_character_by_name(name)
    
    def delete_character(self, name):
        """Delete character from unified database"""
        try:
            query = "DELETE FROM characters WHERE name = ?"
            with self.manager.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting character: {e}")
            return False
    
    def import_character_from_html(self, file_path):
        """Import character data from HTML file using unified database"""
        try:
            parser = CharacterParser(file_path, use_database=True, db_path=self.manager.db.db_path)
            parser.load_html()
            parser.parse_all()
            
            success = parser.save_to_database()
            if success:
                char_name = parser.character_data.get('basic_info', {}).get('name', 'Unknown')
                return True, f"Successfully imported {char_name}"
            else:
                return False, "Failed to store character data"
        except Exception as e:
            return False, f"Import failed: {str(e)}"
    
    def get_character_stats(self):
        """Get character statistics from unified database"""
        stats = self.manager.get_comprehensive_stats()
        return stats['database']
    
    def export_character(self, character_name, file_path):
        """Export character data to JSON file"""
        try:
            character_data = self.get_character_by_name(character_name)
            if character_data:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, indent=2, ensure_ascii=False)
                return True, f"Character '{character_name}' exported successfully"
            else:
                return False, f"Character '{character_name}' not found"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def get_rarities(self):
        """Get available rarities from database"""
        query = "SELECT DISTINCT rarity FROM characters ORDER BY rarity"
        results = self.manager.db.execute_query(query)
        return [row['rarity'] for row in results]
    
    def get_elements(self):
        """Get available elements from database"""
        query = "SELECT DISTINCT element FROM characters ORDER BY element"
        results = self.manager.db.execute_query(query)
        return [row['element'] for row in results]


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
                    if substat_data['stat_name']:
                        substat = Substat(
                            stat_name=substat_data['stat_name'],
                            current_value=substat_data['current_value'],
                            rolls_used=substat_data['rolls_used']
                        )
                        module.substats.append(substat)
                        module.total_enhancement_rolls += substat_data['rolls_used']
            
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
    
    def get_substat_value_options(self, stat_name, rolls):
        """Get possible values for substat based on rolls"""
        if not stat_name or stat_name == "" or rolls <= 0:
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
                # Count module types
                module_type = module.module_type
                overview_data['type_counts'][module_type] = overview_data['type_counts'].get(module_type, 0) + 1
                
                # Track enhancement levels
                level_sum += module.level
                max_level = max(max_level, module.level)
            
            overview_data['avg_level'] = level_sum / len(modules)
            overview_data['max_level'] = max_level
        
        # Calculate loadout equipment information
        for loadout_name, loadout in loadouts.items():
            equipped_count = sum(1 for module_id in loadout.values() if module_id)
            overview_data['loadout_info'][loadout_name] = equipped_count
        
        return overview_data


class ShellModel:
    """Model for shell data management using unified database"""
    
    def __init__(self):
        self.manager = EtheriaManager()
        self._shells = []
        self._selected_shell = None
    
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
                shell_data['matching_matrices_count'] = row['matching_matrices']
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
