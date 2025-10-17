from typing import Dict, List, Optional
from .unified_db import EtheriaDatabase
import json


class ShellManager:
    """Shell management operations using unified database"""
    
    def __init__(self, db: EtheriaDatabase):
        self.db = db
    
    def insert_shell(self, shell_data: Dict) -> Optional[int]:
        """Insert a shell and return its ID"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert basic shell info
                cursor.execute('''
                    INSERT OR REPLACE INTO shells (name, rarity, class, cooldown, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    shell_data['name'], 
                    shell_data['rarity'], 
                    shell_data['class'],
                    shell_data['cooldown']
                ))
                
                shell_id = cursor.lastrowid or self._get_shell_id(cursor, shell_data['name'])
                
                if shell_id is None:
                    return None
                
                # Delete existing related data if updating
                cursor.execute('DELETE FROM shell_skills WHERE shell_id = ?', (shell_id,))
                cursor.execute('DELETE FROM shell_stats WHERE shell_id = ?', (shell_id,))
                cursor.execute('DELETE FROM shell_matrix_compatibility WHERE shell_id = ?', (shell_id,))
                
                # Insert skills
                skills = shell_data.get('skills', {})
                for skill_type, skill_content in skills.items():
                    cursor.execute('''
                        INSERT INTO shell_skills (shell_id, skill_type, skill_content)
                        VALUES (?, ?, ?)
                    ''', (shell_id, skill_type, json.dumps(skill_content, ensure_ascii=False)))
                
                # Insert stats
                stats = shell_data.get('stats', {})
                for stat_name, stat_value in stats.items():
                    cursor.execute('''
                        INSERT INTO shell_stats (shell_id, stat_name, stat_value)
                        VALUES (?, ?, ?)
                    ''', (shell_id, stat_name, stat_value))
                
                # Insert matrix compatibility
                matrix_sets = shell_data.get('sets', [])
                self._insert_matrix_compatibility(cursor, shell_id, matrix_sets)
                
                conn.commit()
                print(f"Shell '{shell_data['name']}' inserted successfully with ID: {shell_id}")
                return shell_id
                
        except Exception as e:
            print(f"Error inserting shell: {e}")
            return None
    
    def add_matrix_compatibility(self, shell_id: int, matrix_id: int, compatibility_score: float = 100.0) -> bool:
        """Add matrix compatibility for a shell"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO shell_matrix_compatibility 
                    (shell_id, matrix_id, compatibility_score)
                    VALUES (?, ?, ?)
                ''', (shell_id, matrix_id, compatibility_score))
                
                conn.commit()
                print(f"Matrix compatibility added: Shell {shell_id} <-> Matrix {matrix_id}")
                return True
                
        except Exception as e:
            print(f"Error adding matrix compatibility: {e}")
            return False
    
    def _get_shell_id(self, cursor, name: str) -> Optional[int]:
        """Get shell ID by name"""
        cursor.execute('SELECT id FROM shells WHERE name = ?', (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _insert_matrix_compatibility(self, cursor, shell_id: int, matrix_names: List[str]):
        """Insert shell-matrix compatibility relationships"""
        for matrix_name in matrix_names:
            # Find or create matrix effect
            cursor.execute('SELECT id FROM matrix_effects WHERE name = ?', (matrix_name,))
            matrix_result = cursor.fetchone()
            
            if matrix_result:
                matrix_id = matrix_result['id']
                cursor.execute('''
                    INSERT INTO shell_matrix_compatibility (shell_id, matrix_id, compatibility_score)
                    VALUES (?, ?, 1.0)
                ''', (shell_id, matrix_id))
            else:
                print(f"Warning: Matrix effect '{matrix_name}' not found, creating placeholder")
                # Create placeholder matrix effect
                from .matrix_manager import MatrixManager
                matrix_manager = MatrixManager(self.db)
                matrix_id = matrix_manager.create_placeholder_matrix(matrix_name, "shells_parser")
                
                if matrix_id:
                    cursor.execute('''
                        INSERT INTO shell_matrix_compatibility (shell_id, matrix_id, compatibility_score)
                        VALUES (?, ?, 1.0)
                    ''', (shell_id, matrix_id))
    
    def get_shell_by_name(self, name: str) -> Optional[Dict]:
        """Get a shell by name with all its data"""
        with self.db.get_connection() as conn:
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
            
            # Get compatible matrix effects
            cursor.execute('''
                SELECT me.name, smc.compatibility_score
                FROM matrix_effects me
                JOIN shell_matrix_compatibility smc ON me.id = smc.matrix_id
                WHERE smc.shell_id = ?
                ORDER BY smc.id
            ''', (shell_id,))
            
            matrix_sets = []
            matrix_compatibility = {}
            for matrix_row in cursor.fetchall():
                matrix_name = matrix_row['name']
                matrix_sets.append(matrix_name)
                matrix_compatibility[matrix_name] = matrix_row['compatibility_score']
            
            if matrix_sets:
                shell_data['sets'] = matrix_sets
                shell_data['matrix_compatibility'] = matrix_compatibility
            
            return shell_data
    
    def get_all_shells(self) -> List[Dict]:
        """Get all shells with their data"""
        with self.db.get_connection() as conn:
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
    
    def get_shells_by_class(self, shell_class: str) -> List[Dict]:
        """Get shells filtered by class"""
        with self.db.get_connection() as conn:
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
    
    def get_shells_by_matrix_effect(self, matrix_name: str) -> List[Dict]:
        """Get shells that are compatible with a specific matrix effect"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT s.name, smc.compatibility_score
                FROM shells s
                JOIN shell_matrix_compatibility smc ON s.id = smc.shell_id
                JOIN matrix_effects me ON smc.matrix_id = me.id
                WHERE me.name = ?
                ORDER BY smc.compatibility_score DESC, s.name
            ''', (matrix_name,))
            
            shells = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['name'])
                if shell_data:
                    shell_data['compatibility_with_matrix'] = row['compatibility_score']
                    shells.append(shell_data)
            
            return shells
    
    def update_shell_stat(self, shell_name: str, stat_name: str, new_value: str) -> bool:
        """Update a specific stat value for a shell"""
        with self.db.get_connection() as conn:
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
                print(f"Shell stat not found: {shell_name} {stat_name}")
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
            print(f"Updated {shell_name} {stat_name} = {new_value}")
            return True
    
    def update_shell_skill(self, shell_name: str, skill_type: str, new_content: str) -> bool:
        """Update a specific skill for a shell"""
        with self.db.get_connection() as conn:
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
                print(f"Shell skill not found: {shell_name} {skill_type}")
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
            print(f"Updated {shell_name} {skill_type} skill")
            return True
    
    def get_shell_recommendations(self, matrix_effects: List[str]) -> List[Dict]:
        """Get shell recommendations based on available matrix effects"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the query to find shells with compatible matrix effects
            placeholders = ','.join('?' * len(matrix_effects))
            
            cursor.execute(f'''
                SELECT 
                    s.name as shell_name,
                    COUNT(smc.matrix_id) as compatible_count,
                    (
                        SELECT COUNT(*) 
                        FROM shell_matrix_compatibility smc2 
                        WHERE smc2.shell_id = s.id
                    ) as total_matrix_count,
                    GROUP_CONCAT(me.name) as compatible_matrices
                FROM shells s
                JOIN shell_matrix_compatibility smc ON s.id = smc.shell_id
                JOIN matrix_effects me ON smc.matrix_id = me.id
                WHERE me.name IN ({placeholders})
                GROUP BY s.id, s.name
                ORDER BY 
                    (CAST(compatible_count AS FLOAT) / total_matrix_count) DESC,
                    compatible_count DESC,
                    s.name
            ''', matrix_effects)
            
            recommendations = []
            for row in cursor.fetchall():
                shell_data = self.get_shell_by_name(row['shell_name'])
                if shell_data:
                    compatibility_score = row['compatible_count'] / row['total_matrix_count']
                    
                    recommendation = {
                        'shell': shell_data,
                        'compatible_matrices': row['compatible_matrices'].split(','),
                        'compatible_count': row['compatible_count'],
                        'total_matrix_count': row['total_matrix_count'],
                        'compatibility_score': compatibility_score
                    }
                    recommendations.append(recommendation)
            
            return recommendations
