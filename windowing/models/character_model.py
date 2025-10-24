#!/usr/bin/env python3
"""
Character Model for the Etheria Simulation Suite
"""

import sys
import os
import json
from typing import Dict, List, Optional, Tuple, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from db.etheria_manager import EtheriaManager
from html_parser.parse_char import CharacterParser
from .base_model import BaseModel


class CharacterModel(BaseModel):
    """Model for character data management using unified database"""
    
    def __init__(self):
        super().__init__()
        self.manager = EtheriaManager()
        self._characters = []
        self._selected_character = None
        
    def initialize(self):
        """Initialize the character model"""
        self._characters = self.get_all_characters()
        
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
                return True, f"Successfully imported character: {char_name}"
            else:
                return False, "Failed to save character to database"
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
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, ensure_ascii=False, indent=2)
                return True, f"Successfully exported {character_name}"
            else:
                return False, f"Character {character_name} not found"
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
