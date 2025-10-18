#!/usr/bin/env python3
"""
Unified parser manager for Etheria game data
Handles parsing and database storage in correct order
"""

import os
import sys

# Add parent directory to path for database imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.etheria_manager import EtheriaManager
from html_parser.parse_matrix import MatrixEffectsParser
from html_parser.parse_shells import ShellParser
from html_parser.parse_char import CharacterParser


class UnifiedParser:
    """Unified parser manager that handles data parsing and storage in correct order"""
    
    def __init__(self, db_path="./db/etheria.db"):
        """Initialize unified parser with database manager"""
        self.db_manager = EtheriaManager(db_path)
        self.matrix_parser = None
        self.shell_parser = None
        self.character_parsers = []  # Changed to list for multiple characters
        
        # Storage stats
        self.stats = {
            'matrices_inserted': 0,
            'shells_inserted': 0,
            'characters_inserted': 0,
            'total_errors': 0
        }
    
    def parse_matrix_effects(self, html_file_path):
        """Parse matrix effects from HTML file"""
        print("=== Step 1: Parsing Matrix Effects ===")
        
        try:
            self.matrix_parser = MatrixEffectsParser(html_file_path, use_database=False)
            self.matrix_parser.load_html()
            self.matrix_parser.parse()  # Use correct method name
            
            matrix_count = len(self.matrix_parser.matrix_effects)
            print(f"Parsed {matrix_count} matrix effects")
            return True
            
        except Exception as e:
            print(f"Error parsing matrix effects: {e}")
            self.stats['total_errors'] += 1
            return False
    
    def parse_shells(self, html_file_path):
        """Parse shells from HTML file"""
        print("\n=== Step 2: Parsing Shells ===")
        
        try:
            self.shell_parser = ShellParser(html_file_path, use_database=False)
            self.shell_parser.load_html()
            self.shell_parser.parse_all_shells()  # Use correct method name
            
            shell_count = len(self.shell_parser.shells_data)
            print(f"Parsed {shell_count} shells")
            return True
            
        except Exception as e:
            print(f"Error parsing shells: {e}")
            self.stats['total_errors'] += 1
            return False
    
    def parse_character(self, html_file_path):
        """Parse character from HTML file"""
        char_name = os.path.basename(html_file_path).replace('.html', '')
        print(f"=== Parsing Character: {char_name} ===")
        
        try:
            character_parser = CharacterParser(html_file_path, use_database=False)
            character_parser.load_html()
            character_parser.parse_all()  # Use correct method name
            
            # Store parser for later database insertion
            self.character_parsers.append(character_parser)
            
            parsed_char_name = character_parser.character_data.get('basic_info', {}).get('name', char_name)
            print(f"Parsed character: {parsed_char_name}")
            return True
            
        except Exception as e:
            print(f"Error parsing character {char_name}: {e}")
            self.stats['total_errors'] += 1
            return False
    
    def parse_multiple_characters(self, character_file_list):
        """Parse multiple character files"""
        print(f"\n=== Step 3: Parsing {len(character_file_list)} Characters ===")
        
        success_count = 0
        for char_file in character_file_list:
            if self.parse_character(char_file):
                success_count += 1
        
        print(f"Successfully parsed {success_count}/{len(character_file_list)} characters")
        return success_count > 0
    
    def store_to_database(self):
        """Store all parsed data to database in correct order"""
        print("\n" + "="*50)
        print("STORING DATA TO UNIFIED DATABASE")
        print("="*50)
        
        # Step 1: Store matrix effects first (no dependencies)
        if self.matrix_parser and self.matrix_parser.matrix_effects:
            print("\n=== Step 1: Storing Matrix Effects ===")
            
            for matrix_data in self.matrix_parser.matrix_effects:
                try:
                    matrix_id = self.db_manager.matrices.insert_matrix_effect(matrix_data)
                    if matrix_id:
                        self.stats['matrices_inserted'] += 1
                        print(f"✅ Inserted matrix: {matrix_data['name']} (ID: {matrix_id})")
                    else:
                        print(f"❌ Failed to insert matrix: {matrix_data['name']}")
                        self.stats['total_errors'] += 1
                        
                except Exception as e:
                    print(f"❌ Error inserting matrix {matrix_data.get('name', 'Unknown')}: {e}")
                    self.stats['total_errors'] += 1
        
        # Step 2: Store shells (depends on matrix effects for sets)
        if self.shell_parser and self.shell_parser.shells_data:
            print("\n=== Step 2: Storing Shells ===")
            
            for shell_data in self.shell_parser.shells_data:
                try:
                    # Validate matrix sets exist before inserting shell
                    matrix_sets = shell_data.get('sets', [])
                    valid_sets = []
                    
                    for matrix_name in matrix_sets:
                        matrix = self.db_manager.matrices.get_matrix_effect_by_name(matrix_name)
                        if matrix:
                            valid_sets.append(matrix_name)
                            print(f"  ✅ Matrix reference validated: {matrix_name}")
                        else:
                            print(f"  ⚠️  Matrix reference not found: {matrix_name}")
                    
                    # Update shell data with validated sets
                    shell_data['sets'] = valid_sets
                    
                    shell_id = self.db_manager.shells.insert_shell(shell_data)
                    if shell_id:
                        self.stats['shells_inserted'] += 1
                        shell_name = shell_data.get('name', 'Unknown')
                        print(f"✅ Inserted shell: {shell_name} (ID: {shell_id}) with {len(valid_sets)} matrix sets")
                    else:
                        print(f"❌ Failed to insert shell: {shell_data.get('name', 'Unknown')}")
                        self.stats['total_errors'] += 1
                        
                except Exception as e:
                    print(f"❌ Error inserting shell {shell_data.get('name', 'Unknown')}: {e}")
                    self.stats['total_errors'] += 1
        
        # Step 3: Store characters (no dependencies on shells/matrices for basic data)
        if self.character_parsers:
            print(f"\n=== Step 3: Storing {len(self.character_parsers)} Characters ===")
            
            for character_parser in self.character_parsers:
                try:
                    character_id = self.db_manager.characters.insert_character(character_parser.character_data)
                    if character_id:
                        self.stats['characters_inserted'] += 1
                        char_name = character_parser.character_data.get('basic_info', {}).get('name', 'Unknown')
                        print(f"✅ Inserted character: {char_name} (ID: {character_id})")
                    else:
                        char_name = character_parser.character_data.get('basic_info', {}).get('name', 'Unknown')
                        print(f"❌ Failed to insert character: {char_name}")
                        self.stats['total_errors'] += 1
                        
                except Exception as e:
                    char_name = character_parser.character_data.get('basic_info', {}).get('name', 'Unknown')
                    print(f"❌ Error inserting character {char_name}: {e}")
                    self.stats['total_errors'] += 1
    
    def print_final_summary(self):
        """Print final summary of parsing and storage operations"""
        print("\n" + "="*60)
        print("UNIFIED PARSING & STORAGE SUMMARY")
        print("="*60)
        
        # Storage statistics
        print(f"📊 Storage Results:")
        print(f"   Matrix Effects: {self.stats['matrices_inserted']} inserted")
        print(f"   Shells: {self.stats['shells_inserted']} inserted")
        print(f"   Characters: {self.stats['characters_inserted']} inserted")
        print(f"   Total Errors: {self.stats['total_errors']}")
        
        # Database statistics
        print(f"\n📈 Database Status:")
        try:
            db_stats = self.db_manager.get_comprehensive_stats()
            db_data = db_stats['database']
            print(f"   Total Matrix Effects: {db_data['total_matrix_effects']}")
            print(f"   Total Shells: {db_data['total_shells']}")
            print(f"   Total Characters: {db_data['total_characters']}")
            print(f"   Shell-Matrix Relationships: {db_data['shell_matrix_relationships']}")
            
            # Integration analysis
            integration = db_stats['integration']
            shell_matrix = integration['shell_matrix']
            print(f"\n🔗 Integration Analysis:")
            print(f"   Shell-Matrix Coverage: {shell_matrix['shell_coverage']:.1f}%")
            print(f"   Matrix Usage Rate: {shell_matrix['matrix_usage']:.1f}%")
            
        except Exception as e:
            print(f"   Error getting database statistics: {e}")
        
        # Success indicator
        total_inserted = sum([
            self.stats['matrices_inserted'],
            self.stats['shells_inserted'], 
            self.stats['characters_inserted']
        ])
        
        if total_inserted > 0 and self.stats['total_errors'] == 0:
            print(f"\n🎉 All operations completed successfully!")
        elif total_inserted > 0:
            print(f"\n⚠️  Operations completed with {self.stats['total_errors']} errors")
        else:
            print(f"\n❌ No data was successfully stored")
    
    def parse_and_store_all(self, matrix_html=None, shells_html=None, 
                           character_html=None, character_html_list=None):
        """Parse and store all data types in correct order
        
        Args:
            matrix_html: Path to matrix effects HTML file
            shells_html: Path to shells HTML file  
            character_html: Path to single character HTML file (legacy)
            character_html_list: List of character HTML file paths
        """
        success_count = 0
        
        # Parse matrix effects first
        if matrix_html:
            if self.parse_matrix_effects(matrix_html):
                success_count += 1
        
        # Parse shells second
        if shells_html:
            if self.parse_shells(shells_html):
                success_count += 1
        
        # Parse characters third - support both single and multiple characters
        if character_html_list:
            # Parse multiple characters
            if self.parse_multiple_characters(character_html_list):
                success_count += 1
        elif character_html:
            # Parse single character (legacy support)
            if self.parse_character(character_html):
                success_count += 1
        
        # Store all data to database in correct order
        if success_count > 0:
            self.store_to_database()
        
        # Print final summary
        self.print_final_summary()
        
        return success_count > 0


def main():
    """Example usage of unified parser"""
    # Initialize unified parser
    parser = UnifiedParser("./db/etheria_unified.db")
    
    # Example file paths (adjust as needed)
    matrix_file = "./var/MatrixEffects.html"
    shells_file = "./var/shells.html"
    character_file = "./var/character/Plume.html"
    
    # Check which files exist
    files_to_parse = {}
    if os.path.exists(matrix_file):
        files_to_parse['matrix'] = matrix_file
    if os.path.exists(shells_file):
        files_to_parse['shells'] = shells_file
    if os.path.exists(character_file):
        files_to_parse['character'] = character_file
    
    if not files_to_parse:
        print("No HTML files found to parse")
        return
    
    print("Starting unified parsing with available files:")
    for data_type, file_path in files_to_parse.items():
        print(f"  {data_type}: {file_path}")
    
    # Parse and store all available data
    parser.parse_and_store_all(
        matrix_html=files_to_parse.get('matrix'),
        shells_html=files_to_parse.get('shells'),
        character_html=files_to_parse.get('character')
    )


if __name__ == "__main__":
    main()
