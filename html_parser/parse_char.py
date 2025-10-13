import os
import sys
from bs4 import BeautifulSoup
import re
import json


class CharacterParser:
    def __init__(self, html_file_path):
        """Initialize parser with HTML file path as parameter"""
        self.html_file = html_file_path
        self.soup = None
        self.data = {}
        self.character_data = {}
    
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
    
    def extract_basic_info(self):
        """Extract character name, rarity, and element"""
        basic_info = {}
        
        try:
            # Extract character name from breadcrumb or h1
            name_candidates = [
                self.soup.find('ul', class_='breadcrumb'),
                self.soup.find('h1'),
                self.soup.find('strong', class_='rarity-SSR')
            ]
            
            character_name = None
            for candidate in name_candidates:
                if candidate:
                    if candidate.name == 'ul':  # breadcrumb
                        last_li = candidate.find_all('li')[-1]
                        if last_li and not last_li.find('a'):  # last item without link
                            character_name = last_li.get_text(strip=True)
                            break
                    else:
                        text = candidate.get_text(strip=True)
                        if text and text not in ['SSR', 'Build and Guide']:
                            character_name = text.replace('Build and Guide', '').strip()
                            break
            
            basic_info['name'] = character_name or 'Unknown'
            
            # Extract rarity from CSS classes
            rarity_element = self.soup.find(class_=re.compile(r'rarity-(SSR|SR|R)'))
            if rarity_element:
                class_list = rarity_element.get('class', [])
                for cls in class_list:
                    if cls.startswith('rarity-'):
                        basic_info['rarity'] = cls.replace('rarity-', '')
                        break
            else:
                basic_info['rarity'] = 'Unknown'
            
            # Extract element from text or classes
            element_patterns = ['Disorder', 'Reason', 'Hollow', 'Odd', 'Constant']
            element_found = None
            
            # First try to find element in strong tags with specific classes
            for pattern in element_patterns:
                element_tag = self.soup.find('strong', class_=pattern)
                if element_tag:
                    element_found = pattern
                    break
            
            # If not found, search in text content
            if not element_found:
                text_content = self.soup.get_text()
                for pattern in element_patterns:
                    if pattern in text_content:
                        element_found = pattern
                        break
            
            basic_info['element'] = element_found or 'Unknown'
            
            print(f"Basic info extracted - Name: {basic_info['name']}, Rarity: {basic_info['rarity']}, Element: {basic_info['element']}")
            
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            basic_info = {'name': 'Unknown', 'rarity': 'Unknown', 'element': 'Unknown'}
        
        return basic_info
    
    def extract_base_stats(self):
        """Extract base character stats (HP, DEF, ATK, SPD, etc.)"""
        stats = {}
        
        # Find stats section in the HTML
        stats_sections = self.soup.find_all(['div'], class_=re.compile('stats|info-list-row'))
        
        # Extract stats from the structured data
        for section in stats_sections:
            # Look for category and details within each stat row
            category_elem = section.find(['div'], class_='category')
            details_elem = section.find(['div'], class_='details')
            
            if category_elem and details_elem:
                # Extract stat name
                stat_text = category_elem.get_text(strip=True)
                
                # Extract values from details
                bigger_value = details_elem.find(['p'], class_='bigger')
                smaller_value = details_elem.find(['p'], class_='smaller')
                
                if bigger_value and smaller_value:
                    total_value = bigger_value.get_text(strip=True)
                    breakdown_text = smaller_value.get_text(strip=True)
                    
                    # Parse breakdown format: "base + bonus"
                    base_value, bonus_value = self._parse_stat_breakdown(breakdown_text)
                    
                    # Store stat information
                    if 'HP' in stat_text:
                        stats['HP'] = {
                            'total': self._extract_number(total_value),
                            'base': base_value,
                            'bonus': bonus_value
                        }
                    elif 'DEF' in stat_text:
                        stats['DEF'] = {
                            'total': self._extract_number(total_value),
                            'base': base_value,
                            'bonus': bonus_value
                        }
                    elif 'ATK' in stat_text:
                        stats['ATK'] = {
                            'total': self._extract_number(total_value),
                            'base': base_value,
                            'bonus': bonus_value
                        }
                    elif 'SPD' in stat_text:
                        stats['SPD'] = {
                            'total': self._extract_number(total_value),
                            'base': base_value,
                            'bonus': bonus_value
                        }
                    elif 'CRIT Rate' in stat_text:
                        stats['CRIT Rate'] = {
                            'total': total_value,
                            'base': self._extract_percentage_breakdown(breakdown_text)[0],
                            'bonus': self._extract_percentage_breakdown(breakdown_text)[1]
                        }
                    elif 'CRIT DMG' in stat_text:
                        stats['CRIT DMG'] = {
                            'total': total_value,
                            'base': self._extract_percentage_breakdown(breakdown_text)[0],
                            'bonus': self._extract_percentage_breakdown(breakdown_text)[1]
                        }
                    elif 'Effect ACC' in stat_text:
                        stats['Effect ACC'] = {
                            'total': total_value,
                            'base': self._extract_percentage_breakdown(breakdown_text)[0],
                            'bonus': self._extract_percentage_breakdown(breakdown_text)[1]
                        }
                    elif 'Effect RES' in stat_text:
                        stats['Effect RES'] = {
                            'total': total_value,
                            'base': self._extract_percentage_breakdown(breakdown_text)[0],
                            'bonus': self._extract_percentage_breakdown(breakdown_text)[1]
                        }
        
        self.character_data['stats'] = stats
        return stats
    
    def _extract_number(self, text):
        """Extract numeric value from text"""
        if not text:
            return 0
        
        # Remove commas and extract digits
        numbers = re.findall(r'[\d,]+', str(text))
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0
    
    def _parse_stat_breakdown(self, breakdown_text):
        """Parse stat breakdown format: 'base + bonus'"""
        if not breakdown_text:
            return None, None
        
        # Look for pattern like "12669 + 5417"
        match = re.search(r'(\d+(?:,\d+)*)\s*\+\s*(\d+(?:,\d+)*)', breakdown_text)
        if match:
            base = int(match.group(1).replace(',', ''))
            bonus = int(match.group(2).replace(',', ''))
            return base, bonus
        
        # If no breakdown found, try to extract single value as base
        single_match = re.search(r'(\d+(?:,\d+)*)', breakdown_text)
        if single_match:
            base = int(single_match.group(1).replace(',', ''))
            return base, 0
        
        return None, None
    
    def _extract_percentage_breakdown(self, breakdown_text):
        """Parse percentage breakdown format: 'base% + bonus%'"""
        if not breakdown_text:
            return None, None
        
        # Look for pattern like "10% + 22%"
        match = re.search(r'(\d+(?:\.\d+)?)%\s*\+\s*(\d+(?:\.\d+)?)%', breakdown_text)
        if match:
            base = match.group(1) + '%'
            bonus = match.group(2) + '%'
            return base, bonus
        
        # If no breakdown found, try to extract single percentage as base
        single_match = re.search(r'(\d+(?:\.\d+)?)%', breakdown_text)
        if single_match:
            base = single_match.group(1) + '%'
            return base, '0%'
        
        return None, None
    
    def extract_skills(self):
        """Extract character skills information"""
        skills = []
        
        # Find skill boxes in the HTML - look specifically in skills section, not eidolons
        skills_section = self.soup.find(['div'], class_='skills')
        if not skills_section:
            self.character_data['skills'] = skills
            return skills
        
        skill_boxes = skills_section.find_all(['div'], class_='box')
        
        for skill_box in skill_boxes:
            # Check if this box contains skill information
            skill_header = skill_box.find(['div'], class_='skill-header')
            if skill_header:
                # Skip if this is a prowess/eidolon (has "with-border" class or P1-P5 in icon)
                if 'with-border' in skill_header.get('class', []):
                    continue
                
                skill_icon = skill_header.find(['div'], class_='skill-icon')
                if skill_icon:
                    icon_text = skill_icon.get_text(strip=True)
                    if icon_text.startswith('P') and icon_text[1:].isdigit():
                        continue  # Skip prowess skills
                
                skill_data = {}
                
                # Extract skill name from skill-info
                skill_info = skill_header.find(['div'], class_='skill-info')
                if skill_info:
                    name_elem = skill_info.find(['p'], class_='skill-name')
                    if name_elem:
                        skill_data['name'] = name_elem.get_text(strip=True)
                
                # Extract skill description/effect
                desc_elem = skill_box.find(['div'], class_='skill-description')
                if desc_elem:
                    # Get all paragraph text and clean it
                    paragraphs = desc_elem.find_all(['p'])
                    if paragraphs:
                        effect_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        # Clean HTML tags and normalize whitespace
                        effect_text = re.sub(r'<[^>]+>', '', effect_text)
                        effect_text = re.sub(r'\s+', ' ', effect_text).strip()
                        if effect_text:
                            skill_data['effect'] = effect_text
                
                # Extract cooldown and tags from additional-information
                add_info = skill_box.find(['div'], class_='additional-information')
                if add_info:
                    # Extract all p elements
                    paragraphs = add_info.find_all(['p'])
                    
                    for p in paragraphs:
                        p_text = p.get_text(strip=True)
                        
                        # Check for cooldown
                        if 'Cooldown:' in p_text:
                            span = p.find(['span'])
                            if span:
                                cooldown_text = span.get_text(strip=True)
                                if cooldown_text and cooldown_text != '-':
                                    try:
                                        skill_data['cooldown'] = int(cooldown_text)
                                    except ValueError:
                                        if cooldown_text == '0':
                                            skill_data['cooldown'] = 0
                        
                        # Check for tags
                        elif 'Tags:' in p_text:
                            span = p.find(['span'])
                            if span:
                                tags_text = span.get_text(strip=True)
                                if tags_text:
                                    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                                    if tags:
                                        skill_data['tags'] = tags
                
                # Only add skill if it has at least a name
                if skill_data.get('name'):
                    skills.append(skill_data)
        
        self.character_data['skills'] = skills
        return skills
    
    def extract_dupes(self):
        """Extract Prowess (P1-P5) information"""
        dupes = {}
        
        # Look for eidolons/prowess sections
        eidolon_sections = self.soup.find_all(['div'], class_='eidolons')
        
        for section in eidolon_sections:
            # Find all boxes within eidolons section
            boxes = section.find_all(['div'], class_='box')
            
            for box in boxes:
                # Get skill header
                skill_header = box.find(['div'], class_='skill-header')
                if skill_header:
                    # Extract prowess number from skill icon
                    skill_icon = skill_header.find(['div'], class_='skill-icon')
                    if skill_icon:
                        icon_text = skill_icon.get_text(strip=True)
                        if icon_text.startswith('P') and icon_text[1:].isdigit():
                            prowess_num = icon_text[1:]
                            
                            # Extract skill name
                            skill_info = skill_header.find(['div'], class_='skill-info')
                            skill_name = skill_info.find(['p'], class_='skill-name').get_text(strip=True) if skill_info else f'Prowess {prowess_num}'
                            
                            # Extract skill description
                            skill_desc = box.find(['div'], class_='skill-description')
                            effect = skill_desc.get_text(strip=True) if skill_desc else None
                            
                            # Clean up effect text
                            if effect:
                                effect = re.sub(r'<[^>]+>', '', effect)
                                effect = re.sub(r'\s+', ' ', effect).strip()
                            
                            dupes[f'P{prowess_num}'] = {
                                'name': skill_name,
                                'effect': effect
                            }
        

        
        self.character_data['dupes'] = dupes
        return dupes
    
    def parse_all(self):
        """Parse all character information"""
        if not self.load_html():
            return None
        
        print("Extracting basic info...")
        basic_info = self.extract_basic_info()
        self.character_data['basic_info'] = basic_info
            
        print("Extracting base stats...")
        self.extract_base_stats()
        
        print("Extracting skills...")
        self.extract_skills()
        
        print("Extracting dupes...")
        self.extract_dupes()
        
        return self.character_data
    
    def save_to_json(self, output_file):
        """Save parsed data to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.character_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def print_summary(self):
        """Print a formatted summary of parsed data"""
        print("\n" + "="*50)
        print("PLUME CHARACTER DATA SUMMARY")
        print("="*50)
        
        # Print basic info if available
        if 'basic_info' in self.character_data:
            print("\nBASIC INFO:")
            print("-" * 20)
            basic_info = self.character_data['basic_info']
            print(f"Name: {basic_info.get('name', 'Unknown')}")
            print(f"Rarity: {basic_info.get('rarity', 'Unknown')}")
            print(f"Element: {basic_info.get('element', 'Unknown')}")
        
        print("\nBASE STATS:")
        print("-" * 20)
        for stat, value in self.character_data['stats'].items():
            print(f"{stat}: {value if value is not None else 'Unknown'}")
        
        print("\nSKILLS:")
        print("-" * 20)
        if self.character_data.get('skills'):
            for i, skill_data in enumerate(self.character_data['skills'], 1):
                print(f"\nSkill {i}: {skill_data.get('name', 'Unknown')}")
                if 'effect' in skill_data:
                    print(f"  Effect: {skill_data['effect']}")
                if 'cooldown' in skill_data:
                    print(f"  Cooldown: {skill_data['cooldown']}")
                if 'tags' in skill_data:
                    print(f"  Tags: {', '.join(skill_data['tags'])}")
        else:
            print("No skills found")
        
        print("\nDUPES (PROWESS):")
        print("-" * 20)
        if self.character_data.get('dupes'):
            for dupe_id, dupe_data in self.character_data['dupes'].items():
                if isinstance(dupe_data, dict):
                    print(f"{dupe_id} - {dupe_data.get('name', 'Unknown')}: {dupe_data.get('effect', 'No effect description')}")
                else:
                    print(f"{dupe_id}: {dupe_data}")
        else:
            print("No prowess information found")


def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python parse_char.py <html_file_path>")
        print("Example: python parse_char.py ./var/Plume.html")
        return
    
    # Get HTML file path from command line argument
    html_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(html_file):
        print(f"Error: HTML file not found at {html_file}")
        return
    
    # Create parser instance with HTML file path
    parser = CharacterParser(html_file)
    
    # Parse the HTML file
    data = parser.parse_all()
    
    if data:
        # Print summary
        parser.print_summary()
        
        # Save to JSON file
        output_file = html_file.replace('.html', '_data.json')
        parser.save_to_json(output_file)
    else:
        print("Failed to parse HTML file")


if __name__ == "__main__":
    main()