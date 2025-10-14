import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_routing import CharacterDatabase
from html_parser.parse_char import CharacterParser
from mathic.mathic_system import MathicSystem


class CharacterPokedexUI:
    """Character Pokedex GUI using tkinter"""
    
    def __init__(self, root):
        """Initialize the UI"""
        self.root = root
        self.root.title("Etheria Simulation Suite")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db = CharacterDatabase()
        
        # Initialize mathic system
        self.mathic_system = MathicSystem()
        
        # Create UI components
        self.create_widgets()
        self.refresh_character_list()
        
        # Bind events
        self.setup_events()
    
    def create_widgets(self):
        """Create and layout UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Main notebook for top-level tabs
        self.main_notebook = ttk.Notebook(main_frame)
        self.main_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Character Pokedex tab
        self.create_character_tab()
        
        # Create Mathic System tab  
        self.create_mathic_tab()
        
        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_character_tab(self):
        """Create the Character Pokedex tab"""
        # Character tab frame
        char_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(char_frame, text="Character Pokedex")
        
        # Configure grid weights for character frame
        char_frame.columnconfigure(1, weight=1)
        char_frame.rowconfigure(0, weight=1)
        
        # Left panel - Character list
        left_frame = ttk.LabelFrame(char_frame, text="Character List", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        
        # Search and filter controls
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_characters)
        search_btn.grid(row=0, column=2)
        
        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        ttk.Label(filter_frame, text="Rarity:").grid(row=0, column=0, padx=(0, 5))
        self.rarity_var = tk.StringVar(value="All")
        rarity_combo = ttk.Combobox(filter_frame, textvariable=self.rarity_var, 
                                   values=["All", "SSR", "SR", "R"], state="readonly", width=8)
        rarity_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(filter_frame, text="Element:").grid(row=0, column=2, padx=(0, 5))
        self.element_var = tk.StringVar(value="All")
        element_combo = ttk.Combobox(filter_frame, textvariable=self.element_var,
                                    values=["All", "Disorder", "Reason", "Hollow", "Odd", "Constant"],
                                    state="readonly", width=10)
        element_combo.grid(row=0, column=3)
        
        # Character listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for character list
        columns = ('Name', 'Rarity', 'Element', 'Updated')
        self.character_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define column headings and widths
        self.character_tree.heading('Name', text='Name')
        self.character_tree.heading('Rarity', text='Rarity')
        self.character_tree.heading('Element', text='Element')
        self.character_tree.heading('Updated', text='Last Updated')
        
        self.character_tree.column('Name', width=120)
        self.character_tree.column('Rarity', width=60)
        self.character_tree.column('Element', width=80)
        self.character_tree.column('Updated', width=100)
        
        self.character_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.character_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.character_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.character_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.character_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Right panel - Character details
        right_frame = ttk.LabelFrame(char_frame, text="Character Details", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Character info frame
        info_frame = ttk.Frame(right_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.char_name_label = ttk.Label(info_frame, text="Select a character", 
                                        font=('Arial', 12, 'bold'))
        self.char_name_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(info_frame, text="Rarity:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.rarity_label = ttk.Label(info_frame, text="-")
        self.rarity_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(info_frame, text="Element:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.element_label = ttk.Label(info_frame, text="-")
        self.element_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Notebook for detailed information
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Stats tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Stats")
        
        # Create stats text widget with scrollbar
        stats_text_frame = ttk.Frame(self.stats_frame)
        stats_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_text_frame.columnconfigure(0, weight=1)
        stats_text_frame.rowconfigure(0, weight=1)
        
        self.stats_text = tk.Text(stats_text_frame, wrap=tk.WORD, height=15, width=40)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_scrollbar = ttk.Scrollbar(stats_text_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        # Skills tab
        self.skills_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.skills_frame, text="Skills")
        
        # Create skills text widget with scrollbar
        skills_text_frame = ttk.Frame(self.skills_frame)
        skills_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        skills_text_frame.columnconfigure(0, weight=1)
        skills_text_frame.rowconfigure(0, weight=1)
        
        self.skills_text = tk.Text(skills_text_frame, wrap=tk.WORD, height=15, width=40)
        self.skills_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        skills_scrollbar = ttk.Scrollbar(skills_text_frame, orient=tk.VERTICAL, command=self.skills_text.yview)
        skills_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.skills_text.configure(yscrollcommand=skills_scrollbar.set)
        
        # Dupes tab
        self.dupes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dupes_frame, text="Dupes/Prowess")
        
        # Create dupes text widget with scrollbar
        dupes_text_frame = ttk.Frame(self.dupes_frame)
        dupes_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dupes_text_frame.columnconfigure(0, weight=1)
        dupes_text_frame.rowconfigure(0, weight=1)
        
        self.dupes_text = tk.Text(dupes_text_frame, wrap=tk.WORD, height=15, width=40)
        self.dupes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        dupes_scrollbar = ttk.Scrollbar(dupes_text_frame, orient=tk.VERTICAL, command=self.dupes_text.yview)
        dupes_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dupes_text.configure(yscrollcommand=dupes_scrollbar.set)
        
        # Configure grid weights for tabs
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.rowconfigure(0, weight=1)
        self.skills_frame.columnconfigure(0, weight=1)
        self.skills_frame.rowconfigure(0, weight=1)
        self.dupes_frame.columnconfigure(0, weight=1)
        self.dupes_frame.rowconfigure(0, weight=1)
        
        # Bottom panel - Action buttons
        button_frame = ttk.Frame(char_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Import HTML", command=self.import_html).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Import JSON", command=self.import_json).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export JSON", command=self.export_json).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Character", command=self.delete_character).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh List", command=self.refresh_character_list).pack(side=tk.LEFT, padx=(0, 10))
    
    def create_mathic_tab(self):
        """Create the Mathic System tab"""
        # Mathic tab frame
        mathic_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(mathic_frame, text="Mathic System")
        
        # Configure grid weights
        mathic_frame.columnconfigure(0, weight=1)
        mathic_frame.rowconfigure(0, weight=1)
        
        # Create notebook for mathic subsystems (now takes full space)
        mathic_notebook = ttk.Notebook(mathic_frame)
        mathic_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Module Editor tab
        module_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(module_frame, text="Module Editor")
        self.create_module_editor(module_frame)
        
        # Enhance Simulator tab
        enhance_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(enhance_frame, text="Enhance Simulator")
        self.create_enhance_simulator(enhance_frame)
        
        # Loadout Manager tab
        loadout_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(loadout_frame, text="Loadout Manager")
        self.create_loadout_manager(loadout_frame)
        
        # System Overview tab
        overview_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(overview_frame, text="System Overview")
        self.create_system_overview(overview_frame)
    
    def setup_events(self):
        """Setup event bindings"""
        self.character_tree.bind('<<TreeviewSelect>>', self.on_character_select)
        self.search_entry.bind('<Return>', lambda e: self.search_characters())
        self.rarity_var.trace('w', lambda *args: self.filter_characters())
        self.element_var.trace('w', lambda *args: self.filter_characters())
    
    def refresh_character_list(self):
        """Refresh the character list from database"""
        try:
            self.status_var.set("Loading characters...")
            self.root.update()
            
            # Clear existing items
            for item in self.character_tree.get_children():
                self.character_tree.delete(item)
            
            # Get characters from database
            characters = self.db.get_all_characters()
            
            for char in characters:
                # Format the updated timestamp
                updated_date = char['updated_at'].split(' ')[0] if char['updated_at'] else 'Unknown'
                
                self.character_tree.insert('', 'end', values=(
                    char['name'],
                    char['rarity'],
                    char['element'],
                    updated_date
                ))
            
            self.status_var.set(f"Loaded {len(characters)} characters")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load characters: {e}")
            self.status_var.set("Error loading characters")
    
    def search_characters(self):
        """Search characters by name"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.refresh_character_list()
            return
        
        try:
            # Clear existing items
            for item in self.character_tree.get_children():
                self.character_tree.delete(item)
            
            # Search in database
            characters = self.db.search_characters(name_like=search_term)
            
            for char in characters:
                updated_date = char['updated_at'].split(' ')[0] if char['updated_at'] else 'Unknown'
                
                self.character_tree.insert('', 'end', values=(
                    char['name'],
                    char['rarity'],
                    char['element'],
                    updated_date
                ))
            
            self.status_var.set(f"Found {len(characters)} characters matching '{search_term}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
    
    def filter_characters(self):
        """Filter characters by rarity and element"""
        try:
            rarity = self.rarity_var.get()
            element = self.element_var.get()
            
            search_params = {}
            if rarity != "All":
                search_params['rarity'] = rarity
            if element != "All":
                search_params['element'] = element
            
            # Clear existing items
            for item in self.character_tree.get_children():
                self.character_tree.delete(item)
            
            # Get filtered characters
            if search_params:
                characters = self.db.search_characters(**search_params)
            else:
                characters = self.db.get_all_characters()
            
            for char in characters:
                updated_date = char['updated_at'].split(' ')[0] if char['updated_at'] else 'Unknown'
                
                self.character_tree.insert('', 'end', values=(
                    char['name'],
                    char['rarity'],
                    char['element'],
                    updated_date
                ))
            
            filter_text = f"Filters: {rarity}, {element}" if search_params else "No filters"
            self.status_var.set(f"Showing {len(characters)} characters. {filter_text}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Filtering failed: {e}")
    
    def on_character_select(self, event):
        """Handle character selection"""
        try:
            selection = self.character_tree.selection()
            if not selection:
                return
            
            item = self.character_tree.item(selection[0])
            if not item or 'values' not in item or not item['values']:
                return
                
            character_name = item['values'][0]
            self.load_character_details(character_name)
            
        except Exception as e:
            print(f"Error in character selection: {e}")
            self.status_var.set(f"Selection error: {e}")
    
    def load_character_details(self, character_name):
        """Load and display character details"""
        try:
            character_data = self.db.get_character_by_name(character_name)
            if not character_data:
                messagebox.showerror("Error", f"Character '{character_name}' not found")
                return
            
            # Update basic info
            basic_info = character_data['basic_info']
            self.char_name_label.config(text=basic_info['name'])
            self.rarity_label.config(text=basic_info['rarity'])
            self.element_label.config(text=basic_info['element'])
            
            # Update stats
            self.display_stats(character_data['stats'])
            
            # Update skills
            self.display_skills(character_data['skills'])
            
            # Update dupes
            self.display_dupes(character_data['dupes'])
            
            # Force UI update
            self.root.update_idletasks()
            
            self.status_var.set(f"Loaded details for {character_name}")
            
        except Exception as e:
            error_msg = f"Failed to load character details: {e}"
            messagebox.showerror("Error", error_msg)
            self.status_var.set(f"Error loading details: {e}")
    
    def display_stats(self, stats):
        """Display character stats in the stats tab"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "CHARACTER STATS\n")
        self.stats_text.insert(tk.END, "="*50 + "\n\n")
        
        for stat_name, stat_data in stats.items():
            if isinstance(stat_data, dict):
                total = stat_data.get('total', 'N/A')
                base = stat_data.get('base', 'N/A')
                bonus = stat_data.get('bonus', 'N/A')
                
                self.stats_text.insert(tk.END, f"{stat_name}:\n")
                self.stats_text.insert(tk.END, f"  Total: {total}\n")
                self.stats_text.insert(tk.END, f"  Base: {base}\n")
                self.stats_text.insert(tk.END, f"  Bonus: {bonus}\n\n")
            else:
                self.stats_text.insert(tk.END, f"{stat_name}: {stat_data}\n\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def display_skills(self, skills):
        """Display character skills in the skills tab"""
        self.skills_text.config(state=tk.NORMAL)
        self.skills_text.delete(1.0, tk.END)
        
        self.skills_text.insert(tk.END, "CHARACTER SKILLS\n")
        self.skills_text.insert(tk.END, "="*50 + "\n\n")
        
        for i, skill in enumerate(skills, 1):
            skill_name = skill.get('name', f'Skill {i}')
            skill_effect = skill.get('effect', 'No description available')
            cooldown = skill.get('cooldown', 'N/A')
            tags = ', '.join(skill.get('tags', []))
            
            self.skills_text.insert(tk.END, f"Skill {i}: {skill_name}\n")
            self.skills_text.insert(tk.END, f"Cooldown: {cooldown}\n")
            self.skills_text.insert(tk.END, f"Tags: {tags}\n")
            self.skills_text.insert(tk.END, f"Effect: {skill_effect}\n")
            self.skills_text.insert(tk.END, "-" * 40 + "\n\n")
        
        self.skills_text.config(state=tk.DISABLED)
    
    def display_dupes(self, dupes):
        """Display character dupes/prowess in the dupes tab"""
        self.dupes_text.config(state=tk.NORMAL)
        self.dupes_text.delete(1.0, tk.END)
        
        self.dupes_text.insert(tk.END, "CHARACTER DUPES/PROWESS\n")
        self.dupes_text.insert(tk.END, "="*50 + "\n\n")
        
        for dupe_id, dupe_data in dupes.items():
            if isinstance(dupe_data, dict):
                dupe_name = dupe_data.get('name', dupe_id)
                dupe_effect = dupe_data.get('effect', 'No effect description')
            else:
                dupe_name = dupe_id
                dupe_effect = str(dupe_data)
            
            self.dupes_text.insert(tk.END, f"{dupe_id} - {dupe_name}\n")
            self.dupes_text.insert(tk.END, f"Effect: {dupe_effect}\n")
            self.dupes_text.insert(tk.END, "-" * 40 + "\n\n")
        
        self.dupes_text.config(state=tk.DISABLED)
    
    def import_html(self):
        """Import character data from HTML file"""
        file_path = filedialog.askopenfilename(
            title="Select HTML file",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.status_var.set("Parsing HTML file...")
            self.root.update()
            
            # Parse HTML file
            parser = CharacterParser(file_path)
            character_data = parser.parse_all()
            
            if character_data:
                # Import to database
                character_id = self.db.insert_character_data(character_data)
                if character_id:
                    character_name = character_data['basic_info']['name']
                    messagebox.showinfo("Success", f"Character '{character_name}' imported successfully!")
                    self.refresh_character_list()
                else:
                    messagebox.showerror("Error", "Failed to save character data to database")
            else:
                messagebox.showerror("Error", "Failed to parse HTML file")
            
            self.status_var.set("Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
            self.status_var.set("Import failed")
    
    def import_json(self):
        """Import character data from JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.status_var.set("Importing JSON file...")
            self.root.update()
            
            success = self.db.import_from_json(file_path)
            if success:
                messagebox.showinfo("Success", "Character data imported successfully!")
                self.refresh_character_list()
            else:
                messagebox.showerror("Error", "Failed to import JSON file")
            
            self.status_var.set("Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
            self.status_var.set("Import failed")
    
    def export_json(self):
        """Export selected character data to JSON file"""
        selection = self.character_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a character to export")
            return
        
        item = self.character_tree.item(selection[0])
        character_name = item['values'][0]
        
        file_path = filedialog.asksaveasfilename(
            title="Save character data as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialvalue=f"{character_name.lower()}_data.json"
        )
        
        if not file_path:
            return
        
        try:
            self.status_var.set(f"Exporting {character_name}...")
            self.root.update()
            
            success = self.db.export_to_json(character_name, file_path)
            if success:
                messagebox.showinfo("Success", f"Character '{character_name}' exported to {file_path}")
            else:
                messagebox.showerror("Error", "Export failed")
            
            self.status_var.set("Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
            self.status_var.set("Export failed")
    
    def delete_character(self):
        """Delete selected character"""
        selection = self.character_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a character to delete")
            return
        
        item = self.character_tree.item(selection[0])
        character_name = item['values'][0]
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete character '{character_name}'?\n\nThis action cannot be undone."
        )
        
        if result:
            try:
                self.status_var.set(f"Deleting {character_name}...")
                self.root.update()
                
                success = self.db.delete_character(character_name)
                if success:
                    messagebox.showinfo("Success", f"Character '{character_name}' deleted successfully")
                    self.refresh_character_list()
                    # Clear details panel
                    self.clear_character_details()
                else:
                    messagebox.showerror("Error", "Delete failed")
                
                self.status_var.set("Ready")
                
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {e}")
                self.status_var.set("Delete failed")
    
    def clear_character_details(self):
        """Clear the character details panel"""
        self.char_name_label.config(text="Select a character")
        self.rarity_label.config(text="-")
        self.element_label.config(text="-")
        
        # Clear all text widgets
        for text_widget in [self.stats_text, self.skills_text, self.dupes_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
    
    def create_module_editor(self, parent_frame):
        """Create module editor interface"""
        # Configure grid weights for parent frame
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1) 
        parent_frame.rowconfigure(0, weight=1)
        
        # Left panel - Module list
        left_panel = ttk.LabelFrame(parent_frame, text="Modules", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Module list
        self.module_listbox = tk.Listbox(left_panel, height=15)
        self.module_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.module_listbox.bind('<<ListboxSelect>>', self.on_module_select)
        
        module_scroll = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.module_listbox.yview)
        module_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.module_listbox.configure(yscrollcommand=module_scroll.set)
        
        # Module controls
        controls_frame = ttk.Frame(left_panel)
        controls_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(controls_frame, text="New Module", command=self.new_module).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(controls_frame, text="Delete Module", command=self.delete_module).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(controls_frame, text="Manual Enhance", command=self.enhance_module_manual).grid(row=0, column=2)
        
        # Right panel - Module details
        right_panel = ttk.LabelFrame(parent_frame, text="Module Details", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Module type and main stat
        type_frame = ttk.Frame(right_panel)
        type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(type_frame, text="Type:").grid(row=0, column=0, padx=(0, 5))
        self.module_type_var = tk.StringVar(value="mask")
        self.module_type_combo = ttk.Combobox(type_frame, textvariable=self.module_type_var,
                                            values=["mask", "transistor", "wristwheel", "core"],
                                            state="readonly", width=15)
        self.module_type_combo.grid(row=0, column=1, padx=(0, 10))
        self.module_type_combo.bind('<<ComboboxSelected>>', self.on_module_type_change)
        
        ttk.Label(type_frame, text="Main Stat:").grid(row=0, column=2, padx=(0, 5))
        self.main_stat_var = tk.StringVar()
        self.main_stat_combo = ttk.Combobox(type_frame, textvariable=self.main_stat_var,
                                          state="readonly", width=12)
        self.main_stat_combo.grid(row=0, column=3, padx=(0, 10))
        self.main_stat_combo.bind('<<ComboboxSelected>>', self.on_main_stat_change)
        
        ttk.Label(type_frame, text="Value:").grid(row=0, column=4, padx=(0, 5))
        self.main_stat_value_var = tk.StringVar()
        self.main_stat_entry = ttk.Entry(type_frame, textvariable=self.main_stat_value_var, 
                                       width=8, state="readonly")
        self.main_stat_entry.grid(row=0, column=5)
        
        # Substats frame
        substats_frame = ttk.LabelFrame(right_panel, text="Substats", padding="10")
        substats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Substats display
        self.substats_tree = ttk.Treeview(substats_frame, 
                                        columns=('Stat', 'Value', 'Rolls', 'Efficiency'), 
                                        show='headings', height=8)
        
        self.substats_tree.heading('Stat', text='Stat')
        self.substats_tree.heading('Value', text='Value')
        self.substats_tree.heading('Rolls', text='Rolls')
        self.substats_tree.heading('Efficiency', text='Efficiency')
        
        self.substats_tree.column('Stat', width=120)
        self.substats_tree.column('Value', width=80)
        self.substats_tree.column('Rolls', width=60)
        self.substats_tree.column('Efficiency', width=80)
        
        self.substats_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        substats_scroll = ttk.Scrollbar(substats_frame, orient=tk.VERTICAL, 
                                      command=self.substats_tree.yview)
        substats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.substats_tree.configure(yscrollcommand=substats_scroll.set)
        
        # Module editing controls frame
        edit_frame = ttk.LabelFrame(right_panel, text="Module Editing", padding="10")
        edit_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Total rolls display (read-only, automatically calculated)
        ttk.Label(edit_frame, text="Total Rolls:").grid(row=0, column=0, padx=(0, 5))
        self.total_rolls_var = tk.StringVar(value="0")
        self.total_rolls_label = ttk.Label(edit_frame, textvariable=self.total_rolls_var,
                                         font=('Arial', 10, 'bold'), foreground="darkblue")
        self.total_rolls_label.grid(row=0, column=1, padx=(0, 10))
        ttk.Label(edit_frame, text="(auto-calculated)", font=('Arial', 8), foreground="gray").grid(row=0, column=2, padx=(0, 10))
        
        # Substat editing controls
        ttk.Label(edit_frame, text="Edit Substat:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        
        # Substat 1
        substat1_frame = ttk.Frame(edit_frame)
        substat1_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Label(substat1_frame, text="1:").grid(row=0, column=0, padx=(0, 5))
        self.substat1_type_var = tk.StringVar()
        self.substat1_combo = ttk.Combobox(substat1_frame, textvariable=self.substat1_type_var,
                                         width=12, state="readonly")
        self.substat1_combo.grid(row=0, column=1, padx=(0, 5))
        self.substat1_value_var = tk.StringVar()
        self.substat1_value_combo = ttk.Combobox(substat1_frame, textvariable=self.substat1_value_var, width=8)
        self.substat1_value_combo.grid(row=0, column=2, padx=(0, 5))
        self.substat1_rolls_var = tk.StringVar(value="0")
        self.substat1_spinbox = ttk.Spinbox(substat1_frame, textvariable=self.substat1_rolls_var,
                                          from_=0, to=5, width=5)
        self.substat1_spinbox.grid(row=0, column=3)
        
        # Substat 2
        substat2_frame = ttk.Frame(edit_frame)
        substat2_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0))
        ttk.Label(substat2_frame, text="2:").grid(row=0, column=0, padx=(0, 5))
        self.substat2_type_var = tk.StringVar()
        self.substat2_combo = ttk.Combobox(substat2_frame, textvariable=self.substat2_type_var,
                                         width=12, state="readonly")
        self.substat2_combo.grid(row=0, column=1, padx=(0, 5))
        self.substat2_value_var = tk.StringVar()
        self.substat2_value_combo = ttk.Combobox(substat2_frame, textvariable=self.substat2_value_var, width=8)
        self.substat2_value_combo.grid(row=0, column=2, padx=(0, 5))
        self.substat2_rolls_var = tk.StringVar(value="0")
        self.substat2_spinbox = ttk.Spinbox(substat2_frame, textvariable=self.substat2_rolls_var,
                                          from_=0, to=5, width=5)
        self.substat2_spinbox.grid(row=0, column=3)
        
        # Substat 3
        substat3_frame = ttk.Frame(edit_frame)
        substat3_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0))
        ttk.Label(substat3_frame, text="3:").grid(row=0, column=0, padx=(0, 5))
        self.substat3_type_var = tk.StringVar()
        self.substat3_combo = ttk.Combobox(substat3_frame, textvariable=self.substat3_type_var,
                                         width=12, state="readonly")
        self.substat3_combo.grid(row=0, column=1, padx=(0, 5))
        self.substat3_value_var = tk.StringVar()
        self.substat3_value_combo = ttk.Combobox(substat3_frame, textvariable=self.substat3_value_var, width=8)
        self.substat3_value_combo.grid(row=0, column=2, padx=(0, 5))
        self.substat3_rolls_var = tk.StringVar(value="0")
        self.substat3_spinbox = ttk.Spinbox(substat3_frame, textvariable=self.substat3_rolls_var,
                                          from_=0, to=5, width=5)
        self.substat3_spinbox.grid(row=0, column=3)
        
        # Substat 4
        substat4_frame = ttk.Frame(edit_frame)
        substat4_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0))
        ttk.Label(substat4_frame, text="4:").grid(row=0, column=0, padx=(0, 5))
        self.substat4_type_var = tk.StringVar()
        self.substat4_combo = ttk.Combobox(substat4_frame, textvariable=self.substat4_type_var,
                                         width=12, state="readonly")
        self.substat4_combo.grid(row=0, column=1, padx=(0, 5))
        self.substat4_value_var = tk.StringVar()
        self.substat4_value_combo = ttk.Combobox(substat4_frame, textvariable=self.substat4_value_var, width=8)
        self.substat4_value_combo.grid(row=0, column=2, padx=(0, 5))
        self.substat4_rolls_var = tk.StringVar(value="0")
        self.substat4_spinbox = ttk.Spinbox(substat4_frame, textvariable=self.substat4_rolls_var,
                                          from_=0, to=5, width=5)
        self.substat4_spinbox.grid(row=0, column=3)
        
        # Apply changes button
        ttk.Button(edit_frame, text="Apply Changes", command=self.apply_module_changes).grid(row=6, column=0, pady=(10, 0))
        
        # Store substat controls for easy access
        self.substat_controls = [
            (self.substat1_combo, self.substat1_value_combo, self.substat1_spinbox, self.substat1_type_var, self.substat1_value_var, self.substat1_rolls_var),
            (self.substat2_combo, self.substat2_value_combo, self.substat2_spinbox, self.substat2_type_var, self.substat2_value_var, self.substat2_rolls_var),
            (self.substat3_combo, self.substat3_value_combo, self.substat3_spinbox, self.substat3_type_var, self.substat3_value_var, self.substat3_rolls_var),
            (self.substat4_combo, self.substat4_value_combo, self.substat4_spinbox, self.substat4_type_var, self.substat4_value_var, self.substat4_rolls_var),
        ]
        
        # Configure additional grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        substats_frame.columnconfigure(0, weight=1)
        substats_frame.rowconfigure(0, weight=1)
        
        # Initialize selection tracking
        self.current_selected_module_id = None
        self.current_selected_index = None
        
        # Initialize flag to prevent infinite loops during rolls adjustment
        self.adjusting_rolls = False
        self.pending_warning = None  # For batching warning messages
        self.rolls_change_depth = 0  # Track reentrancy depth for additional protection
        
        # Initialize
        self.create_sample_modules()
        self.refresh_module_list()
        self.on_module_type_change()
    
    def create_loadout_manager(self, parent_frame):
        """Create loadout manager interface"""
        # Configure grid weights - now we have two columns
        parent_frame.columnconfigure(0, weight=2)  # Left side for slots
        parent_frame.columnconfigure(1, weight=1)  # Right side for stats
        parent_frame.rowconfigure(1, weight=1)
        
        # Top frame - Loadout selection (spans both columns)
        top_frame = ttk.Frame(parent_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
        
        ttk.Label(top_frame, text="Loadout:").grid(row=0, column=0, padx=(0, 5))
        self.loadout_var = tk.StringVar()
        self.loadout_combo = ttk.Combobox(top_frame, textvariable=self.loadout_var,
                                        state="readonly", width=20)
        self.loadout_combo.grid(row=0, column=1, padx=(0, 10))
        self.loadout_combo.bind('<<ComboboxSelected>>', self.on_loadout_select)
        
        ttk.Button(top_frame, text="New Loadout", command=self.new_loadout).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(top_frame, text="Delete Loadout", command=self.delete_loadout).grid(row=0, column=3)
        
        # Loadout slots frame (left side)
        slots_frame = ttk.LabelFrame(parent_frame, text="Equipment Slots", padding="10")
        slots_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=5)
        
        # Create 6 slots in vertical layout (2 columns x 3 rows)
        # slot 1  slot 4
        # slot 2  slot 5  
        # slot 3  slot 6
        self.slot_frames = {}
        self.slot_labels = {}
        self.slot_combos = {}
        self.slot_vars = {}
        
        slot_positions = [
            (0, 0), (1, 0), (2, 0),  # Column 1: slots 1, 2, 3
            (0, 1), (1, 1), (2, 1)   # Column 2: slots 4, 5, 6
        ]
        
        for i in range(6):
            slot_id = i + 1
            row, col = slot_positions[i]
            
            slot_frame = ttk.LabelFrame(slots_frame, text=f"Slot {slot_id}", padding="10")
            slot_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=5, pady=5)
            
            self.slot_frames[slot_id] = slot_frame
            
            # Module selection
            self.slot_vars[slot_id] = tk.StringVar()
            self.slot_combos[slot_id] = ttk.Combobox(slot_frame, 
                                                   textvariable=self.slot_vars[slot_id],
                                                   state="readonly", width=15)
            self.slot_combos[slot_id].grid(row=0, column=0, pady=(0, 5))
            self.slot_combos[slot_id].bind('<<ComboboxSelected>>', 
                                         lambda e, s=slot_id: self.on_slot_module_change(s))
            
            # Substats display area (vertical layout)
            self.slot_substats_labels = getattr(self, 'slot_substats_labels', {})
            substats_frame = ttk.Frame(slot_frame)
            substats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            
            # Create 4 labels for substats in vertical layout
            self.slot_substats_labels[slot_id] = []
            for i in range(4):
                substat_label = ttk.Label(substats_frame, text="", font=("Arial", 10), foreground="darkblue")
                substat_label.grid(row=i, column=0, sticky=tk.W, pady=1)
                self.slot_substats_labels[slot_id].append(substat_label)
        
        # Stats summary frame (right side)
        stats_frame = ttk.LabelFrame(parent_frame, text="Total Stats", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=5)
        
        self.stats_summary_text = tk.Text(stats_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure additional grid weights for vertical layout (2 columns x 3 rows)
        slots_frame.columnconfigure(0, weight=1)
        slots_frame.columnconfigure(1, weight=1)
        slots_frame.rowconfigure(0, weight=1)
        slots_frame.rowconfigure(1, weight=1)
        slots_frame.rowconfigure(2, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # Initialize
        self.refresh_loadout_list()
    
    def create_enhance_simulator(self, parent_frame):
        """Create enhance simulator interface"""
        # Configure grid weights
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        # Top frame - Module selection
        top_frame = ttk.Frame(parent_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(top_frame, text="Select Module for Enhancement:").grid(row=0, column=0, padx=(0, 10))
        self.enhance_module_var = tk.StringVar()
        self.enhance_module_combo = ttk.Combobox(top_frame, textvariable=self.enhance_module_var,
                                               state="readonly", width=30)
        self.enhance_module_combo.grid(row=0, column=1, padx=(0, 10))
        self.enhance_module_combo.bind('<<ComboboxSelected>>', self.on_enhance_module_select)
        
        ttk.Button(top_frame, text="Refresh Modules", command=self.refresh_enhance_modules).grid(row=0, column=2)
        
        # Left panel - Enhancement controls and current module info
        left_panel = ttk.LabelFrame(parent_frame, text="Enhancement Controls", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Current module info
        current_info_frame = ttk.LabelFrame(left_panel, text="Current Module", padding="10")
        current_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.current_module_text = tk.Text(current_info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.current_module_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Enhancement buttons
        enhance_buttons_frame = ttk.Frame(left_panel)
        enhance_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(enhance_buttons_frame, text="Enhance Once", command=self.enhance_once).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance 5 Times", command=self.enhance_five_times).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance to Max", command=self.enhance_to_max).grid(row=0, column=2)
        
        # Enhancement log
        log_frame = ttk.LabelFrame(left_panel, text="Enhancement Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.enhancement_log = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.enhancement_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.enhancement_log.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.enhancement_log.configure(yscrollcommand=log_scroll.set)
        
        # Right panel - Statistics and probabilities
        right_panel = ttk.LabelFrame(parent_frame, text="Statistics & Analysis", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Substat probabilities
        prob_frame = ttk.LabelFrame(right_panel, text="Enhancement Probabilities", padding="10")
        prob_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.probability_tree = ttk.Treeview(prob_frame, columns=('Probability',), show='tree headings', height=8)
        self.probability_tree.heading('#0', text='Substat')
        self.probability_tree.heading('Probability', text='Probability (%)')
        self.probability_tree.column('#0', width=150)
        self.probability_tree.column('Probability', width=100)
        self.probability_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        prob_scroll = ttk.Scrollbar(prob_frame, orient=tk.VERTICAL, command=self.probability_tree.yview)
        prob_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.probability_tree.configure(yscrollcommand=prob_scroll.set)
        
        # Module value analysis
        value_frame = ttk.LabelFrame(right_panel, text="Module Value Analysis", padding="10")
        value_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.value_analysis_text = tk.Text(value_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
        self.value_analysis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        value_scroll = ttk.Scrollbar(value_frame, orient=tk.VERTICAL, command=self.value_analysis_text.yview)
        value_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.value_analysis_text.configure(yscrollcommand=value_scroll.set)
        
        # Configure grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        current_info_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        prob_frame.columnconfigure(0, weight=1)
        value_frame.columnconfigure(0, weight=1)
        value_frame.rowconfigure(0, weight=1)
        
        # Initialize
        self.refresh_enhance_modules()
    
    def create_system_overview(self, parent_frame):
        """Create system overview interface"""
        # Configure grid weights
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        
        overview_text = tk.Text(parent_frame, wrap=tk.WORD, state=tk.DISABLED)
        overview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=10)
        
        overview_scroll = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL,
                                      command=overview_text.yview)
        overview_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(0, 10), pady=10)
        overview_text.configure(yscrollcommand=overview_scroll.set)
        
        parent_frame.columnconfigure(1, weight=0)  # Scrollbar column should not expand
        
        self.overview_text = overview_text
        self.update_system_overview()
    
    # Mathic system event handlers
    def create_sample_modules(self):
        """Create sample modules for demonstration"""
        if not self.mathic_system.modules:  # Only create if no modules exist
            try:
                # Create sample modules
                samples = [
                    ("mask", "ATK"),
                    ("transistor", "HP"),
                    ("wristwheel", "DEF"),
                    ("core", "CRIT Rate"),
                    ("core", "CRIT DMG"),
                ]
                
                for i, (module_type, main_stat) in enumerate(samples):
                    slot_position = i + 1
                    module = self.mathic_system.create_module(module_type, slot_position, main_stat)
                    
                    if module:
                        # Generate random substats
                        self.mathic_system.generate_random_substats(module, 4)
                        
                        # Enhance some modules randomly
                        for _ in range(2):  # 2 enhancement attempts
                            self.mathic_system.enhance_module_random_substat(module)
                
                # Create sample loadouts
                self.mathic_system.create_mathic_loadout("Sample Build")
                self.mathic_system.create_mathic_loadout("DPS Build")
                
                print(f"Created {len(samples)} sample modules and 2 loadouts")
                
            except Exception as e:
                print(f"Error creating sample modules: {e}")
    
    def refresh_module_list(self):
        """Refresh the module list"""
        self.module_listbox.delete(0, tk.END)
        for module_id, module in self.mathic_system.modules.items():
            display_text = f"{module.module_type} - {module.main_stat} ({module.level})"
            self.module_listbox.insert(tk.END, display_text)
    
    def on_module_select(self, event):
        """Handle module selection"""
        selection = self.module_listbox.curselection()
        if selection:
            idx = selection[0]
            module_id = list(self.mathic_system.modules.keys())[idx]
            module = self.mathic_system.modules[module_id]
            # Store current selection for later reference
            self.current_selected_module_id = module_id
            self.current_selected_index = idx
            self.display_module_details(module)
            self.update_enhance_options()
    
    def on_module_type_change(self, event=None):
        """Handle module type change"""
        module_type = self.module_type_var.get()
        if module_type in self.mathic_system.config.get("module_types", {}):
            module_config = self.mathic_system.config["module_types"][module_type]
            main_stat_options = module_config["main_stat_options"]
            self.main_stat_combo.configure(values=main_stat_options)
            if main_stat_options:
                self.main_stat_var.set(main_stat_options[0])
                # Auto-fill main stat value
                self.on_main_stat_change()
        
        # Update substat options
        self.update_substat_options()
    
    def on_main_stat_change(self, event=None):
        """Handle main stat change - auto-fill the value"""
        module_type = self.module_type_var.get()
        main_stat = self.main_stat_var.get()
        
        if (module_type in self.mathic_system.config.get("module_types", {}) and 
            main_stat in self.mathic_system.config["module_types"][module_type]["max_main_stats"]):
            max_value = self.mathic_system.config["module_types"][module_type]["max_main_stats"][main_stat]
            self.main_stat_value_var.set(str(int(max_value)))
    
    def update_substat_options(self):
        """Update substat combo options based on main stat"""
        available_stats = list(self.mathic_system.config.get("substats", {}).keys())
        main_stat = self.main_stat_var.get()
        
        # Remove main stat from available substats
        if main_stat in available_stats:
            available_stats.remove(main_stat)
        
        # Remove percentage version if flat version is main stat (and vice versa)
        main_stat_base = main_stat.replace('%', '')
        for stat in available_stats[:]:
            stat_base = stat.replace('%', '')
            if stat_base == main_stat_base and stat != main_stat:
                available_stats.remove(stat)
        
        # Add "None" option at the beginning
        substat_options = [""] + available_stats
        
        # Update all substat combos
        for combo, _, _, _, _, _ in self.substat_controls:
            combo.configure(values=substat_options)
        
        # Bind substat type change events to update value options and total rolls
        self.substat1_combo.bind('<<ComboboxSelected>>', lambda e: self.on_substat_type_change(1))
        self.substat2_combo.bind('<<ComboboxSelected>>', lambda e: self.on_substat_type_change(2))
        self.substat3_combo.bind('<<ComboboxSelected>>', lambda e: self.on_substat_type_change(3))
        self.substat4_combo.bind('<<ComboboxSelected>>', lambda e: self.on_substat_type_change(4))
        
        # Bind substat type variable changes to update total rolls
        self.substat1_type_var.trace('w', lambda *args: self.on_substat_type_change(1))
        self.substat2_type_var.trace('w', lambda *args: self.on_substat_type_change(2))
        self.substat3_type_var.trace('w', lambda *args: self.on_substat_type_change(3))
        self.substat4_type_var.trace('w', lambda *args: self.on_substat_type_change(4))
        
        # Bind roll spinbox value changes to update value options and total rolls
        self.substat1_rolls_var.trace('w', lambda *args: self.on_substat_rolls_change(1))
        self.substat2_rolls_var.trace('w', lambda *args: self.on_substat_rolls_change(2))
        self.substat3_rolls_var.trace('w', lambda *args: self.on_substat_rolls_change(3))
        self.substat4_rolls_var.trace('w', lambda *args: self.on_substat_rolls_change(4))
    
    def display_module_details(self, module):
        """Display module details in the editor"""
        self.module_type_var.set(module.module_type)
        self.main_stat_var.set(module.main_stat)
        self.main_stat_value_var.set(str(module.main_stat_value))
        
        # Update main stat combo
        self.on_module_type_change()
        
        # Clear and populate substats tree
        for item in self.substats_tree.get_children():
            self.substats_tree.delete(item)
        
        for substat in module.substats:
            if substat.stat_name:
                max_value = self.mathic_system.config["substats"][substat.stat_name]["max_value"]
                efficiency = substat.get_efficiency_percentage(max_value)
                
                self.substats_tree.insert('', tk.END, values=(
                    substat.stat_name,
                    f"{int(substat.current_value)}",  # Show as integer
                    f"{substat.rolls_used}/{substat.max_rolls}",
                    f"{efficiency:.1f}%"
                ))
        
        # Update editing controls
        self.update_editing_controls(module)
        
    def update_editing_controls(self, module):
        """Update the editing controls with module data"""
        # Set substat data first
        for i in range(4):
            combo, value_combo, spinbox, type_var, value_var, rolls_var = self.substat_controls[i]
            if i < len(module.substats):
                substat = module.substats[i]
                type_var.set(substat.stat_name)
                value_var.set(str(int(substat.current_value)))
                rolls_var.set(str(substat.rolls_used))
                # Update value options for this substat
                self.update_substat_value_options(i + 1)
            else:
                type_var.set("")
                value_var.set("")
                rolls_var.set("0")
                # Clear value options
                value_combo.configure(values=[])
        
        # Update total rolls display automatically based on individual rolls
        self.update_total_rolls_display()
    
    def update_substat_value_options(self, substat_index):
        """Update value options based on substat type and roll count"""
        if not hasattr(self, 'substat_controls') or substat_index < 1 or substat_index > 4:
            return
        
        idx = substat_index - 1
        combo, value_combo, spinbox, type_var, value_var, rolls_var = self.substat_controls[idx]
        
        stat_name = type_var.get()
        if not stat_name or stat_name == "":
            value_combo.configure(values=[])
            return
        
        try:
            rolls = int(rolls_var.get()) if rolls_var.get() else 0
        except ValueError:
            rolls = 0
        
        if stat_name in self.mathic_system.config["substats"]:
            stat_config = self.mathic_system.config["substats"][stat_name]
            roll_range = stat_config["roll_range"]
            min_roll, max_roll = roll_range
            
            # Calculate possible values based on rolls
            value_options = []
            
            if rolls == 0:
                # Initial roll - single roll range
                for val in range(min_roll, max_roll + 1):
                    value_options.append(str(val))
            else:
                # Multiple rolls - calculate possible totals
                min_total = min_roll + (rolls - 1) * min_roll  # minimum possible
                max_total = max_roll + (rolls - 1) * max_roll  # maximum possible
                
                # Create reasonable intervals for selection
                step = max(1, (max_total - min_total) // 20)  # At most 20 options
                for val in range(min_total, max_total + 1, step):
                    value_options.append(str(val))
                
                # Always include the maximum possible value
                if str(max_total) not in value_options:
                    value_options.append(str(max_total))
            
            value_combo.configure(values=value_options)
            
            # Preserve current value if it's valid, otherwise set to maximum
            current_value = value_var.get()
            if not current_value and value_options:
                value_var.set(value_options[-1])  # Set to max value only if empty
            elif current_value and current_value not in value_options and value_options:
                # If current value is not valid for new roll count, set to closest valid value
                try:
                    current_float = float(current_value)
                    # Find closest valid value
                    closest_value = min(value_options, key=lambda x: abs(float(x) - current_float))
                    value_var.set(closest_value)
                except ValueError:
                    value_var.set(value_options[-1])
        else:
            value_combo.configure(values=[])
    
    def on_substat_type_change(self, substat_index):
        """Handle substat type change - update value options and total rolls"""
        self.update_substat_value_options(substat_index)
        self.update_total_rolls_display()
    
    def on_substat_rolls_change(self, substat_index):
        """Handle substat rolls change - update value options and validate total rolls"""
        # Prevent infinite loops during adjustment or messagebox display
        if getattr(self, 'adjusting_rolls', False):
            return
        
        # Note: We don't block on pending_warning here because adjustment logic should still run
        # Only the warning display is batched, not the actual value adjustment
        
        # Final protection: prevent excessive reentrancy depth
        if getattr(self, 'rolls_change_depth', 0) > 0:
            return
        
        # Set reentrancy counter
        self.rolls_change_depth = getattr(self, 'rolls_change_depth', 0) + 1
        
        # Calculate what the new total would be
        try:
            new_total = 0
            for _, _, _, type_var, _, rolls_var in self.substat_controls:
                # Only count rolls if substat type is set (not empty)
                stat_name = type_var.get()
                if stat_name and stat_name != "":
                    rolls = int(rolls_var.get()) if rolls_var.get() else 0
                    new_total += rolls
            
            # Check if total rolls would exceed 5
            if new_total > 5:
                # Set flag to prevent infinite loops
                self.adjusting_rolls = True
                max_allowed = 0  # Default value
                
                try:
                    # Reset the current substat's rolls to bring total back to 5 or under
                    idx = substat_index - 1
                    current_rolls_var = self.substat_controls[idx][5]  # rolls_var is at index 5
                    current_rolls = int(current_rolls_var.get()) if current_rolls_var.get() else 0
                    
                    # Calculate maximum allowed rolls for this substat
                    other_total = new_total - current_rolls
                    max_allowed = 5 - other_total
                    
                    if max_allowed < 0:
                        max_allowed = 0
                    
                    # Set the rolls to maximum allowed value
                    current_rolls_var.set(str(max_allowed))
                    
                except ValueError:
                    pass
                finally:
                    # Always clear the flag first
                    self.adjusting_rolls = False
                
                # Schedule warning message to avoid multiple rapid messageboxes
                self.schedule_warning_message(substat_index, max_allowed)
        
        except ValueError:
            pass  # Ignore invalid values
        finally:
            # Always reset reentrancy counter
            self.rolls_change_depth = max(0, getattr(self, 'rolls_change_depth', 1) - 1)
        
        # Update value options and total display
        self.update_substat_value_options(substat_index)
        self.update_total_rolls_display()
    
    def schedule_warning_message(self, substat_index, adjusted_value):
        """Schedule a warning message, batching multiple rapid adjustments"""
        # Cancel any existing pending warning
        if self.pending_warning:
            self.root.after_cancel(self.pending_warning)
        
        # Schedule new warning with a small delay to batch rapid changes
        def show_warning():
            # Additional protection: Set flag before showing messagebox
            self.adjusting_rolls = True
            try:
                messagebox.showwarning("Rolls Limit", 
                                     f"Total rolls cannot exceed 5.\n"
                                     f"Values have been automatically adjusted.")
            finally:
                # Always clear flag after messagebox, even if exception occurs
                self.adjusting_rolls = False
                self.pending_warning = None
        
        self.pending_warning = self.root.after(100, show_warning)  # 100ms delay
    
    def update_total_rolls_display(self):
        """Update total rolls display based on individual substat rolls (only count non-empty substats)"""
        try:
            total = 0
            for _, _, _, type_var, _, rolls_var in self.substat_controls:
                # Only count rolls if substat type is set (not empty)
                stat_name = type_var.get()
                if stat_name and stat_name != "":
                    rolls = int(rolls_var.get()) if rolls_var.get() else 0
                    total += rolls
            self.total_rolls_var.set(str(total))
        except ValueError:
            self.total_rolls_var.set("0")
    
    def apply_module_changes(self):
        """Apply the changes made in the editing controls"""
        # Use tracked selection instead of current selection to avoid UI interaction issues
        if not hasattr(self, 'current_selected_module_id') or self.current_selected_module_id is None:
            messagebox.showwarning("Warning", "Please select a module to edit")
            return
        
        module_id = self.current_selected_module_id
        if module_id not in self.mathic_system.modules:
            messagebox.showerror("Error", "Selected module no longer exists")
            return
        
        module = self.mathic_system.modules[module_id]
        
        try:
            # Collect and validate substats
            new_substats = []
            used_stats = set()
            
            for i, (combo, entry, spinbox, type_var, value_var, rolls_var) in enumerate(self.substat_controls):
                stat_name = type_var.get()
                if stat_name and stat_name != "":
                    # Check for duplicate substats
                    if stat_name in used_stats:
                        messagebox.showerror("Error", f"Duplicate substat: {stat_name}\nEach substat can only appear once.")
                        return
                    used_stats.add(stat_name)
                    
                    try:
                        value = float(value_var.get()) if value_var.get() else 0.0
                        rolls = int(rolls_var.get()) if rolls_var.get() else 0
                        
                        # Validate rolls
                        if rolls < 0 or rolls > 5:
                            messagebox.showerror("Error", f"Rolls for {stat_name} must be between 0 and 5")
                            return
                        
                        # Validate value based on stat config
                        if stat_name in self.mathic_system.config["substats"]:
                            stat_config = self.mathic_system.config["substats"][stat_name]
                            max_possible = stat_config["max_value"]
                            if value > max_possible:
                                messagebox.showerror("Error", 
                                                   f"Value for {stat_name} ({value}) exceeds maximum ({max_possible})")
                                return
                        
                        # Create substat
                        from mathic.mathic_system import Substat
                        substat = Substat(stat_name, value, rolls)
                        new_substats.append(substat)
                        
                    except ValueError as e:
                        messagebox.showerror("Error", f"Invalid value for substat {i+1}: {e}")
                        return
            
            # Calculate total rolls automatically from individual rolls
            total_rolls = sum(substat.rolls_used for substat in new_substats)
            
            # Validate total rolls don't exceed maximum
            if total_rolls > module.max_total_rolls:
                messagebox.showerror("Error", 
                                   f"Total rolls ({total_rolls}) exceeds maximum allowed ({module.max_total_rolls})")
                return
            
            # Apply changes
            module.total_enhancement_rolls = total_rolls
            module.level = total_rolls
            module.substats = new_substats
            
            # Update total rolls display automatically
            self.total_rolls_var.set(str(total_rolls))
            
            # Refresh displays first
            self.refresh_module_list()
            
            # Restore selection using tracked index
            if hasattr(self, 'current_selected_index') and self.current_selected_index is not None:
                try:
                    self.module_listbox.selection_set(self.current_selected_index)
                    self.module_listbox.activate(self.current_selected_index)
                    self.module_listbox.see(self.current_selected_index)
                except:
                    pass  # Selection restoration failed, but not critical
            
            # Display details after selection is restored
            self.display_module_details(module)
            
            messagebox.showinfo("Success", "Module updated successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update module: {e}")
    
    def new_module(self):
        """Create a new module using values from the editing panel"""
        module_type = self.module_type_var.get()
        main_stat = self.main_stat_var.get()
        
        if not main_stat:
            messagebox.showwarning("Warning", "Please select a main stat")
            return
        
        try:
            # Get main stat value from the editing panel
            main_stat_value = float(self.main_stat_value_var.get()) if self.main_stat_value_var.get() else 0.0
            
            # Validate total rolls
            try:
                total_rolls = int(self.total_rolls_var.get())
                if total_rolls < 0 or total_rolls > 5:
                    messagebox.showerror("Error", "Total rolls must be between 0 and 5")
                    return
            except ValueError:
                total_rolls = 0
            
            # Collect substats from editing panel
            new_substats = []
            used_stats = set()
            
            for i, (combo, entry, spinbox, type_var, value_var, rolls_var) in enumerate(self.substat_controls):
                stat_name = type_var.get()
                if stat_name and stat_name != "":
                    # Check for duplicate substats
                    if stat_name in used_stats:
                        messagebox.showerror("Error", f"Duplicate substat: {stat_name}\nEach substat can only appear once.")
                        return
                    used_stats.add(stat_name)
                    
                    try:
                        value = float(value_var.get()) if value_var.get() else 0.0
                        rolls = int(rolls_var.get()) if rolls_var.get() else 0
                        
                        # Validate rolls
                        if rolls < 0 or rolls > 5:
                            messagebox.showerror("Error", f"Rolls for {stat_name} must be between 0 and 5")
                            return
                        
                        # Validate value based on stat config
                        if stat_name in self.mathic_system.config["substats"]:
                            stat_config = self.mathic_system.config["substats"][stat_name]
                            max_possible = stat_config["max_value"]
                            if value > max_possible:
                                messagebox.showerror("Error", 
                                                   f"Value for {stat_name} ({value}) exceeds maximum ({max_possible})")
                                return
                        
                        # Create substat
                        from mathic.mathic_system import Substat
                        substat = Substat(stat_name, value, rolls)
                        new_substats.append(substat)
                        
                    except ValueError as e:
                        messagebox.showerror("Error", f"Invalid value for substat {i+1}: {e}")
                        return
            
            # Validate total rolls vs individual rolls
            total_individual_rolls = sum(substat.rolls_used for substat in new_substats)
            if total_individual_rolls != total_rolls:
                messagebox.showerror("Error", 
                                   f"Total rolls ({total_rolls}) doesn't match sum of individual rolls ({total_individual_rolls})")
                return
            
            # Create the module
            slot_position = len(self.mathic_system.modules) + 1
            module = self.mathic_system.create_module(module_type, slot_position, main_stat)
            
            if module:
                # Set the main stat value from the panel
                if main_stat_value > 0:
                    module.main_stat_value = main_stat_value
                
                # Set the substats from the editing panel
                module.substats = new_substats
                module.total_enhancement_rolls = total_rolls
                module.level = total_rolls
                
                self.refresh_module_list()
                self.refresh_slot_module_options()
                
                # Select the newly created module
                try:
                    new_idx = len(self.mathic_system.modules) - 1
                    self.module_listbox.selection_set(new_idx)
                    self.module_listbox.activate(new_idx)
                    self.module_listbox.see(new_idx)
                    self.display_module_details(module)
                except:
                    pass
                
                messagebox.showinfo("Success", f"Created new {module_type} module with custom values")
            else:
                messagebox.showerror("Error", "Failed to create module")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating module: {e}")
    
    def delete_module(self):
        """Delete selected module"""
        selection = self.module_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this module?"):
            idx = selection[0]
            module_id = list(self.mathic_system.modules.keys())[idx]
            del self.mathic_system.modules[module_id]
            self.refresh_module_list()
            self.refresh_slot_module_options()
    
    def enhance_module_random(self):
        """Randomly enhance selected module"""
        selection = self.module_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module to enhance")
            return
        
        idx = selection[0]
        module_id = list(self.mathic_system.modules.keys())[idx]
        module = self.mathic_system.modules[module_id]
        
        enhanced_stat = self.mathic_system.enhance_module_random_substat(module)
        if enhanced_stat:
            self.display_module_details(module)
            self.refresh_module_list()
            self.update_enhance_options()
            messagebox.showinfo("Success", f"Enhanced {enhanced_stat}")
        else:
            messagebox.showinfo("Info", "No substats can be enhanced further")
    
    def enhance_module_manual(self):
        """Open manual enhancement dialog"""
        selection = self.module_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module to enhance")
            return
        
        idx = selection[0]
        module_id = list(self.mathic_system.modules.keys())[idx]
        module = self.mathic_system.modules[module_id]
        
        # Update enhancement options for the selected module
        self.update_enhance_options()
        
        messagebox.showinfo("Manual Enhancement", 
                          f"Use the Manual Enhancement section below to enhance {module.module_type} substats.\n"
                          f"Remaining rolls: {module.max_total_rolls - module.total_enhancement_rolls}")
    
    # Enhance Simulator functions
    def refresh_enhance_modules(self):
        """Refresh the module list for enhance simulator"""
        module_options = []
        for module_id, module in self.mathic_system.modules.items():
            display_text = f"{module_id}: {module.module_type} - {module.main_stat}"
            module_options.append(display_text)
        
        self.enhance_module_combo.configure(values=module_options)
        if module_options and not self.enhance_module_var.get():
            self.enhance_module_var.set(module_options[0])
            self.on_enhance_module_select()
    
    def on_enhance_module_select(self, event=None):
        """Handle module selection in enhance simulator"""
        selection = self.enhance_module_var.get()
        if not selection:
            return
        
        module_id = selection.split(":")[0]
        if module_id in self.mathic_system.modules:
            module = self.mathic_system.modules[module_id]
            self.update_current_module_display(module)
            self.update_probability_display(module)
            self.update_value_analysis_display(module)
    
    def update_current_module_display(self, module):
        """Update current module information display"""
        self.current_module_text.config(state=tk.NORMAL)
        self.current_module_text.delete(1.0, tk.END)
        
        info_text = f"Module: {module.module_type}\n"
        info_text += f"Main Stat: {module.main_stat} ({int(module.main_stat_value)})\n"
        info_text += f"Level: {module.level} (Rolls: {module.total_enhancement_rolls}/{module.max_total_rolls})\n"
        info_text += f"Substats: {len(module.substats)}/4\n\n"
        
        if module.substats:
            info_text += "Current Substats:\n"
            for i, substat in enumerate(module.substats, 1):
                max_val = self.mathic_system.config["substats"][substat.stat_name]["max_value"]
                efficiency = substat.get_efficiency_percentage(max_val)
                info_text += f"{i}. {substat.stat_name}: {int(substat.current_value)} "
                info_text += f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}%)\n"
        else:
            info_text += "No substats yet\n"
        
        self.current_module_text.insert(1.0, info_text)
        self.current_module_text.config(state=tk.DISABLED)
    
    def update_probability_display(self, module):
        """Update probability display for next enhancement"""
        # Clear existing items
        for item in self.probability_tree.get_children():
            self.probability_tree.delete(item)
        
        probabilities = self.mathic_system.calculate_substat_probabilities(module)
        
        if probabilities:
            for stat_name, prob in probabilities.items():
                self.probability_tree.insert('', tk.END, text=stat_name, 
                                            values=(f"{prob*100:.1f}%",))
        else:
            self.probability_tree.insert('', tk.END, text="No enhancements possible", 
                                        values=("0.0%",))
    
    def update_value_analysis_display(self, module):
        """Update module value analysis display"""
        self.value_analysis_text.config(state=tk.NORMAL)
        self.value_analysis_text.delete(1.0, tk.END)
        
        value_data = self.mathic_system.calculate_module_value(module)
        
        analysis_text = "MODULE VALUE ANALYSIS\n"
        analysis_text += "="*30 + "\n\n"
        
        analysis_text += f"Total Value Score: {value_data['total_value']:.2f}\n"
        analysis_text += f"Overall Efficiency: {value_data['efficiency']:.1f}%\n"
        analysis_text += f"Roll Efficiency: {value_data['roll_efficiency']:.1f}%\n\n"
        
        if value_data['details']:
            analysis_text += "Substat Breakdown:\n"
            analysis_text += "-" * 20 + "\n"
            
            for stat_name, details in value_data['details'].items():
                analysis_text += f"{stat_name}:\n"
                analysis_text += f"  Value: {int(details['current_value'])}\n"
                analysis_text += f"  Efficiency: {details['efficiency']:.1f}%\n"
                analysis_text += f"  Rolls: {details['rolls_used']}/5\n"
                analysis_text += f"  Score: {details['substat_value']:.2f}\n"
                analysis_text += f"  Importance: {details['importance']:.1f}\n\n"
        
        enhancement_potential = module.max_total_rolls - module.total_enhancement_rolls
        if enhancement_potential > 0:
            analysis_text += f"Enhancement Potential:\n"
            analysis_text += f"Remaining rolls: {enhancement_potential}\n"
            if len(module.substats) < 4:
                new_substats_possible = min(4 - len(module.substats), enhancement_potential)
                analysis_text += f"New substats possible: {new_substats_possible}\n"
        else:
            analysis_text += "Module fully enhanced\n"
        
        self.value_analysis_text.insert(1.0, analysis_text)
        self.value_analysis_text.config(state=tk.DISABLED)
    
    def enhance_once(self):
        """Enhance the selected module once"""
        self.perform_enhancement(1)
    
    def enhance_five_times(self):
        """Enhance the selected module 5 times"""
        self.perform_enhancement(5)
    
    def enhance_to_max(self):
        """Enhance the selected module to maximum"""
        selection = self.enhance_module_var.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module")
            return
        
        module_id = selection.split(":")[0]
        if module_id in self.mathic_system.modules:
            module = self.mathic_system.modules[module_id]
            remaining_rolls = module.max_total_rolls - module.total_enhancement_rolls
            if remaining_rolls > 0:
                self.perform_enhancement(remaining_rolls)
            else:
                messagebox.showinfo("Info", "Module is already at maximum enhancement")
    
    def perform_enhancement(self, times):
        """Perform enhancement multiple times and log results"""
        selection = self.enhance_module_var.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a module")
            return
        
        module_id = selection.split(":")[0]
        if module_id not in self.mathic_system.modules:
            messagebox.showerror("Error", "Module not found")
            return
        
        module = self.mathic_system.modules[module_id]
        
        # Check if enhancement is possible
        if not module.can_be_enhanced():
            messagebox.showinfo("Info", "Module cannot be enhanced further")
            return
        
        # Log enhancement start
        self.enhancement_log.config(state=tk.NORMAL)
        self.enhancement_log.insert(tk.END, f"\n--- Starting {times} enhancement(s) for {module.module_type} ---\n")
        
        success_count = 0
        for i in range(times):
            if not module.can_be_enhanced():
                self.enhancement_log.insert(tk.END, f"Enhancement {i+1}: Module fully enhanced\n")
                break
            
            enhanced_stat = self.mathic_system.enhance_module_random_substat(module)
            if enhanced_stat:
                success_count += 1
                if enhanced_stat.startswith("New substat:"):
                    self.enhancement_log.insert(tk.END, f"Enhancement {i+1}: {enhanced_stat}\n")
                else:
                    # Get the actual roll value for logging
                    substat = module.get_substat(enhanced_stat)
                    if substat:
                        self.enhancement_log.insert(tk.END, 
                                                   f"Enhancement {i+1}: Enhanced {enhanced_stat} "
                                                   f"(Current: {int(substat.current_value)}, "
                                                   f"Rolls: {substat.rolls_used}/5)\n")
            else:
                self.enhancement_log.insert(tk.END, f"Enhancement {i+1}: Failed\n")
                break
        
        self.enhancement_log.insert(tk.END, f"Completed {success_count}/{times} enhancements\n")
        self.enhancement_log.insert(tk.END, f"Module level: {module.level} "
                                            f"(Rolls: {module.total_enhancement_rolls}/{module.max_total_rolls})\n")
        self.enhancement_log.config(state=tk.DISABLED)
        self.enhancement_log.see(tk.END)
        
        # Update displays
        self.update_current_module_display(module)
        self.update_probability_display(module)
        self.update_value_analysis_display(module)
        
        # Update module list in Module Editor if it exists
        if hasattr(self, 'module_listbox'):
            self.refresh_module_list()
    
    def enhance_substat_manual(self):
        """Legacy manual enhancement function - redirects to Enhance Simulator"""
        messagebox.showinfo("Feature Moved", 
                          "Manual enhancement has been moved to the Enhance Simulator tab.\n"
                          "Please use Mathic System > Enhance Simulator for advanced enhancement features.")
    
    def update_enhance_options(self):
        """Update enhancement options based on selected module (legacy function - no longer needed)"""
        # This function is kept for compatibility but no longer performs any operations
        # since the enhancement UI has been moved to Enhance Simulator tab
        pass
    
    def refresh_loadout_list(self):
        """Refresh the loadout list"""
        loadouts = list(self.mathic_system.mathic_loadouts.keys())
        self.loadout_combo.configure(values=loadouts)
        if loadouts and not self.loadout_var.get():
            self.loadout_var.set(loadouts[0])
            self.on_loadout_select()
    
    def refresh_slot_module_options(self):
        """Refresh module options for all slots with type restrictions"""
        # Get slot type restrictions from config
        slot_restrictions = {
            1: ["mask"],
            2: ["transistor"], 
            3: ["wristwheel"],
            4: ["core"],
            5: ["core"],
            6: ["core"]
        }
        
        for slot_id in range(1, 7):
            allowed_types = slot_restrictions.get(slot_id, [])
            
            # Filter modules by allowed types for this slot
            slot_module_options = ["None"]
            for mid, mod in self.mathic_system.modules.items():
                if mod.module_type in allowed_types:
                    slot_module_options.append(f"{mid}: {mod.module_type} - {mod.main_stat}")
            
            self.slot_combos[slot_id].configure(values=slot_module_options)
    
    def on_loadout_select(self, event=None):
        """Handle loadout selection"""
        loadout_name = self.loadout_var.get()
        if loadout_name in self.mathic_system.mathic_loadouts:
            loadout = self.mathic_system.mathic_loadouts[loadout_name]
            
            # Update slot displays
            for slot_id in range(1, 7):
                module_id = loadout.get(slot_id)
                if module_id and module_id in self.mathic_system.modules:
                    module = self.mathic_system.modules[module_id]
                    self.slot_vars[slot_id].set(f"{module_id}: {module.module_type} - {module.main_stat}")
                    
                    # Update substats display (vertical layout)
                    if hasattr(self, 'slot_substats_labels') and slot_id in self.slot_substats_labels:
                        for i, substat_label in enumerate(self.slot_substats_labels[slot_id]):
                            if i < len(module.substats):
                                substat = module.substats[i]
                                text = f"{substat.stat_name}: +{int(substat.current_value)}"
                                substat_label.config(text=text)
                            else:
                                substat_label.config(text="")
                else:
                    self.slot_vars[slot_id].set("None")
                    
                    # Clear substats display
                    if hasattr(self, 'slot_substats_labels') and slot_id in self.slot_substats_labels:
                        for substat_label in self.slot_substats_labels[slot_id]:
                            substat_label.config(text="")
            
            self.refresh_slot_module_options()
            self.update_loadout_stats()
    
    def on_slot_module_change(self, slot_id):
        """Handle slot module assignment"""
        loadout_name = self.loadout_var.get()
        if not loadout_name:
            return
        
        selection = self.slot_vars[slot_id].get()
        
        if selection == "None":
            # Clear slot
            self.mathic_system.mathic_loadouts[loadout_name][slot_id] = None
            
            # Clear substats display
            if hasattr(self, 'slot_substats_labels') and slot_id in self.slot_substats_labels:
                for substat_label in self.slot_substats_labels[slot_id]:
                    substat_label.config(text="")
        else:
            # Assign module
            module_id = selection.split(":")[0]
            if module_id in self.mathic_system.modules:
                self.mathic_system.mathic_loadouts[loadout_name][slot_id] = module_id
                module = self.mathic_system.modules[module_id]
                
                # Update substats display (vertical layout)
                if hasattr(self, 'slot_substats_labels') and slot_id in self.slot_substats_labels:
                    for i, substat_label in enumerate(self.slot_substats_labels[slot_id]):
                        if i < len(module.substats):
                            substat = module.substats[i]
                            text = f"{substat.stat_name}: +{int(substat.current_value)}"
                            substat_label.config(text=text)
                        else:
                            substat_label.config(text="")
        
        self.update_loadout_stats()
    
    def new_loadout(self):
        """Create a new loadout"""
        from tkinter.simpledialog import askstring
        name = askstring("New Loadout", "Enter loadout name:")
        if name and name not in self.mathic_system.mathic_loadouts:
            self.mathic_system.create_mathic_loadout(name)
            self.refresh_loadout_list()
            self.loadout_var.set(name)
            self.on_loadout_select()
        elif name in self.mathic_system.mathic_loadouts:
            messagebox.showwarning("Warning", "Loadout name already exists")
    
    def delete_loadout(self):
        """Delete selected loadout"""
        loadout_name = self.loadout_var.get()
        if not loadout_name:
            return
        
        if messagebox.askyesno("Confirm", f"Delete loadout '{loadout_name}'?"):
            del self.mathic_system.mathic_loadouts[loadout_name]
            self.refresh_loadout_list()
    
    def update_loadout_stats(self):
        """Update loadout total stats display"""
        loadout_name = self.loadout_var.get()
        if not loadout_name or loadout_name not in self.mathic_system.mathic_loadouts:
            return
        
        loadout_modules = self.mathic_system.get_loadout_modules(loadout_name)
        total_stats = {}
        
        # Calculate total stats
        for slot_id, module in loadout_modules.items():
            if module:
                # Add main stat
                if module.main_stat in total_stats:
                    total_stats[module.main_stat] += module.main_stat_value
                else:
                    total_stats[module.main_stat] = module.main_stat_value
                
                # Add substats
                for substat in module.substats:
                    if substat.stat_name:
                        if substat.stat_name in total_stats:
                            total_stats[substat.stat_name] += substat.current_value
                        else:
                            total_stats[substat.stat_name] = substat.current_value
        
        # Display stats
        self.stats_summary_text.config(state=tk.NORMAL)
        self.stats_summary_text.delete(1.0, tk.END)
        
        if total_stats:
            stats_text = "Total Stats:\n" + "="*30 + "\n"
            
            # Separate flat and percentage stats
            flat_stats = ["ATK", "HP", "DEF"]
            percent_stats = ["ATK%", "HP%", "DEF%", "CRIT Rate", "CRIT DMG", 
                           "Effect ACC", "Effect RES", "SPD"]
            
            stats_text += "\nFlat Stats:\n"
            for stat in flat_stats:
                if stat in total_stats:
                    stats_text += f"  {stat}: +{int(total_stats[stat])}\n"
            
            stats_text += "\nPercentage Stats:\n"
            for stat in percent_stats:
                if stat in total_stats:
                    stats_text += f"  {stat}: +{total_stats[stat]:.1f}%\n"
        else:
            stats_text = "No modules equipped"
        
        self.stats_summary_text.insert(1.0, stats_text)
        self.stats_summary_text.config(state=tk.DISABLED)
    
    def update_system_overview(self):
        """Update system overview display"""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        
        overview = "Mathic System Overview\n" + "="*50 + "\n\n"
        
        # Module statistics
        module_count = len(self.mathic_system.modules)
        loadout_count = len(self.mathic_system.mathic_loadouts)
        
        overview += f"Total Modules: {module_count}\n"
        overview += f"Total Loadouts: {loadout_count}\n\n"
        
        if self.mathic_system.modules:
            # Module type distribution
            type_counts = {}
            level_sum = 0
            max_level = 0
            
            for module in self.mathic_system.modules.values():
                type_counts[module.module_type] = type_counts.get(module.module_type, 0) + 1
                level_sum += module.level
                max_level = max(max_level, module.level)
            
            overview += "Module Distribution:\n"
            for module_type, count in sorted(type_counts.items()):
                overview += f"  {module_type}: {count}\n"
            
            avg_level = level_sum / module_count if module_count > 0 else 0
            overview += f"\nEnhancement Stats:\n"
            overview += f"  Average Level: {avg_level:.1f}\n"
            overview += f"  Highest Level: {max_level}\n\n"
            
            # Loadout information
            overview += "Loadouts:\n"
            for loadout_name, loadout in self.mathic_system.mathic_loadouts.items():
                equipped_count = sum(1 for module_id in loadout.values() if module_id)
                overview += f"  {loadout_name}: {equipped_count}/6 slots\n"
        else:
            overview += "No modules created yet.\n"
            overview += "Use the Module Editor to create your first module!\n"
        
        self.overview_text.insert(1.0, overview)
        self.overview_text.config(state=tk.DISABLED)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CharacterPokedexUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    main()
