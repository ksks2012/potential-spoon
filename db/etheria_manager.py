from typing import Dict, List, Optional
from .unified_db import EtheriaDatabase
from .character_manager import CharacterManager
from .matrix_manager import MatrixManager
from .shell_manager import ShellManager
import json
import os


class EtheriaManager:
    """Unified manager for all Etheria data operations"""
    
    def __init__(self, db_path: str = "./db/etheria.db"):
        """Initialize unified manager with database and sub-managers"""
        self.db = EtheriaDatabase(db_path)
        self.characters = CharacterManager(self.db)
        self.matrices = MatrixManager(self.db)
        self.shells = ShellManager(self.db)
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics from all modules"""
        base_stats = self.db.get_database_stats()
        
        # Add matrix usage stats
        matrix_usage = self.matrices.get_matrix_usage_by_shells()
        
        # Calculate integration metrics
        integration_stats = self._calculate_integration_stats()
        
        return {
            'database': base_stats,
            'matrix_usage_by_shells': matrix_usage,
            'integration': integration_stats
        }
    
    def _calculate_integration_stats(self) -> Dict:
        """Calculate integration statistics between modules"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Shell-Matrix integration
            cursor.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM shells) as total_shells,
                    (SELECT COUNT(*) FROM matrix_effects) as total_matrices,
                    (SELECT COUNT(DISTINCT shell_id) FROM shell_matrix_compatibility) as shells_with_matrices,
                    (SELECT COUNT(DISTINCT matrix_id) FROM shell_matrix_compatibility) as matrices_used_by_shells,
                    (SELECT COUNT(*) FROM shell_matrix_compatibility) as total_shell_matrix_relationships
            ''')
            
            result = cursor.fetchone()
            
            stats['shell_matrix'] = {
                'total_shells': result['total_shells'],
                'total_matrices': result['total_matrices'],
                'shells_with_matrices': result['shells_with_matrices'],
                'matrices_used_by_shells': result['matrices_used_by_shells'],
                'total_relationships': result['total_shell_matrix_relationships'],
                'shell_coverage': (result['shells_with_matrices'] / max(result['total_shells'], 1)) * 100,
                'matrix_usage': (result['matrices_used_by_shells'] / max(result['total_matrices'], 1)) * 100
            }
            
            # Character-Shell integration
            cursor.execute('''
                SELECT 
                    (SELECT COUNT(*) FROM characters) as total_characters,
                    (SELECT COUNT(DISTINCT character_id) FROM character_shell_equipment) as characters_with_shells,
                    (SELECT COUNT(*) FROM character_shell_equipment WHERE is_active = 1) as active_shell_equipment
            ''')
            
            result = cursor.fetchone()
            
            stats['character_shell'] = {
                'total_characters': result['total_characters'],
                'characters_with_shells': result['characters_with_shells'],
                'active_equipment': result['active_shell_equipment'],
                'equipment_rate': (result['characters_with_shells'] / max(result['total_characters'], 1)) * 100
            }
            
            # Character-Matrix integration
            cursor.execute('''
                SELECT 
                    (SELECT COUNT(DISTINCT character_id) FROM character_matrix_loadouts) as characters_with_loadouts,
                    (SELECT COUNT(DISTINCT loadout_name) FROM character_matrix_loadouts) as unique_loadouts,
                    (SELECT COUNT(*) FROM character_matrix_loadouts WHERE is_active = 1) as active_loadouts
            ''')
            
            result = cursor.fetchone()
            
            stats['character_matrix'] = {
                'characters_with_loadouts': result['characters_with_loadouts'],
                'unique_loadout_names': result['unique_loadouts'],
                'active_loadouts': result['active_loadouts']
            }
            
            return stats
    
    def import_all_data(self, characters_json: str = None, matrices_json: str = None, 
                       shells_json: str = None) -> Dict:
        """Import data from multiple JSON sources"""
        results = {
            'characters': {'success': False, 'count': 0, 'errors': []},
            'matrices': {'success': False, 'count': 0, 'errors': []},
            'shells': {'success': False, 'count': 0, 'errors': []}
        }
        
        # Import characters
        if characters_json and os.path.exists(characters_json):
            try:
                with open(characters_json, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                
                char_id = self.characters.insert_character(char_data)
                if char_id:
                    results['characters']['success'] = True
                    results['characters']['count'] = 1
                else:
                    results['characters']['errors'].append("Failed to insert character")
                    
            except Exception as e:
                results['characters']['errors'].append(str(e))
        
        # Import matrices (assuming it's an array of matrix effects)
        if matrices_json and os.path.exists(matrices_json):
            try:
                with open(matrices_json, 'r', encoding='utf-8') as f:
                    matrices_data = json.load(f)
                
                if isinstance(matrices_data, list):
                    for matrix_data in matrices_data:
                        matrix_id = self.matrices.insert_matrix_effect(matrix_data)
                        if matrix_id:
                            results['matrices']['count'] += 1
                        else:
                            results['matrices']['errors'].append(f"Failed to insert matrix: {matrix_data.get('name', 'Unknown')}")
                else:
                    matrix_id = self.matrices.insert_matrix_effect(matrices_data)
                    if matrix_id:
                        results['matrices']['count'] = 1
                
                results['matrices']['success'] = results['matrices']['count'] > 0
                    
            except Exception as e:
                results['matrices']['errors'].append(str(e))
        
        # Import shells (assuming it's an array of shells)
        if shells_json and os.path.exists(shells_json):
            try:
                with open(shells_json, 'r', encoding='utf-8') as f:
                    shells_data = json.load(f)
                
                if isinstance(shells_data, list):
                    for shell_data in shells_data:
                        shell_id = self.shells.insert_shell(shell_data)
                        if shell_id:
                            results['shells']['count'] += 1
                        else:
                            results['shells']['errors'].append(f"Failed to insert shell: {shell_data.get('name', 'Unknown')}")
                else:
                    shell_id = self.shells.insert_shell(shells_data)
                    if shell_id:
                        results['shells']['count'] = 1
                
                results['shells']['success'] = results['shells']['count'] > 0
                    
            except Exception as e:
                results['shells']['errors'].append(str(e))
        
        return results
    
    def migrate_from_separate_databases(self, 
                                       characters_db_path: str = "./db/characters.db",
                                       matrices_db_path: str = "./db/matrix_effects.db", 
                                       shells_db_path: str = "./db/shells.db") -> Dict:
        """Migrate data from separate database files to unified database"""
        migration_results = {
            'characters': 0,
            'matrices': 0, 
            'shells': 0,
            'errors': []
        }
        
        try:
            # Migrate characters
            if os.path.exists(characters_db_path):
                from .db_routing import CharacterDatabase
                old_char_db = CharacterDatabase(characters_db_path)
                characters = old_char_db.get_all_characters()
                
                for char_basic in characters:
                    char_data = old_char_db.get_character_by_name(char_basic['name'])
                    if char_data:
                        char_id = self.characters.insert_character(char_data)
                        if char_id:
                            migration_results['characters'] += 1
            
            # Migrate matrix effects
            if os.path.exists(matrices_db_path):
                from .matrix_db import MatrixDatabase
                old_matrix_db = MatrixDatabase(matrices_db_path)
                matrices = old_matrix_db.get_all_matrix_effects()
                
                for matrix_data in matrices:
                    matrix_id = self.matrices.insert_matrix_effect(matrix_data)
                    if matrix_id:
                        migration_results['matrices'] += 1
            
            # Migrate shells
            if os.path.exists(shells_db_path):
                from .shells_db import ShellsDatabase
                old_shell_db = ShellsDatabase(shells_db_path)
                shells = old_shell_db.get_all_shells()
                
                for shell_data in shells:
                    shell_id = self.shells.insert_shell(shell_data)
                    if shell_id:
                        migration_results['shells'] += 1
        
        except Exception as e:
            migration_results['errors'].append(str(e))
        
        return migration_results
    
    def create_team_setup(self, character_name: str, shell_name: str, 
                         matrix_loadout: List[str], loadout_name: str = "Default") -> Dict:
        """Create a complete team setup for a character"""
        result = {
            'character': character_name,
            'shell_equipped': False,
            'matrix_loadout_set': False,
            'errors': []
        }
        
        # Equip shell
        if self.characters.equip_shell(character_name, shell_name):
            result['shell_equipped'] = True
        else:
            result['errors'].append(f"Failed to equip shell '{shell_name}'")
        
        # Set matrix loadout
        if self.characters.set_matrix_loadout(character_name, matrix_loadout, loadout_name):
            result['matrix_loadout_set'] = True
        else:
            result['errors'].append(f"Failed to set matrix loadout '{loadout_name}'")
        
        return result
    
    def get_character_complete_info(self, character_name: str) -> Optional[Dict]:
        """Get complete character information including equipped shell and matrix loadout"""
        character = self.characters.get_character_by_name(character_name)
        if not character:
            return None
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get equipped shell
            cursor.execute('''
                SELECT s.name, s.rarity, s.class, s.cooldown
                FROM characters c
                JOIN character_shell_equipment cse ON c.id = cse.character_id
                JOIN shells s ON cse.shell_id = s.id
                WHERE c.name = ? AND cse.is_active = 1
            ''', (character_name,))
            
            shell_result = cursor.fetchone()
            if shell_result:
                character['equipped_shell'] = dict(shell_result)
            
            # Get matrix loadouts
            cursor.execute('''
                SELECT me.name, cml.position, cml.loadout_name
                FROM characters c
                JOIN character_matrix_loadouts cml ON c.id = cml.character_id
                JOIN matrix_effects me ON cml.matrix_id = me.id
                WHERE c.name = ? AND cml.is_active = 1
                ORDER BY cml.loadout_name, cml.position
            ''', (character_name,))
            
            loadouts = {}
            for row in cursor.fetchall():
                loadout_name = row['loadout_name']
                if loadout_name not in loadouts:
                    loadouts[loadout_name] = []
                loadouts[loadout_name].append({
                    'matrix': row['name'],
                    'position': row['position']
                })
            
            if loadouts:
                character['matrix_loadouts'] = loadouts
        
        return character
    
    def export_unified_data(self, output_file: str = "etheria_unified_export.json") -> bool:
        """Export all data from unified database to JSON"""
        try:
            export_data = {
                'metadata': {
                    'database_stats': self.get_comprehensive_stats(),
                    'export_timestamp': self.db.execute_query('SELECT CURRENT_TIMESTAMP as ts')[0]['ts']
                },
                'characters': [],
                'shells': [],
                'matrix_effects': [],
                'relationships': {
                    'shell_matrix_compatibility': [],
                    'character_shell_equipment': [],
                    'character_matrix_loadouts': []
                }
            }
            
            # Export characters with complete info
            characters = self.characters.get_all_characters()
            for char_basic in characters:
                char_complete = self.get_character_complete_info(char_basic['name'])
                export_data['characters'].append(char_complete)
            
            # Export shells
            export_data['shells'] = self.shells.get_all_shells()
            
            # Export matrix effects
            export_data['matrix_effects'] = self.matrices.get_all_matrix_effects()
            
            # Export relationships
            export_data['relationships']['shell_matrix_compatibility'] = self.db.execute_query('''
                SELECT s.name as shell_name, me.name as matrix_name, smc.compatibility_score
                FROM shell_matrix_compatibility smc
                JOIN shells s ON smc.shell_id = s.id
                JOIN matrix_effects me ON smc.matrix_id = me.id
            ''')
            
            export_data['relationships']['character_shell_equipment'] = self.db.execute_query('''
                SELECT c.name as character_name, s.name as shell_name, cse.is_active, cse.equipped_at
                FROM character_shell_equipment cse
                JOIN characters c ON cse.character_id = c.id
                JOIN shells s ON cse.shell_id = s.id
            ''')
            
            export_data['relationships']['character_matrix_loadouts'] = self.db.execute_query('''
                SELECT c.name as character_name, me.name as matrix_name, 
                       cml.position, cml.loadout_name, cml.is_active
                FROM character_matrix_loadouts cml
                JOIN characters c ON cml.character_id = c.id
                JOIN matrix_effects me ON cml.matrix_id = me.id
            ''')
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"Unified data exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
