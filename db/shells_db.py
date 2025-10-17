import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple, Any


class ShellsDatabase:
    """SQLite database handler for Etheria Shells data"""
    
    def __init__(self, db_path: str = "./db/shells.db"):
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
        """Initialize all database tables for shells"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Shells basic info table
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
            
            # Shell skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    skill_type TEXT NOT NULL CHECK (skill_type IN ('awakened', 'non_awakened')),
                    skill_content TEXT NOT NULL,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE
                )
            ''')
            
            # Shell stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE
                )
            ''')
            
            # Shell matrix sets relationship table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shell_matrix_sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shell_id INTEGER NOT NULL,
                    matrix_set_name TEXT NOT NULL,
                    FOREIGN KEY (shell_id) REFERENCES shells (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shells_name ON shells (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shells_rarity ON shells (rarity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shells_class ON shells (class)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shell_skills_shell_id ON shell_skills (shell_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shell_stats_shell_id ON shell_stats (shell_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shell_matrix_sets_shell_id ON shell_matrix_sets (shell_id)')
            
            conn.commit()
    
    def clear_all_data(self):
        """Clear all shells data from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM shell_matrix_sets')
            cursor.execute('DELETE FROM shell_stats')
            cursor.execute('DELETE FROM shell_skills')
            cursor.execute('DELETE FROM shells')
            conn.commit()
    
    def insert_shell(self, shell_data: Dict) -> int:
        """Insert a shell and return its ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert basic shell info
            cursor.execute('''
                INSERT OR REPLACE INTO shells (name, rarity, class, cooldown)
                VALUES (?, ?, ?, ?)
            ''', (
                shell_data['name'], 
                shell_data['rarity'], 
                shell_data['class'],
                shell_data['cooldown']
            ))
            
            shell_id = cursor.lastrowid
            
            # Delete existing related data if updating
            cursor.execute('DELETE FROM shell_skills WHERE shell_id = ?', (shell_id,))
            cursor.execute('DELETE FROM shell_stats WHERE shell_id = ?', (shell_id,))
            cursor.execute('DELETE FROM shell_matrix_sets WHERE shell_id = ?', (shell_id,))
            
            # Insert skills
            skills = shell_data.get('skills', {})
            for skill_type, skill_content in skills.items():
                cursor.execute('''
                    INSERT INTO shell_skills (shell_id, skill_type, skill_content)
                    VALUES (?, ?, ?)
                ''', (shell_id, skill_type, skill_content))
            
            # Insert stats
            stats = shell_data.get('stats', {})
            for stat_name, stat_value in stats.items():
                cursor.execute('''
                    INSERT INTO shell_stats (shell_id, stat_name, stat_value)
                    VALUES (?, ?, ?)
                ''', (shell_id, stat_name, stat_value))
            
            # Insert matrix sets
            matrix_sets = shell_data.get('sets', [])
            for set_name in matrix_sets:
                cursor.execute('''
                    INSERT INTO shell_matrix_sets (shell_id, matrix_set_name)
                    VALUES (?, ?)
                ''', (shell_id, set_name))
            
            conn.commit()
            return shell_id
    
    def get_shell_by_name(self, name: str) -> Optional[Dict]:
        """Get a shell by name with all its data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get basic shell info
            cursor.execute('''
                SELECT id, name, rarity, class, cooldown, created_at, updated_at
                FROM shells
                WHERE name = ?
            ''', (name,))
            
            shell_row = cursor.fetchone()
            if not shell_row:
                return None
            
            shell_data = dict(shell_row)
            shell_id = shell_data['id']
            
            # Get skills
            cursor.execute('''
                SELECT skill_type, skill_content FROM shell_skills
                WHERE shell_id = ?
                ORDER BY skill_type
            ''', (shell_id,))
            
            skills = {}
            for skill_row in cursor.fetchall():
                skills[skill_row['skill_type']] = skill_row['skill_content']
            
            if skills:
                shell_data['skills'] = skills
            
            # Get stats
            cursor.execute('''
                SELECT stat_name, stat_value FROM shell_stats
                WHERE shell_id = ?
                ORDER BY stat_name
            ''', (shell_id,))
            
            stats = {}
            for stat_row in cursor.fetchall():
                stats[stat_row['stat_name']] = stat_row['stat_value']
            
            if stats:
                shell_data['stats'] = stats
            
            # Get matrix sets
            cursor.execute('''
                SELECT matrix_set_name FROM shell_matrix_sets
                WHERE shell_id = ?
                ORDER BY id
            ''', (shell_id,))
            
            matrix_sets = [row['matrix_set_name'] for row in cursor.fetchall()]
            if matrix_sets:
                shell_data['sets'] = matrix_sets
            
            return shell_data
    
    def get_all_shells(self) -> List[Dict]:
        """Get all shells with their data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM shells
                ORDER BY name
            ''')
            
            shells = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['name'])
                if shell_data:
                    shells.append(shell_data)
            
            return shells
    
    def get_shells_by_rarity(self, rarity: str) -> List[Dict]:
        """Get shells filtered by rarity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM shells
                WHERE rarity = ?
                ORDER BY name
            ''', (rarity,))
            
            shells = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['name'])
                if shell_data:
                    shells.append(shell_data)
            
            return shells
    
    def get_shells_by_class(self, shell_class: str) -> List[Dict]:
        """Get shells filtered by class"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM shells
                WHERE class = ?
                ORDER BY name
            ''', (shell_class,))
            
            shells = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['name'])
                if shell_data:
                    shells.append(shell_data)
            
            return shells
    
    def get_shells_by_matrix_set(self, matrix_set_name: str) -> List[Dict]:
        """Get shells that can use a specific matrix set"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT s.name
                FROM shells s
                JOIN shell_matrix_sets sms ON s.id = sms.shell_id
                WHERE sms.matrix_set_name = ?
                ORDER BY s.name
            ''', (matrix_set_name,))
            
            shells = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['name'])
                if shell_data:
                    shells.append(shell_data)
            
            return shells
    
    def get_stats_summary(self) -> Dict:
        """Get summary statistics about shells"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) as total FROM shells')
            total_count = cursor.fetchone()['total']
            
            # Count by rarity
            cursor.execute('''
                SELECT rarity, COUNT(*) as count
                FROM shells
                GROUP BY rarity
                ORDER BY count DESC
            ''')
            rarity_counts = {row['rarity']: row['count'] for row in cursor.fetchall()}
            
            # Count by class
            cursor.execute('''
                SELECT class, COUNT(*) as count
                FROM shells
                GROUP BY class
                ORDER BY count DESC
            ''')
            class_counts = {row['class']: row['count'] for row in cursor.fetchall()}
            
            # Most common matrix sets
            cursor.execute('''
                SELECT matrix_set_name, COUNT(*) as count
                FROM shell_matrix_sets
                GROUP BY matrix_set_name
                ORDER BY count DESC
                LIMIT 10
            ''')
            matrix_set_counts = {row['matrix_set_name']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_count': total_count,
                'rarity_counts': rarity_counts,
                'class_counts': class_counts,
                'matrix_set_counts': matrix_set_counts
            }
    
    def update_shell_stat(self, shell_name: str, stat_name: str, new_value: str) -> bool:
        """Update a specific stat value for a shell"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find the shell and stat
            cursor.execute('''
                SELECT ss.id
                FROM shells s
                JOIN shell_stats ss ON s.id = ss.shell_id
                WHERE s.name = ? AND ss.stat_name = ?
            ''', (shell_name, stat_name))
            
            stat_row = cursor.fetchone()
            if not stat_row:
                return False
            
            # Update the stat value
            cursor.execute('''
                UPDATE shell_stats
                SET stat_value = ?
                WHERE id = ?
            ''', (new_value, stat_row['id']))
            
            # Update shell updated_at timestamp
            cursor.execute('''
                UPDATE shells
                SET updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (shell_name,))
            
            conn.commit()
            return True
    
    def update_shell_skill(self, shell_name: str, skill_type: str, new_content: str) -> bool:
        """Update a specific skill for a shell"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find the shell and skill
            cursor.execute('''
                SELECT ss.id
                FROM shells s
                JOIN shell_skills ss ON s.id = ss.shell_id
                WHERE s.name = ? AND ss.skill_type = ?
            ''', (shell_name, skill_type))
            
            skill_row = cursor.fetchone()
            if not skill_row:
                return False
            
            # Update the skill content
            cursor.execute('''
                UPDATE shell_skills
                SET skill_content = ?
                WHERE id = ?
            ''', (new_content, skill_row['id']))
            
            # Update shell updated_at timestamp
            cursor.execute('''
                UPDATE shells
                SET updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            ''', (shell_name,))
            
            conn.commit()
            return True
