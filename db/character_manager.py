import json
from typing import Dict, List, Optional
from .unified_db import EtheriaDatabase


class CharacterManager:
    """Character management operations using unified database"""
    
    def __init__(self, db: EtheriaDatabase):
        self.db = db
    
    def insert_character(self, character_data: Dict) -> Optional[int]:
        """Insert complete character data"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                basic_info = character_data.get('basic_info', {})
                name = basic_info.get('name', 'Unknown')
                rarity = basic_info.get('rarity', 'Unknown')
                element = basic_info.get('element', 'Unknown')
                
                # Insert character basic info
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (name, rarity, element, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, rarity, element))
                
                character_id = cursor.lastrowid or self._get_character_id(cursor, name)
                
                if character_id is None:
                    return None
                
                # Insert stats
                self._insert_character_stats(cursor, character_id, character_data.get('stats', {}))
                
                # Insert skills
                self._insert_character_skills(cursor, character_id, character_data.get('skills', []))
                
                # Insert dupes
                self._insert_character_dupes(cursor, character_id, character_data.get('dupes', {}))
                
                conn.commit()
                print(f"Character '{name}' inserted successfully with ID: {character_id}")
                return character_id
                
        except Exception as e:
            print(f"Error inserting character: {e}")
            return None
    
    def _get_character_id(self, cursor, name: str) -> Optional[int]:
        """Get character ID by name"""
        cursor.execute('SELECT id FROM characters WHERE name = ?', (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _insert_character_stats(self, cursor, character_id: int, stats: Dict):
        """Insert character stats"""
        cursor.execute('DELETE FROM character_stats WHERE character_id = ?', (character_id,))
        
        for stat_name, stat_data in stats.items():
            if isinstance(stat_data, dict):
                total_val = str(stat_data.get('total', ''))
                base_val = str(stat_data.get('base', ''))
                bonus_val = str(stat_data.get('bonus', ''))
            else:
                total_val = str(stat_data)
                base_val = ''
                bonus_val = ''
            
            cursor.execute('''
                INSERT INTO character_stats 
                (character_id, stat_name, total_value, base_value, bonus_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (character_id, stat_name, total_val, base_val, bonus_val))
    
    def _insert_character_skills(self, cursor, character_id: int, skills: List):
        """Insert character skills"""
        cursor.execute('DELETE FROM character_skills WHERE character_id = ?', (character_id,))
        
        for idx, skill_data in enumerate(skills, 1):
            skill_name = skill_data.get('name', f'Skill {idx}')
            skill_effect = skill_data.get('effect', '')
            cooldown = skill_data.get('cooldown', '')
            tags = json.dumps(skill_data.get('tags', []))
            
            cursor.execute('''
                INSERT INTO character_skills 
                (character_id, skill_number, skill_name, skill_effect, cooldown, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (character_id, idx, skill_name, skill_effect, cooldown, tags))
    
    def _insert_character_dupes(self, cursor, character_id: int, dupes: Dict):
        """Insert character dupes"""
        cursor.execute('DELETE FROM character_dupes WHERE character_id = ?', (character_id,))
        
        for dupe_id, dupe_data in dupes.items():
            if isinstance(dupe_data, dict):
                dupe_name = dupe_data.get('name', dupe_id)
                dupe_effect = dupe_data.get('effect', '')
            else:
                dupe_name = dupe_id
                dupe_effect = str(dupe_data)
            
            cursor.execute('''
                INSERT INTO character_dupes 
                (character_id, dupe_id, dupe_name, dupe_effect)
                VALUES (?, ?, ?, ?)
            ''', (character_id, dupe_id, dupe_name, dupe_effect))
    
    def get_character_by_name(self, name: str) -> Optional[Dict]:
        """Get complete character data by name"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM characters WHERE name = ?', (name,))
            character_row = cursor.fetchone()
            
            if not character_row:
                return None
            
            character_id = character_row['id']
            
            character_data = {
                'basic_info': {
                    'name': character_row['name'],
                    'rarity': character_row['rarity'],
                    'element': character_row['element']
                },
                'stats': {},
                'skills': [],
                'dupes': {}
            }
            
            # Get stats
            cursor.execute('''
                SELECT * FROM character_stats 
                WHERE character_id = ? 
                ORDER BY stat_name
            ''', (character_id,))
            
            for stat_row in cursor.fetchall():
                character_data['stats'][stat_row['stat_name']] = {
                    'total': stat_row['total_value'],
                    'base': stat_row['base_value'],
                    'bonus': stat_row['bonus_value']
                }
            
            # Get skills
            cursor.execute('''
                SELECT * FROM character_skills 
                WHERE character_id = ? 
                ORDER BY skill_number
            ''', (character_id,))
            
            for skill_row in cursor.fetchall():
                skill_data = {
                    'name': skill_row['skill_name'],
                    'effect': skill_row['skill_effect'],
                    'cooldown': skill_row['cooldown'],
                    'tags': json.loads(skill_row['tags'] or '[]')
                }
                character_data['skills'].append(skill_data)
            
            # Get dupes
            cursor.execute('''
                SELECT * FROM character_dupes 
                WHERE character_id = ? 
                ORDER BY dupe_id
            ''', (character_id,))
            
            for dupe_row in cursor.fetchall():
                character_data['dupes'][dupe_row['dupe_id']] = {
                    'name': dupe_row['dupe_name'],
                    'effect': dupe_row['dupe_effect']
                }
            
            return character_data
    
    def get_all_characters(self) -> List[Dict]:
        """Get list of all characters with basic info"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM characters ORDER BY name')
            
            characters = []
            for row in cursor.fetchall():
                characters.append(dict(row))
            
            return characters
    
    def equip_shell(self, character_name: str, shell_name: str) -> bool:
        """Equip a shell to a character"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get character and shell IDs
            cursor.execute('SELECT id FROM characters WHERE name = ?', (character_name,))
            char_result = cursor.fetchone()
            if not char_result:
                print(f"Character '{character_name}' not found")
                return False
            
            cursor.execute('SELECT id FROM shells WHERE name = ?', (shell_name,))
            shell_result = cursor.fetchone()
            if not shell_result:
                print(f"Shell '{shell_name}' not found")
                return False
            
            character_id = char_result['id']
            shell_id = shell_result['id']
            
            # Deactivate current shell equipment
            cursor.execute('''
                UPDATE character_shell_equipment 
                SET is_active = FALSE 
                WHERE character_id = ?
            ''', (character_id,))
            
            # Equip new shell
            cursor.execute('''
                INSERT OR REPLACE INTO character_shell_equipment 
                (character_id, shell_id, is_active)
                VALUES (?, ?, TRUE)
            ''', (character_id, shell_id))
            
            conn.commit()
            print(f"Equipped shell '{shell_name}' to character '{character_name}'")
            return True
    
    def set_matrix_loadout(self, character_name: str, matrix_names: List[str], 
                          loadout_name: str = 'Default') -> bool:
        """Set matrix loadout for a character"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get character ID
            cursor.execute('SELECT id FROM characters WHERE name = ?', (character_name,))
            char_result = cursor.fetchone()
            if not char_result:
                print(f"Character '{character_name}' not found")
                return False
            
            character_id = char_result['id']
            
            # Clear existing loadout
            cursor.execute('''
                DELETE FROM character_matrix_loadouts 
                WHERE character_id = ? AND loadout_name = ?
            ''', (character_id, loadout_name))
            
            # Add new matrix loadout
            for position, matrix_name in enumerate(matrix_names):
                cursor.execute('SELECT id FROM matrix_effects WHERE name = ?', (matrix_name,))
                matrix_result = cursor.fetchone()
                
                if matrix_result:
                    matrix_id = matrix_result['id']
                    cursor.execute('''
                        INSERT INTO character_matrix_loadouts 
                        (character_id, matrix_id, position, loadout_name)
                        VALUES (?, ?, ?, ?)
                    ''', (character_id, matrix_id, position, loadout_name))
                else:
                    print(f"Warning: Matrix '{matrix_name}' not found")
            
            conn.commit()
            print(f"Set matrix loadout '{loadout_name}' for character '{character_name}'")
            return True
