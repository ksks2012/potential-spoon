import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager


class EtheriaDatabase:
    """Unified SQLite database handler for Etheria simulation system"""
    
    def __init__(self, db_path: str = "./db/etheria.db"):
        """Initialize unified database connection and create all tables"""
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_tables()
    
    def ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def init_tables(self):
        """Initialize all database tables with proper foreign key relationships"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # ============= CHARACTERS TABLES =============
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
            
            # ============= MATRIX EFFECTS TABLES =============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matrix_id INTEGER NOT NULL,
                    type_name TEXT NOT NULL,
                    FOREIGN KEY (matrix_id) REFERENCES matrix_effects (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_effect_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matrix_id INTEGER NOT NULL,
                    required_count INTEGER NOT NULL,
                    total_count INTEGER NOT NULL,
                    extra_effect TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (matrix_id) REFERENCES matrix_effects (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_effect_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tier_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY (tier_id) REFERENCES matrix_effect_tiers (id) ON DELETE CASCADE
                )
            ''')
            
            # ============= SHELLS TABLES =============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shells (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    rarity TEXT NOT NULL,
                    class TEXT NOT NULL,
                    cooldown TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    skill_type TEXT NOT NULL CHECK (skill_type IN ('awakened', 'non_awakened')),
                    skill_content TEXT NOT NULL,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE,
                    UNIQUE (shell_id, skill_type)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE,
                    UNIQUE (shell_id, stat_name)
                )
            ''')
            
            # ============= RELATIONSHIP TABLES =============
            # Shell-Matrix relationship (shells can use multiple matrix sets)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_matrix_compatibility (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    matrix_id INTEGER NOT NULL,
                    compatibility_score REAL DEFAULT 1.0, -- Future use for compatibility rating
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE,
                    FOREIGN KEY (matrix_id) REFERENCES matrix_effects (id) ON DELETE CASCADE,
                    UNIQUE (shell_id, matrix_id)
                )
            ''')
            
            # Character-Shell relationship (characters can equip shells)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_shell_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    shell_id INTEGER NOT NULL,
                    equipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE
                )
            ''')
            
            # Character-Matrix relationship (characters can have matrix loadouts)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS character_matrix_loadouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    matrix_id INTEGER NOT NULL,
                    position INTEGER NOT NULL, -- Matrix slot position
                    loadout_name TEXT DEFAULT 'Default',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
                    FOREIGN KEY (matrix_id) REFERENCES matrix_effects (id) ON DELETE CASCADE,
                    UNIQUE (character_id, matrix_id, position, loadout_name)
                )
            ''')
            
            # ============= COMMON LOOKUP TABLES =============
            # Rarity definitions (shared across all entities)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rarities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color_code TEXT,
                    sort_order INTEGER DEFAULT 0
                )
            ''')
            
            # Element types (for characters)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color_code TEXT,
                    description TEXT
                )
            ''')
            
            # Shell classes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            
            # Stat types (shared definitions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stat_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    description TEXT,
                    is_percentage BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # ============= INDEXES =============
            self._create_indexes(cursor)
            
            # ============= INITIAL DATA =============
            self._insert_initial_data(cursor)
            
            conn.commit()
            print("Unified database initialized successfully")
    
    def _create_indexes(self, cursor):
        """Create indexes for better performance"""
        indexes = [
            # Characters
            'CREATE INDEX IF NOT EXISTS idx_characters_name ON characters (name)',
            'CREATE INDEX IF NOT EXISTS idx_characters_rarity ON characters (rarity)',
            'CREATE INDEX IF NOT EXISTS idx_characters_element ON characters (element)',
            'CREATE INDEX IF NOT EXISTS idx_character_stats_character_id ON character_stats (character_id)',
            'CREATE INDEX IF NOT EXISTS idx_character_skills_character_id ON character_skills (character_id)',
            'CREATE INDEX IF NOT EXISTS idx_character_dupes_character_id ON character_dupes (character_id)',
            
            # Matrix Effects
            'CREATE INDEX IF NOT EXISTS idx_matrix_effects_name ON matrix_effects (name)',
            'CREATE INDEX IF NOT EXISTS idx_matrix_effects_source ON matrix_effects (source)',
            'CREATE INDEX IF NOT EXISTS idx_matrix_types_matrix_id ON matrix_types (matrix_id)',
            'CREATE INDEX IF NOT EXISTS idx_matrix_tiers_matrix_id ON matrix_effect_tiers (matrix_id)',
            'CREATE INDEX IF NOT EXISTS idx_matrix_stats_tier_id ON matrix_effect_stats (tier_id)',
            
            # Shells
            'CREATE INDEX IF NOT EXISTS idx_shells_name ON shells (name)',
            'CREATE INDEX IF NOT EXISTS idx_shells_rarity ON shells (rarity)',
            'CREATE INDEX IF NOT EXISTS idx_shells_class ON shells (class)',
            'CREATE INDEX IF NOT EXISTS idx_shell_skills_shell_id ON shell_skills (shell_id)',
            'CREATE INDEX IF NOT EXISTS idx_shell_stats_shell_id ON shell_stats (shell_id)',
            
            # Relationships
            'CREATE INDEX IF NOT EXISTS idx_shell_matrix_shell_id ON shell_matrix_compatibility (shell_id)',
            'CREATE INDEX IF NOT EXISTS idx_shell_matrix_matrix_id ON shell_matrix_compatibility (matrix_id)',
            'CREATE INDEX IF NOT EXISTS idx_char_shell_char_id ON character_shell_equipment (character_id)',
            'CREATE INDEX IF NOT EXISTS idx_char_shell_shell_id ON character_shell_equipment (shell_id)',
            'CREATE INDEX IF NOT EXISTS idx_char_matrix_char_id ON character_matrix_loadouts (character_id)',
            'CREATE INDEX IF NOT EXISTS idx_char_matrix_matrix_id ON character_matrix_loadouts (matrix_id)',
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _insert_initial_data(self, cursor):
        """Insert initial lookup data"""
        # Insert common rarities
        rarities = [
            ('N', '#808080', 0),
            ('R', '#00ff00', 1),
            ('SR', '#0080ff', 2),
            ('SSR', '#8000ff', 3),
            ('Legendary', '#ff8000', 4),
            ('Mythic', '#ff0080', 5)
        ]
        
        cursor.execute('SELECT COUNT(*) FROM rarities')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT OR IGNORE INTO rarities (name, color_code, sort_order)
                VALUES (?, ?, ?)
            ''', rarities)
        
        # Insert common elements
        elements = [
            ('Physical', '#ff4444', 'Physical damage type'),
            ('Volt', '#ffff44', 'Electrical damage type'),
            ('Ice', '#4488ff', 'Ice/Frost damage type'),
            ('Fire', '#ff8844', 'Fire/Heat damage type'),
            ('Altered', '#8844ff', 'Altered dimension damage type')
        ]
        
        cursor.execute('SELECT COUNT(*) FROM elements')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT OR IGNORE INTO elements (name, color_code, description)
                VALUES (?, ?, ?)
            ''', elements)
        
        # Insert shell classes
        shell_classes = [
            ('Tank', 'High defense and HP, protects team'),
            ('DPS', 'High damage output, eliminates enemies'),
            ('Support', 'Provides buffs and utility to team'),
            ('Healer', 'Restores HP and provides healing'),
            ('Striker', 'Balanced offense and utility'),
            ('Survivor', 'High survivability with defensive abilities'),
            ('Supporter', 'Team support and utility functions')
        ]
        
        cursor.execute('SELECT COUNT(*) FROM shell_classes')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT OR IGNORE INTO shell_classes (name, description)
                VALUES (?, ?)
            ''', shell_classes)
        
        # Insert common stat types
        stat_types = [
            ('HP', 'Health Points', 'Maximum health of the unit', False),
            ('ATK', 'Attack', 'Physical/elemental attack power', False),
            ('DEF', 'Defense', 'Physical damage resistance', False),
            ('SPD', 'Speed', 'Action speed and turn order', False),
            ('CRIT', 'Critical Rate', 'Chance to deal critical damage', True),
            ('CRIT_DMG', 'Critical Damage', 'Critical damage multiplier', True),
            ('Effect_RES', 'Effect Resistance', 'Resistance to debuffs', True),
            ('Effect_ACC', 'Effect Accuracy', 'Accuracy for applying effects', True)
        ]
        
        cursor.execute('SELECT COUNT(*) FROM stat_types')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT OR IGNORE INTO stat_types (name, display_name, description, is_percentage)
                VALUES (?, ?, ?, ?)
            ''', stat_types)
    
    def clear_all_data(self, confirm=False):
        """Clear all data from the database (requires confirmation)"""
        if not confirm:
            print("Warning: This will delete all data. Use clear_all_data(confirm=True) to proceed.")
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear relationship tables first (due to foreign key constraints)
            cursor.execute('DELETE FROM character_matrix_loadouts')
            cursor.execute('DELETE FROM character_shell_equipment')
            cursor.execute('DELETE FROM shell_matrix_compatibility')
            
            # Clear detail tables
            cursor.execute('DELETE FROM matrix_effect_stats')
            cursor.execute('DELETE FROM matrix_effect_tiers')
            cursor.execute('DELETE FROM matrix_types')
            cursor.execute('DELETE FROM shell_stats')
            cursor.execute('DELETE FROM shell_skills')
            cursor.execute('DELETE FROM character_dupes')
            cursor.execute('DELETE FROM character_skills')
            cursor.execute('DELETE FROM character_stats')
            
            # Clear main tables
            cursor.execute('DELETE FROM matrix_effects')
            cursor.execute('DELETE FROM shells')
            cursor.execute('DELETE FROM characters')
            
            conn.commit()
            print("All data cleared successfully")
            return True
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Entity counts
            tables = ['characters', 'shells', 'matrix_effects']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                stats[f'total_{table}'] = cursor.fetchone()['count']
            
            # Relationship counts
            cursor.execute('SELECT COUNT(*) as count FROM shell_matrix_compatibility')
            stats['shell_matrix_relationships'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM character_shell_equipment')
            stats['character_shell_equipment'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM character_matrix_loadouts')
            stats['character_matrix_loadouts'] = cursor.fetchone()['count']
            
            # Distribution stats
            cursor.execute('''
                SELECT rarity, COUNT(*) as count 
                FROM characters 
                GROUP BY rarity 
                ORDER BY count DESC
            ''')
            stats['characters_by_rarity'] = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT class, COUNT(*) as count 
                FROM shells 
                GROUP BY class 
                ORDER BY count DESC
            ''')
            stats['shells_by_class'] = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT source, COUNT(*) as count 
                FROM matrix_effects 
                GROUP BY source 
                ORDER BY count DESC
            ''')
            stats['matrix_by_source'] = dict(cursor.fetchall())
            
            return stats
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Execute a custom query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Convert rows to dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
