#!/usr/bin/env python3
"""
Database manager for Mathic System
Handles SQLite storage and retrieval of modules and loadouts
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import asdict


class MathicDatabase:
    """Database manager for mathic modules and loadouts"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables"""
        if db_path is None:
            # Default to mathic directory
            mathic_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(mathic_dir, "mathic_data.db")
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('PRAGMA foreign_keys = ON')
            
            # Create modules table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS modules (
                    module_id TEXT PRIMARY KEY,
                    module_type TEXT NOT NULL,
                    slot_position INTEGER NOT NULL,
                    level INTEGER DEFAULT 0,
                    main_stat TEXT NOT NULL,
                    main_stat_value REAL DEFAULT 0.0,
                    set_tag TEXT DEFAULT '',
                    matrix TEXT DEFAULT '',
                    matrix_count INTEGER DEFAULT 3,
                    total_enhancement_rolls INTEGER DEFAULT 0,
                    max_total_rolls INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create substats table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS substats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id TEXT NOT NULL,
                    stat_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    rolls_used INTEGER DEFAULT 0,
                    max_rolls INTEGER DEFAULT 5,
                    FOREIGN KEY (module_id) REFERENCES modules (module_id) ON DELETE CASCADE
                )
            ''')
            
            # Create loadouts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS loadouts (
                    loadout_name TEXT PRIMARY KEY,
                    description TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create loadout_slots table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS loadout_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loadout_name TEXT NOT NULL,
                    slot_position INTEGER NOT NULL,
                    module_id TEXT,
                    FOREIGN KEY (loadout_name) REFERENCES loadouts (loadout_name) ON DELETE CASCADE,
                    FOREIGN KEY (module_id) REFERENCES modules (module_id) ON DELETE SET NULL,
                    UNIQUE (loadout_name, slot_position)
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_modules_type ON modules (module_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_substats_module ON substats (module_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_loadout_slots_loadout ON loadout_slots (loadout_name)')
            
            conn.commit()
    
    def save_module(self, module) -> bool:
        """Save module to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert or update module
                conn.execute('''
                    INSERT OR REPLACE INTO modules (
                        module_id, module_type, slot_position, level, main_stat, main_stat_value,
                        set_tag, matrix, matrix_count, total_enhancement_rolls, max_total_rolls,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    module.module_id, module.module_type, module.slot_position, module.level,
                    module.main_stat, module.main_stat_value, module.set_tag, module.matrix,
                    module.matrix_count, module.total_enhancement_rolls, module.max_total_rolls
                ))
                
                # Delete existing substats
                conn.execute('DELETE FROM substats WHERE module_id = ?', (module.module_id,))
                
                # Insert substats
                for substat in module.substats:
                    conn.execute('''
                        INSERT INTO substats (module_id, stat_name, current_value, rolls_used, max_rolls)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        module.module_id, substat.stat_name, substat.current_value,
                        substat.rolls_used, substat.max_rolls
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving module {module.module_id}: {e}")
            return False
    
    def load_module(self, module_id: str):
        """Load module from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Load module data
                module_row = conn.execute(
                    'SELECT * FROM modules WHERE module_id = ?', 
                    (module_id,)
                ).fetchone()
                
                if not module_row:
                    return None
                
                # Load substats
                substat_rows = conn.execute(
                    'SELECT * FROM substats WHERE module_id = ? ORDER BY id',
                    (module_id,)
                ).fetchall()
                
                # Import here to avoid circular imports
                from mathic.mathic_system import Module, Substat
                
                # Create substats
                substats = []
                for row in substat_rows:
                    substat = Substat(
                        stat_name=row['stat_name'],
                        current_value=row['current_value'],
                        rolls_used=row['rolls_used'],
                        max_rolls=row['max_rolls']
                    )
                    substats.append(substat)
                
                # Create module
                module = Module(
                    module_id=module_row['module_id'],
                    module_type=module_row['module_type'],
                    slot_position=module_row['slot_position'],
                    level=module_row['level'],
                    main_stat=module_row['main_stat'],
                    main_stat_value=module_row['main_stat_value'],
                    substats=substats,
                    set_tag=module_row['set_tag'],
                    matrix=module_row['matrix'],
                    matrix_count=module_row['matrix_count'],
                    total_enhancement_rolls=module_row['total_enhancement_rolls'],
                    max_total_rolls=module_row['max_total_rolls']
                )
                
                return module
                
        except Exception as e:
            print(f"Error loading module {module_id}: {e}")
            return None
    
    def load_all_modules(self) -> Dict[str, Any]:
        """Load all modules from database"""
        modules = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get all module IDs
                module_ids = conn.execute('SELECT module_id FROM modules').fetchall()
                
                for row in module_ids:
                    module = self.load_module(row['module_id'])
                    if module:
                        modules[module.module_id] = module
                        
        except Exception as e:
            print(f"Error loading modules: {e}")
        
        return modules
    
    def delete_module(self, module_id: str) -> bool:
        """Delete module from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM modules WHERE module_id = ?', (module_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting module {module_id}: {e}")
            return False
    
    def save_loadout(self, loadout_name: str, loadout_data: Dict[int, str], description: str = '') -> bool:
        """Save loadout to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert or update loadout
                conn.execute('''
                    INSERT OR REPLACE INTO loadouts (loadout_name, description, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (loadout_name, description))
                
                # Delete existing slots
                conn.execute('DELETE FROM loadout_slots WHERE loadout_name = ?', (loadout_name,))
                
                # Insert slots
                for slot_position, module_id in loadout_data.items():
                    conn.execute('''
                        INSERT INTO loadout_slots (loadout_name, slot_position, module_id)
                        VALUES (?, ?, ?)
                    ''', (loadout_name, slot_position, module_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving loadout {loadout_name}: {e}")
            return False
    
    def load_loadout(self, loadout_name: str) -> Optional[Dict[int, str]]:
        """Load loadout from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Check if loadout exists
                loadout_row = conn.execute(
                    'SELECT * FROM loadouts WHERE loadout_name = ?',
                    (loadout_name,)
                ).fetchone()
                
                if not loadout_row:
                    return None
                
                # Load slots
                slot_rows = conn.execute(
                    'SELECT slot_position, module_id FROM loadout_slots WHERE loadout_name = ?',
                    (loadout_name,)
                ).fetchall()
                
                loadout_data = {}
                for row in slot_rows:
                    loadout_data[row['slot_position']] = row['module_id']
                
                return loadout_data
                
        except Exception as e:
            print(f"Error loading loadout {loadout_name}: {e}")
            return None
    
    def load_all_loadouts(self) -> Dict[str, Dict[int, str]]:
        """Load all loadouts from database"""
        loadouts = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get all loadout names
                loadout_rows = conn.execute('SELECT loadout_name FROM loadouts').fetchall()
                
                for row in loadout_rows:
                    loadout_data = self.load_loadout(row['loadout_name'])
                    if loadout_data is not None:
                        loadouts[row['loadout_name']] = loadout_data
                        
        except Exception as e:
            print(f"Error loading loadouts: {e}")
        
        return loadouts
    
    def delete_loadout(self, loadout_name: str) -> bool:
        """Delete loadout from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM loadouts WHERE loadout_name = ?', (loadout_name,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting loadout {loadout_name}: {e}")
            return False
    
    def get_loadout_names(self) -> List[str]:
        """Get all loadout names"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute('SELECT loadout_name FROM loadouts ORDER BY loadout_name').fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error getting loadout names: {e}")
            return []
    
    def get_module_count(self) -> int:
        """Get total number of modules"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute('SELECT COUNT(*) FROM modules').fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting module count: {e}")
            return 0
    
    def get_modules_by_type(self, module_type: str) -> List[str]:
        """Get module IDs by type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute(
                    'SELECT module_id FROM modules WHERE module_type = ? ORDER BY module_id',
                    (module_type,)
                ).fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"Error getting modules by type {module_type}: {e}")
            return []
