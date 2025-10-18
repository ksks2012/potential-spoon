from typing import Dict, List, Optional
from .unified_db import EtheriaDatabase


class MatrixManager:
    """Matrix effects management operations using unified database"""
    
    def __init__(self, db: EtheriaDatabase):
        self.db = db
    
    def insert_matrix_effect(self, matrix_data: Dict) -> Optional[int]:
        """Insert a matrix effect and return its ID"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert basic matrix info
                cursor.execute('''
                    INSERT OR REPLACE INTO matrix_effects (name, source, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (matrix_data['name'], matrix_data['source']))
                
                matrix_id = cursor.lastrowid or self._get_matrix_id(cursor, matrix_data['name'])
                
                if matrix_id is None:
                    return None
                
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
                        INSERT INTO matrix_effect_tiers 
                        (matrix_id, required_count, total_count, extra_effect)
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
                print(f"Matrix effect '{matrix_data['name']}' inserted successfully with ID: {matrix_id}")
                return matrix_id
                
        except Exception as e:
            print(f"Error inserting matrix effect: {e}")
            return None
    
    def _get_matrix_id(self, cursor, name: str) -> Optional[int]:
        """Get matrix ID by name"""
        cursor.execute('SELECT id FROM matrix_effects WHERE name = ?', (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_matrix_effect_by_name(self, name: str) -> Optional[Dict]:
        """Get a matrix effect by name with all its data"""
        with self.db.get_connection() as conn:
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
        with self.db.get_connection() as conn:
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
        with self.db.get_connection() as conn:
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
        with self.db.get_connection() as conn:
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
    
    def update_matrix_value(self, matrix_name: str, tier_required: int, tier_total: int, 
                           stat_name: str, new_value: str) -> bool:
        """Update a specific stat value for a matrix effect tier"""
        with self.db.get_connection() as conn:
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
                print(f"Matrix stat not found: {matrix_name} ({tier_required}/{tier_total}) {stat_name}")
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
            print(f"Updated {matrix_name} ({tier_required}/{tier_total}) {stat_name} = {new_value}")
            return True
    
    def get_matrix_usage_by_shells(self) -> Dict:
        """Get matrix usage statistics from shell compatibility"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Most used matrix effects by shells
            cursor.execute('''
                SELECT me.name, COUNT(*) as usage_count
                FROM matrix_effects me
                JOIN shell_matrix_compatibility smc ON me.id = smc.matrix_id
                GROUP BY me.name
                ORDER BY usage_count DESC
            ''')
            
            usage_stats = {}
            for row in cursor.fetchall():
                usage_stats[row['name']] = row['usage_count']
            
            return usage_stats
    
    def create_placeholder_matrix(self, name: str, source: str = "auto_generated") -> Optional[int]:
        """Create a placeholder matrix effect for missing references"""
        placeholder_data = {
            'name': name,
            'source': source,
            'type': ['Unknown'],
            'effects': [
                {
                    'required': 2,
                    'total': 4,
                    'effect': {
                        'placeholder': 'Effect data not available'
                    }
                },
                {
                    'required': 4,
                    'total': 4,
                    'effect': {
                        'placeholder': 'Full set effect not available'
                    }
                }
            ]
        }
        
        return self.insert_matrix_effect(placeholder_data)
