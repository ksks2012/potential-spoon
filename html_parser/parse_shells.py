import os
import sys
from bs4 import BeautifulSoup
import re
import json

# Add parent directory to path for database imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from db.etheria_manager import EtheriaManager
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database modules not available: {e}")
    print("Running in JSON-only mode")
    DATABASE_AVAILABLE = False


class ShellParser:
    def __init__(self, html_file_path, use_database=True, db_path="./db/etheria.db"):
        """Initialize parser with HTML file path as parameter"""
        self.html_file = html_file_path
        self.soup = None
        self.data = {}
        self.shells_data = []
        self.use_database = use_database and DATABASE_AVAILABLE
        
        if self.use_database:
            # Initialize unified database manager
            self.db_manager = EtheriaManager(db_path)
        else:
            self.db_manager = None
    
    def load_html(self):
        """Load the HTML file"""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as file:
                content = file.read()
                self.soup = BeautifulSoup(content, 'html.parser')
                print(f"HTML file loaded successfully: {self.html_file}")
        except Exception as e:
            print(f"Error loading HTML file: {e}")
            return False
        return True
    
    def extract_shell_basic_info(self, shell_element):
        """Extract basic info from a single shell element"""
        basic_info = {}
        
        try:
            # Extract name from h4 tag
            name_elem = shell_element.find('h4')
            basic_info['name'] = name_elem.get_text(strip=True) if name_elem else 'Unknown'
            
            # Extract rarity from strong tag with class "rarity"
            rarity_elem = shell_element.find('strong', class_=re.compile(r'rarity'))
            if rarity_elem:
                basic_info['rarity'] = rarity_elem.get_text(strip=True)
            else:
                basic_info['rarity'] = 'Unknown'
            
            # Extract class from the info section
            info_div = shell_element.find('div', class_='eth-shell-info')
            if info_div:
                class_p = info_div.find_all('p')[1] if len(info_div.find_all('p')) > 1 else None
                if class_p:
                    class_text = class_p.get_text(strip=True)
                    # Extract class after "Class: "
                    if 'Class:' in class_text:
                        basic_info['class'] = class_text.split('Class:')[1].strip()
                    else:
                        basic_info['class'] = 'Unknown'
                else:
                    basic_info['class'] = 'Unknown'
            else:
                basic_info['class'] = 'Unknown'
            
            # Extract cooldown from the info section
            if info_div:
                cooldown_p = info_div.find_all('p')[2] if len(info_div.find_all('p')) > 2 else None
                if cooldown_p:
                    cooldown_text = cooldown_p.get_text(strip=True)
                    # Extract cooldown after "Cooldown: "
                    if 'Cooldown:' in cooldown_text:
                        cooldown_value = cooldown_text.split('Cooldown:')[1].strip()
                        basic_info['cooldown'] = cooldown_value
                    else:
                        basic_info['cooldown'] = 'Unknown'
                else:
                    basic_info['cooldown'] = 'Unknown'
            else:
                basic_info['cooldown'] = 'Unknown'
                
        except Exception as e:
            print(f"Error extracting basic info for shell: {e}")
            basic_info = {
                'name': 'Unknown',
                'rarity': 'Unknown', 
                'class': 'Unknown',
                'cooldown': 'Unknown'
            }
        
        return basic_info
    
    def extract_shell_skills(self, shell_element):
        """Extract skill information from shell element"""
        skills = {}
        
        try:
            # Find the skill tab content
            skill_tab = shell_element.find('div', role='tabpanel', id=re.compile(r'.*-tabpane-skill'))
            if not skill_tab:
                return skills
            
            # Find all h5 elements (remove class filter)
            h5_elements = skill_tab.find_all('h5')
            
            for h5 in h5_elements:
                h5_text = h5.get_text(strip=True)
                
                # Check if this is non-awakened skill first (more specific)
                if 'Non-Awakened' in h5_text:
                    skill_div = h5.find_next_sibling('div', class_='skill-with-coloring')
                    if skill_div:
                        skills['non_awakened'] = skill_div.get_text(strip=True)
                
                # Check if this is awakened skill (less specific)
                elif 'Awakened' in h5_text:
                    skill_div = h5.find_next_sibling('div', class_='skill-with-coloring')
                    if skill_div:
                        skills['awakened'] = skill_div.get_text(strip=True)
                        
        except Exception as e:
            print(f"Error extracting skills for shell: {e}")
            
        return skills
    
    def extract_shell_stats(self, shell_element):
        """Extract stats from shell element"""
        stats = {}
        
        try:
            # Find stats content in the Stats tab
            stats_tabpane = shell_element.find('div', id=re.compile(r'.*-tabpane-stat'))
            if stats_tabpane:
                specialities_list = stats_tabpane.find('div', class_='specialities-list')
                if specialities_list:
                    stat_spans = specialities_list.find_all('span')
                    for span in stat_spans:
                        text = span.get_text(strip=True)
                        if ':' in text:
                            stat_name, stat_value = text.split(':', 1)
                            stats[stat_name.strip()] = stat_value.strip()
                            
        except Exception as e:
            print(f"Error extracting stats for shell: {e}")
            
        return stats
    
    def extract_matrix_sets(self, shell_element):
        """Extract matrix set information from shell element"""
        matrix_sets = []
        
        try:
            # Find sets container
            sets_div = shell_element.find('div', class_='eth-shell-sets')
            if sets_div:
                set_divs = sets_div.find_all('div', class_='single-set')
                for set_div in set_divs:
                    # Look for noscript tag which contains the real image source
                    noscript_elem = set_div.find('noscript')
                    if noscript_elem:
                        noscript_img = noscript_elem.find('img')
                        if noscript_img:
                            src = noscript_img.get('src', '')
                            if 'set_' in src:
                                # Extract set name from filename like "set_wellspring.webp"
                                set_name = src.split('set_')[-1].split('.webp')[0]
                                matrix_sets.append(set_name.capitalize())
                    
                    # Fallback: check regular img if noscript not found
                    if not noscript_elem:
                        img_elem = set_div.find('img')
                        if img_elem:
                            # Check data-lazy-src or other attributes
                            for attr in ['data-lazy-src', 'data-src', 'src']:
                                src = img_elem.get(attr, '')
                                if 'set_' in src:
                                    set_name = src.split('set_')[-1].split('.webp')[0]
                                    matrix_sets.append(set_name.capitalize())
                                    break
                            
        except Exception as e:
            print(f"Error extracting matrix sets for shell: {e}")
            
        return matrix_sets
    
    def parse_all_shells(self):
        """Parse all shells from the HTML"""
        if not self.soup:
            print("HTML not loaded. Call load_html() first.")
            return []
        
        # Find all shell elements
        shell_elements = self.soup.find_all('div', class_='single-shell')
        
        print(f"Found {len(shell_elements)} shell elements")
        
        for i, shell_element in enumerate(shell_elements):
            shell_data = {}
            
            # Extract basic info
            basic_info = self.extract_shell_basic_info(shell_element)
            shell_data.update(basic_info)
            
            # Extract skills
            skills = self.extract_shell_skills(shell_element)
            if skills:
                shell_data['skills'] = skills
            
            # Extract stats
            stats = self.extract_shell_stats(shell_element)
            if stats:
                shell_data['stats'] = stats
            
            # Extract matrix sets
            matrix_sets = self.extract_matrix_sets(shell_element)
            if matrix_sets:
                shell_data['sets'] = matrix_sets
            
            self.shells_data.append(shell_data)
            print(f"Processed shell {i+1}: {shell_data.get('name', 'Unknown')}")
        
        return self.shells_data
    
    def save_to_database(self, validate_matrix_refs=True):
        """Save parsed data to unified database
        
        Args:
            validate_matrix_refs: If True, validates that matrix references exist in database
        """
        if not self.use_database:
            print("Database mode not enabled")
            return False
        
        try:
            # Check if matrices exist in database
            stats = self.db_manager.get_comprehensive_stats()
            matrix_count = stats['database']['total_matrix_effects']
            
            if validate_matrix_refs and matrix_count == 0:
                print("⚠️  Warning: No matrix effects found in database. Matrix effects should be inserted first.")
            
            # Insert all shells using unified database
            inserted_count = 0
            failed_count = 0
            validation_warnings = 0
            
            for shell_data in self.shells_data:
                # Validate matrix set references if enabled
                if validate_matrix_refs and 'sets' in shell_data:
                    original_sets = shell_data['sets'][:]
                    validated_sets = []
                    
                    for matrix_name in original_sets:
                        matrix = self.db_manager.matrices.get_matrix_effect_by_name(matrix_name)
                        if matrix:
                            validated_sets.append(matrix_name)
                        else:
                            print(f"  ⚠️  Matrix reference not found in database: {matrix_name}")
                            validation_warnings += 1
                    
                    # Update shell data with validated matrix sets
                    shell_data['sets'] = validated_sets
                    
                    if len(validated_sets) != len(original_sets):
                        shell_name = shell_data.get('name', 'Unknown')
                        print(f"  📝 Shell '{shell_name}': {len(original_sets)} -> {len(validated_sets)} matrix references")
                
                # Insert shell into database
                shell_id = self.db_manager.shells.insert_shell(shell_data)
                if shell_id:
                    inserted_count += 1
                    shell_name = shell_data.get('name', 'Unknown')
                    matrix_count = len(shell_data.get('sets', []))
                    print(f"✅ Inserted shell: {shell_name} (ID: {shell_id}) with {matrix_count} matrix references")
                else:
                    failed_count += 1
                    print(f"❌ Failed to insert shell: {shell_data.get('name', 'Unknown')}")
            
            print(f"\n=== Shell Database Save Summary ===")
            print(f"Total shells saved to database: {inserted_count}")
            print(f"Failed insertions: {failed_count}")
            print(f"Matrix reference warnings: {validation_warnings}")
            
            # Show database statistics using unified manager
            stats = self.db_manager.get_comprehensive_stats()
            print(f"Database contains {stats['database']['total_shells']} shells")
            print(f"Shell-matrix relationships: {stats['database']['shell_matrix_relationships']}")
            
            return inserted_count > 0
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False
    
    def save_to_json(self, output_file=None):
        """Save parsed data to JSON file (legacy method)"""
        if not output_file:
            # Generate output filename based on input filename
            base_name = os.path.splitext(os.path.basename(self.html_file))[0]
            output_file = f"{base_name}_parsed.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.shells_data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to {output_file}")
            print(f"Total shells parsed: {len(self.shells_data)}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def create_missing_matrix_effects(self):
        """Create missing matrix effects based on shell references"""
        if not self.use_database:
            print("Database mode not enabled")
            return 0
        
        try:
            created_count = self.integrated_db.create_missing_matrix_effects("shells_parser")
            print(f"Created {created_count} missing matrix effects")
            return created_count
        except Exception as e:
            print(f"Error creating missing matrix effects: {e}")
            return 0
    
    def analyze_matrix_integration(self):
        """Analyze matrix integration with shells"""
        if not self.use_database:
            print("Database mode not enabled")
            return None
        
        try:
            analysis = self.integrated_db.get_matrix_usage_analysis()
            
            print(f"\n=== Matrix Integration Analysis ===")
            print(f"Total matrix sets referenced by shells: {analysis['total_matrix_sets_used']}")
            print(f"Total matrix effects available: {analysis['total_matrix_effects_available']}")
            print(f"Coverage percentage: {analysis['coverage_percentage']:.1f}%")
            
            if analysis['missing_matrix_effects']:
                print(f"\nMissing matrix effects ({len(analysis['missing_matrix_effects'])}):")
                for missing in analysis['missing_matrix_effects'][:10]:  # Show first 10
                    print(f"  - {missing}")
                if len(analysis['missing_matrix_effects']) > 10:
                    print(f"  ... and {len(analysis['missing_matrix_effects']) - 10} more")
            
            if analysis['unused_matrix_effects']:
                print(f"\nUnused matrix effects ({len(analysis['unused_matrix_effects'])}):")
                for unused in analysis['unused_matrix_effects'][:10]:  # Show first 10
                    print(f"  - {unused}")
                if len(analysis['unused_matrix_effects']) > 10:
                    print(f"  ... and {len(analysis['unused_matrix_effects']) - 10} more")
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing matrix integration: {e}")
            return None
    
    def print_summary(self):
        """Print a summary of parsed shells"""
        if not self.shells_data:
            print("No shell data available")
            return
        
        print(f"\n=== Shell Parser Summary ===")
        print(f"Total shells parsed: {len(self.shells_data)}")
        
        # Group by rarity
        rarity_count = {}
        class_count = {}
        
        for shell in self.shells_data:
            rarity = shell.get('rarity', 'Unknown')
            shell_class = shell.get('class', 'Unknown')
            
            rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
            class_count[shell_class] = class_count.get(shell_class, 0) + 1
        
        print(f"\nBy Rarity:")
        for rarity, count in rarity_count.items():
            print(f"  {rarity}: {count}")
        
        print(f"\nBy Class:")
        for shell_class, count in class_count.items():
            print(f"  {shell_class}: {count}")
        
        # Show first few examples
        print(f"\nFirst 3 shells:")
        for i, shell in enumerate(self.shells_data[:3]):
            print(f"  {i+1}. {shell.get('name', 'Unknown')} ({shell.get('rarity', 'Unknown')}, {shell.get('class', 'Unknown')})")


def main():
    """Main function to run the parser"""
    if len(sys.argv) < 2:
        print("Usage: python parse_shells.py <html_file_path> [--json-only]")
        print("Options:")
        print("  --json-only    Save to JSON only (skip database)")
        sys.exit(1)
    
    html_file = sys.argv[1]
    json_only = "--json-only" in sys.argv or not DATABASE_AVAILABLE
    
    if not DATABASE_AVAILABLE:
        print("Database modules not available, using JSON-only mode")
    
    if not os.path.exists(html_file):
        print(f"Error: HTML file '{html_file}' not found")
        sys.exit(1)
    
    # Create parser and process
    parser = ShellParser(html_file, use_database=not json_only)
    
    if not parser.load_html():
        print("Failed to load HTML file")
        sys.exit(1)
    
    # Parse all shells
    shells_data = parser.parse_all_shells()
    
    # Print summary
    parser.print_summary()
    
    if json_only or not DATABASE_AVAILABLE:
        # Save to JSON only
        parser.save_to_json()
    else:
        # Save to database (primary method)
        success = parser.save_to_database()
        
        if success:
            # Analyze matrix integration
            parser.analyze_matrix_integration()
            
            # Create missing matrix effects if needed
            parser.create_missing_matrix_effects()
            
            # Export combined data
            try:
                parser.integrated_db.export_combined_data()
            except Exception as e:
                print(f"Warning: Could not export combined data: {e}")
        
        # Also save JSON as backup
        parser.save_to_json()
    
    print("\nParsing completed successfully!")


if __name__ == "__main__":
    main()
