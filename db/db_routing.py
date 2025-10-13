import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple, Any


class CharacterDatabase:
    """SQLite database handler for Etheria character data"""
    
    def __init__(self, db_path: str = "./db/characters.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_tables()
    
    def ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        """Initialize all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Characters basic info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    rarity TEXT NOT NULL,
                    element TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Character stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    total_value TEXT NOT NULL,
                    base_value TEXT NOT NULL,
                    bonus_value TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    UNIQUE (character_id, stat_name)
                )
            ''')
            
            # Character skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    skill_number INTEGER NOT NULL,
                    skill_name TEXT NOT NULL,
                    skill_effect TEXT,
                    cooldown TEXT,
                    tags TEXT, -- JSON array as string
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    UNIQUE (character_id, skill_number)
                )
            ''')
            
            # Character dupes/prowess table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_dupes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    dupe_id TEXT NOT NULL, -- P1, P2, etc.
                    dupe_name TEXT NOT NULL,
                    dupe_effect TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    UNIQUE (character_id, dupe_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_name ON characters (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_rarity ON characters (rarity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_element ON characters (element)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_character ON character_stats (character_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_character ON character_skills (character_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dupes_character ON character_dupes (character_id)')
            
            conn.commit()
            print("Database tables initialized successfully")
    
    def insert_character_data(self, character_data: Dict) -> Optional[int]:
        """Insert complete character data from parsed JSON"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic info
                basic_info = character_data.get('basic_info', {})
                name = basic_info.get('name', 'Unknown')
                rarity = basic_info.get('rarity', 'Unknown')
                element = basic_info.get('element', 'Unknown')
                
                # Insert or update character basic info
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (name, rarity, element, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, rarity, element))
                
                character_id = cursor.lastrowid
                
                # If character already existed, get the existing ID
                if character_id is None:
                    cursor.execute('SELECT id FROM characters WHERE name = ?', (name,))
                    result = cursor.fetchone()
                    character_id = result[0] if result else None
                
                if character_id is None:
                    print(f"Error: Could not get character ID for {name}")
                    return None
                
                # Insert stats
                stats = character_data.get('stats', {})
                self._insert_character_stats(cursor, character_id, stats)
                
                # Insert skills
                skills = character_data.get('skills', [])
                self._insert_character_skills(cursor, character_id, skills)
                
                # Insert dupes
                dupes = character_data.get('dupes', {})
                self._insert_character_dupes(cursor, character_id, dupes)
                
                conn.commit()
                print(f"Character '{name}' data inserted successfully with ID: {character_id}")
                return character_id
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def _insert_character_stats(self, cursor: sqlite3.Cursor, character_id: int, stats: Dict):
        """Insert character stats data"""
        # Clear existing stats
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
    
    def _insert_character_skills(self, cursor: sqlite3.Cursor, character_id: int, skills: List):
        """Insert character skills data"""
        # Clear existing skills
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
    
    def _insert_character_dupes(self, cursor: sqlite3.Cursor, character_id: int, dupes: Dict):
        """Insert character dupes/prowess data"""
        # Clear existing dupes
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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic info
                cursor.execute('SELECT * FROM characters WHERE name = ?', (name,))
                character_row = cursor.fetchone()
                
                if not character_row:
                    return None
                
                character_id = character_row['id']
                
                # Build character data dictionary
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
                cursor.execute('SELECT * FROM character_stats WHERE character_id = ? ORDER BY stat_name', 
                              (character_id,))
                for stat_row in cursor.fetchall():
                    character_data['stats'][stat_row['stat_name']] = {
                        'total': stat_row['total_value'],
                        'base': stat_row['base_value'],
                        'bonus': stat_row['bonus_value']
                    }
                
                # Get skills
                cursor.execute('SELECT * FROM character_skills WHERE character_id = ? ORDER BY skill_number', 
                              (character_id,))
                for skill_row in cursor.fetchall():
                    skill_data = {
                        'name': skill_row['skill_name'],
                        'effect': skill_row['skill_effect'],
                        'cooldown': skill_row['cooldown'],
                        'tags': json.loads(skill_row['tags'] or '[]')
                    }
                    character_data['skills'].append(skill_data)
                
                # Get dupes
                cursor.execute('SELECT * FROM character_dupes WHERE character_id = ? ORDER BY dupe_id', 
                              (character_id,))
                for dupe_row in cursor.fetchall():
                    character_data['dupes'][dupe_row['dupe_id']] = {
                        'name': dupe_row['dupe_name'],
                        'effect': dupe_row['dupe_effect']
                    }
                
                return character_data
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_all_characters(self) -> List[Dict]:
        """Get list of all characters with basic info"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM characters ORDER BY name')
                
                characters = []
                for row in cursor.fetchall():
                    characters.append({
                        'id': row['id'],
                        'name': row['name'],
                        'rarity': row['rarity'],
                        'element': row['element'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return characters
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def delete_character(self, name: str) -> bool:
        """Delete a character and all related data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM characters WHERE name = ?', (name,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Character '{name}' deleted successfully")
                    return True
                else:
                    print(f"Character '{name}' not found")
                    return False
                    
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def search_characters(self, **kwargs) -> List[Dict]:
        """Search characters by various criteria"""
        try:
            conditions = []
            params = []
            
            if 'rarity' in kwargs:
                conditions.append('rarity = ?')
                params.append(kwargs['rarity'])
            
            if 'element' in kwargs:
                conditions.append('element = ?')
                params.append(kwargs['element'])
            
            if 'name_like' in kwargs:
                conditions.append('name LIKE ?')
                params.append(f"%{kwargs['name_like']}%")
            
            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT * FROM characters WHERE {where_clause} ORDER BY name', params)
                
                characters = []
                for row in cursor.fetchall():
                    characters.append({
                        'id': row['id'],
                        'name': row['name'],
                        'rarity': row['rarity'],
                        'element': row['element'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return characters
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def import_from_json(self, json_file_path: str) -> bool:
        """Import character data from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            character_id = self.insert_character_data(character_data)
            return character_id is not None
            
        except FileNotFoundError:
            print(f"JSON file not found: {json_file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
            return False
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return False
    
    def export_to_json(self, character_name: str, output_file: str) -> bool:
        """Export character data to JSON file"""
        try:
            character_data = self.get_character_by_name(character_name)
            
            if not character_data:
                print(f"Character '{character_name}' not found")
                return False
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=2, ensure_ascii=False)
            
            print(f"Character '{character_name}' exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total characters
                cursor.execute('SELECT COUNT(*) as count FROM characters')
                stats['total_characters'] = cursor.fetchone()['count']
                
                # Characters by rarity
                cursor.execute('SELECT rarity, COUNT(*) as count FROM characters GROUP BY rarity')
                stats['by_rarity'] = {row['rarity']: row['count'] for row in cursor.fetchall()}
                
                # Characters by element
                cursor.execute('SELECT element, COUNT(*) as count FROM characters GROUP BY element')
                stats['by_element'] = {row['element']: row['count'] for row in cursor.fetchall()}
                
                return stats
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}


def main():
    """Test database operations"""
    # Initialize database
    db = CharacterDatabase()
    
    # Test importing from JSON
    json_file = './var/plume_data.json'
    if os.path.exists(json_file):
        print(f"Importing character data from {json_file}...")
        success = db.import_from_json(json_file)
        if success:
            print("Import successful!")
        else:
            print("Import failed!")
    
    # Show database stats
    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    stats = db.get_database_stats()
    print(f"Total Characters: {stats.get('total_characters', 0)}")
    
    if stats.get('by_rarity'):
        print("\nBy Rarity:")
        for rarity, count in stats['by_rarity'].items():
            print(f"  {rarity}: {count}")
    
    if stats.get('by_element'):
        print("\nBy Element:")
        for element, count in stats['by_element'].items():
            print(f"  {element}: {count}")
    
    # List all characters
    print("\n" + "="*50)
    print("ALL CHARACTERS")
    print("="*50)
    characters = db.get_all_characters()
    for char in characters:
        print(f"  {char['name']} ({char['rarity']}) - {char['element']} element")


if __name__ == "__main__":
    main()
