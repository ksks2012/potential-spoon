import os
import sys
from bs4 import BeautifulSoup
import re
import json

# Add parent directory to path to import db module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from db.matrix_db import MatrixDatabase


class MatrixEffectsParser:
    def __init__(self, html_file_path):
        """Initialize parser with HTML file path as parameter"""
        self.html_file = html_file_path
        self.soup = None
        self.matrix_effects = []
    
    def parse_effect_text(self, effect_text):
        """Parse effect text to extract stat bonuses and extra effects"""
        effect_data = {
            'effect': {},
            'extra_effect': ''
        }
        
        # Common stat patterns
        stat_patterns = [
            (r'ATK\s*\+(\d+)%', 'ATK'),
            (r'DEF\s*\+(\d+)%', 'DEF'),
            (r'HP\s*\+(\d+)%', 'HP'),
            (r'SPD\s*\+(\d+)%', 'SPD'),
            (r'CRIT Rate\s*\+(\d+)%', 'CRIT Rate'),
            (r'CRIT DMG\s*\+(\d+)%', 'CRIT DMG'),
            (r'Effect RES\s*\+(\d+)%', 'Effect RES'),
            (r'Effect ACC\s*\+(\d+)%', 'Effect ACC'),
            (r'Healing Effect\s*(?:increases by\s*)?(\d+)%', 'Healing Effect')
        ]
        
        # Extract stat bonuses
        remaining_text = effect_text
        for pattern, stat_name in stat_patterns:
            matches = re.findall(pattern, remaining_text, re.IGNORECASE)
            if matches:
                # Take the first match and convert to int
                effect_data['effect'][stat_name] = f"{matches[0]}%"
                # Remove the matched text from remaining text
                remaining_text = re.sub(pattern, '', remaining_text, flags=re.IGNORECASE)
        
        # Handle combined stats with &
        # Example: "DEF +25% & Effect RES +20%"
        if '&' in effect_text:
            parts = effect_text.split('&')
            for part in parts:
                part = part.strip()
                for pattern, stat_name in stat_patterns:
                    match = re.search(pattern, part, re.IGNORECASE)
                    if match:
                        effect_data['effect'][stat_name] = f"{match.group(1)}%"
        
        # Clean up remaining text for extra effects
        # Remove multiple spaces, leading/trailing dots and spaces
        remaining_text = re.sub(r'\s*&\s*', ' ', remaining_text)
        remaining_text = re.sub(r'^\.\s*', '', remaining_text)
        remaining_text = re.sub(r'\s+', ' ', remaining_text).strip()
        remaining_text = remaining_text.strip(' .')
        
        # If there's meaningful text left, it's an extra effect
        if remaining_text and len(remaining_text) > 10:  # Avoid very short meaningless text
            effect_data['extra_effect'] = remaining_text
        
        return effect_data
    
    def load_html(self):
        """Load the HTML file"""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as file:
                content = file.read()
                self.soup = BeautifulSoup(content, 'html.parser')
                print(f"HTML file loaded successfully")
        except Exception as e:
            print(f"Error loading HTML file: {e}")
            return False
        return True
    
    def extract_matrix_effects(self):
        """Extract all matrix effects from the HTML"""
        matrix_effects = []
        seen_names = set()  # To avoid duplicates
        
        try:
            # Find all matrix containers - use more specific selector to avoid duplicates
            matrix_containers = self.soup.find_all('div', class_='etheria-matrix-box box')
            
            for container in matrix_containers:
                matrix_data = {}
                
                # Extract matrix name
                name_element = container.find('h4')
                if name_element:
                    # Remove any span tags (like [INFERNO ONLY])
                    name_text = name_element.get_text().strip()
                    # Clean up the name by removing special indicators
                    matrix_data['name'] = re.sub(r'\s*\[.*?\]', '', name_text).strip()
                
                # Extract type and convert to list
                type_element = container.find('div', class_='etheria-matrix-info')
                if type_element:
                    type_p = type_element.find('p')
                    if type_p and 'Type:' in type_p.get_text():
                        type_strong = type_p.find('strong')
                        if type_strong:
                            type_text = type_strong.get_text().strip()
                            # Split by '/' and strip whitespace from each part
                            matrix_data['type'] = [t.strip() for t in type_text.split('/')]
                
                # Extract source
                source_element = container.find('div', class_='etheria-matrix-info')
                if source_element:
                    source_ps = source_element.find_all('p')
                    for p in source_ps:
                        if 'Source:' in p.get_text():
                            source_strong = p.find('strong')
                            if source_strong:
                                matrix_data['source'] = source_strong.get_text().strip()
                            break
                
                # Extract effects
                content_element = container.find('div', class_='etheria-matrix-content')
                if content_element:
                    effects = []
                    effect_ps = content_element.find_all('p')
                    
                    for p in effect_ps:
                        # Parse effect text to extract the matrix count and effect description
                        effect_text = p.get_text().strip()
                        
                        # Match patterns like "4/8: " or "12/12: "
                        match = re.match(r'(\d+)/(\d+):\s*(.+)', effect_text)
                        if match:
                            required_count = match.group(1)
                            total_count = match.group(2)
                            effect_desc = match.group(3)
                            
                            # Clean up the effect description
                            # Remove HTML entities and extra spaces
                            effect_desc = re.sub(r'&nbsp;', ' ', effect_desc)
                            effect_desc = re.sub(r'\s+', ' ', effect_desc).strip()
                            
                            # Parse the effect using the new parsing function
                            parsed_effect = self.parse_effect_text(effect_desc)
                            
                            effect_entry = {
                                'required': int(required_count),
                                'total': int(total_count),
                                'effect': parsed_effect['effect']
                            }
                            
                            # Only add extra_effect if it exists and is not empty
                            if parsed_effect['extra_effect']:
                                effect_entry['extra_effect'] = parsed_effect['extra_effect']
                            
                            effects.append(effect_entry)
                    
                    matrix_data['effects'] = effects
                
                # Only add if we have a name and haven't seen this matrix before
                if matrix_data.get('name') and matrix_data['name'] not in seen_names:
                    seen_names.add(matrix_data['name'])
                    matrix_effects.append(matrix_data)
        
        except Exception as e:
            print(f"Error extracting matrix effects: {e}")
            return []
        
        self.matrix_effects = matrix_effects
        return matrix_effects
    
    def save_to_database(self, db_path=None):
        """Save extracted data to SQLite database"""
        try:
            if db_path:
                db = MatrixDatabase(db_path)
            else:
                db = MatrixDatabase()
            
            # Clear existing data
            db.clear_all_data()
            print("Cleared existing matrix effects data")
            
            # Insert all matrix effects
            inserted_count = 0
            for matrix_data in self.matrix_effects:
                matrix_id = db.insert_matrix_effect(matrix_data)
                if matrix_id:
                    inserted_count += 1
                    print(f"Inserted: {matrix_data['name']} (ID: {matrix_id})")
            
            print(f"Matrix effects data saved to database: {inserted_count} effects inserted")
            return db
        except Exception as e:
            print(f"Error saving to database: {e}")
            return None
    
    def save_to_json(self, output_file):
        """Save extracted data to JSON file (backup option)"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.matrix_effects, f, indent=2, ensure_ascii=False)
            print(f"Matrix effects data also saved to {output_file}")
        except Exception as e:
            print(f"Error saving JSON backup: {e}")
    
    def print_matrix_effects(self):
        """Print all matrix effects in a formatted way"""
        for i, matrix in enumerate(self.matrix_effects, 1):
            print(f"\n{i}. Matrix Effect:")
            print(f"   Name: {matrix.get('name', 'Unknown')}")
            # Convert type list back to string for display
            type_list = matrix.get('type', ['Unknown'])
            print(f"   Type: {' / '.join(type_list)}")
            print(f"   Source: {matrix.get('source', 'Unknown')}")
            
            effects = matrix.get('effects', [])
            for effect in effects:
                # Display stat bonuses
                stat_parts = []
                for stat, value in effect['effect'].items():
                    stat_parts.append(f"{stat} +{value}")
                stats_str = ', '.join(stat_parts) if stat_parts else 'No stat bonuses'
                
                print(f"   {effect['required']}/{effect['total']}: {stats_str}")
                
                # Display extra effect if present
                if 'extra_effect' in effect:
                    print(f"      Extra: {effect['extra_effect']}")
    
    def parse(self):
        """Main parsing function"""
        if not self.load_html():
            return False
        
        self.extract_matrix_effects()
        return True


def main():
    # Default file path
    html_file = '/home/hong/code/python/etheria_sim/var/MatrixEffects.html'
    
    # Allow command line argument for file path
    if len(sys.argv) > 1:
        html_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(html_file):
        print(f"Error: File {html_file} not found")
        return
    
    # Create parser and parse
    parser = MatrixEffectsParser(html_file)
    
    if parser.parse():
        print(f"\nFound {len(parser.matrix_effects)} matrix effects:")
        parser.print_matrix_effects()
        
        # Save to database (primary storage)
        print("\n" + "="*50)
        print("Saving to database...")
        db = parser.save_to_database()
        
        # Save to JSON file as backup
        output_file = html_file.replace('.html', '_parsed.json')
        parser.save_to_json(output_file)
        
        # Show database statistics
        if db:
            print("\n" + "="*50)
            print("Database Statistics:")
            stats = db.get_stats_summary()
            print(f"Total matrices: {stats['total_count']}")
            
            print("\nBy Source:")
            for source, count in stats['source_counts'].items():
                print(f"  {source}: {count}")
            
            print("\nBy Type:")
            for type_name, count in stats['type_counts'].items():
                print(f"  {type_name}: {count}")
        
        # Show example format like requested
        print("\n" + "="*50)
        print("Example format (first matrix from database):")
        if db:
            all_matrices = db.get_all_matrix_effects()
            if all_matrices:
                matrix = all_matrices[0]
                print(f"- name: {matrix.get('name')}")
                # Display type as joined string for better readability
                type_list = matrix.get('type', [])
                print(f"- Type: {' / '.join(type_list)}")
                print(f"- Source: {matrix.get('source')}")
                for effect in matrix.get('effects', []):
                    print(f"- {effect['required']}/{effect['total']}:")
                    print(f"    effect: {effect['effect']}")
                    if 'extra_effect' in effect:
                        print(f"    extra_effect: {effect['extra_effect']}")


if __name__ == "__main__":
    main()
