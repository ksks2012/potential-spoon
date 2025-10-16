import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple, Any


class MatrixDatabase:
    """SQLite database handler for Etheria Matrix Effects data"""
    
    def __init__(self, db_path: str = "./db/matrix_effects.db"):
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
        """Initialize all database tables for matrix effects"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Matrix Effects basic info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Matrix types table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matrix_id INTEGER NOT NULL,
                    type_name TEXT NOT NULL,
                    FOREIGN KEY (matrix_id) REFERENCES matrix_effects (id) ON DELETE CASCADE
                )
            ''')
            
            # Matrix effect tiers table
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
            
            # Matrix effect stats table (stat bonuses for each tier)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix_effect_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tier_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY (tier_id) REFERENCES matrix_effect_tiers (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matrix_name ON matrix_effects (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matrix_source ON matrix_effects (source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matrix_types_matrix_id ON matrix_types (matrix_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tiers_matrix_id ON matrix_effect_tiers (matrix_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_tier_id ON matrix_effect_stats (tier_id)')
            
            conn.commit()
    
    def clear_all_data(self):
        """Clear all matrix effects data from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM matrix_effect_stats')
            cursor.execute('DELETE FROM matrix_effect_tiers')
            cursor.execute('DELETE FROM matrix_types')
            cursor.execute('DELETE FROM matrix_effects')
            conn.commit()
    
    def insert_matrix_effect(self, matrix_data: Dict) -> int:
        """Insert a matrix effect and return its ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert basic matrix info
            cursor.execute('''
                INSERT OR REPLACE INTO matrix_effects (name, source)
                VALUES (?, ?)
            ''', (matrix_data['name'], matrix_data['source']))
            
            matrix_id = cursor.lastrowid
            
            # Delete existing related data if updating
            cursor.execute('DELETE FROM matrix_types WHERE matrix_id = ?', (matrix_id,))
            cursor.execute('DELETE FROM matrix_effect_tiers WHERE matrix_id = ?', (matrix_id,))
            
            # Insert matrix types
            for type_name in matrix_data.get('type', []):
                cursor.execute('''
                    INSERT INTO matrix_types (matrix_id, type_name)
                    VALUES (?, ?)
                ''', (matrix_id, type_name))
            
            # Insert effect tiers and their stats
            for effect in matrix_data.get('effects', []):
                cursor.execute('''
                    INSERT INTO matrix_effect_tiers (matrix_id, required_count, total_count, extra_effect)
                    VALUES (?, ?, ?, ?)
                ''', (
                    matrix_id, 
                    effect['required'], 
                    effect['total'],
                    effect.get('extra_effect', None)
                ))
                
                tier_id = cursor.lastrowid
                
                # Insert stat bonuses for this tier
                for stat_name, stat_value in effect.get('effect', {}).items():
                    cursor.execute('''
                        INSERT INTO matrix_effect_stats (tier_id, stat_name, stat_value)
                        VALUES (?, ?, ?)
                    ''', (tier_id, stat_name, stat_value))
            
            conn.commit()
            return matrix_id
    
    def get_matrix_effect_by_name(self, name: str) -> Optional[Dict]:
        """Get a matrix effect by name with all its data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get basic matrix info
            cursor.execute('''
                SELECT id, name, source, created_at, updated_at
                FROM matrix_effects
                WHERE name = ?
            ''', (name,))
            
            matrix_row = cursor.fetchone()
            if not matrix_row:
                return None
            
            matrix_data = dict(matrix_row)
            matrix_id = matrix_data['id']
            
            # Get types
            cursor.execute('''
                SELECT type_name FROM matrix_types
                WHERE matrix_id = ?
                ORDER BY id
            ''', (matrix_id,))
            
            matrix_data['type'] = [row['type_name'] for row in cursor.fetchall()]
            
            # Get effect tiers with stats
            cursor.execute('''
                SELECT id, required_count, total_count, extra_effect
                FROM matrix_effect_tiers
                WHERE matrix_id = ?
                ORDER BY required_count, total_count
            ''', (matrix_id,))
            
            effects = []
            for tier_row in cursor.fetchall():
                tier_data = {
                    'required': tier_row['required_count'],
                    'total': tier_row['total_count'],
                    'effect': {}
                }
                
                if tier_row['extra_effect']:
                    tier_data['extra_effect'] = tier_row['extra_effect']
                
                # Get stats for this tier
                cursor.execute('''
                    SELECT stat_name, stat_value
                    FROM matrix_effect_stats
                    WHERE tier_id = ?
                    ORDER BY id
                ''', (tier_row['id'],))
                
                for stat_row in cursor.fetchall():
                    tier_data['effect'][stat_row['stat_name']] = stat_row['stat_value']
                
                effects.append(tier_data)
            
            matrix_data['effects'] = effects
            return matrix_data
    
    def get_all_matrix_effects(self) -> List[Dict]:
        """Get all matrix effects with their data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM matrix_effects
                ORDER BY name
            ''')
            
            matrix_effects = []
            for row in cursor.fetchall():
                matrix_data = self.get_matrix_effect_by_name(row['name'])
                if matrix_data:
                    matrix_effects.append(matrix_data)
            
            return matrix_effects
    
    def get_matrix_effects_by_source(self, source: str) -> List[Dict]:
        """Get matrix effects filtered by source"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM matrix_effects
                WHERE source = ?
                ORDER BY name
            ''', (source,))
            
            matrix_effects = []
            for row in cursor.fetchall():
                matrix_data = self.get_matrix_effect_by_name(row['name'])
                if matrix_data:
                    matrix_effects.append(matrix_data)
            
            return matrix_effects
    
    def get_matrix_effects_by_type(self, type_name: str) -> List[Dict]:
        """Get matrix effects filtered by type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT me.name
                FROM matrix_effects me
                JOIN matrix_types mt ON me.id = mt.matrix_id
                WHERE mt.type_name = ?
                ORDER BY me.name
            ''', (type_name,))
            
            matrix_effects = []
            for row in cursor.fetchall():
                matrix_data = self.get_matrix_effect_by_name(row['name'])
                if matrix_data:
                    matrix_effects.append(matrix_data)
            
            return matrix_effects
    
    def get_stats_summary(self) -> Dict:
        """Get summary statistics about matrix effects"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) as total FROM matrix_effects')
            total_count = cursor.fetchone()['total']
            
            # Count by source
            cursor.execute('''
                SELECT source, COUNT(*) as count
                FROM matrix_effects
                GROUP BY source
                ORDER BY count DESC
            ''')
            source_counts = {row['source']: row['count'] for row in cursor.fetchall()}
            
            # Count by type
            cursor.execute('''
                SELECT mt.type_name, COUNT(DISTINCT me.id) as count
                FROM matrix_effects me
                JOIN matrix_types mt ON me.id = mt.matrix_id
                GROUP BY mt.type_name
                ORDER BY count DESC
            ''')
            type_counts = {row['type_name']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_count': total_count,
                'source_counts': source_counts,
                'type_counts': type_counts
            }
    
    def update_matrix_value(self, matrix_name: str, tier_required: int, tier_total: int, 
                           stat_name: str, new_value: str) -> bool:
        """Update a specific stat value for a matrix effect tier"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find the matrix and tier
            cursor.execute('''
                SELECT mes.id
                FROM matrix_effects me
                JOIN matrix_effect_tiers met ON me.id = met.matrix_id
                JOIN matrix_effect_stats mes ON met.id = mes.tier_id
                WHERE me.name = ? AND met.required_count = ? AND met.total_count = ? AND mes.stat_name = ?
            ''', (matrix_name, tier_required, tier_total, stat_name))
            
            stat_row = cursor.fetchone()
            if not stat_row:
                return False
            
            # Update the stat value
            cursor.execute('''
                UPDATE matrix_effect_stats
                SET stat_value = ?
                WHERE id = ?
            ''', (new_value, stat_row['id']))
            
            # Update matrix updated_at timestamp
            cursor.execute('''
                UPDATE matrix_effects
                SET updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (matrix_name,))
            
            conn.commit()
            return True
