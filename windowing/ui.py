import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_routing import CharacterDatabase
from html_parser.parse_char import PlumeParser


class CharacterPokedexUI:
    """Character Pokedex GUI using tkinter"""
    
    def __init__(self, root):
        """Initialize the UI"""
        self.root = root
        self.root.title("Etheria Character Pokedex")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db = CharacterDatabase()
        
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
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Etheria Character Pokedex", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Character list
        left_frame = ttk.LabelFrame(main_frame, text="Character List", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
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
        right_frame = ttk.LabelFrame(main_frame, text="Character Details", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
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
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(button_frame, text="Import HTML", command=self.import_html).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Import JSON", command=self.import_json).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export JSON", command=self.export_json).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Character", command=self.delete_character).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh List", command=self.refresh_character_list).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
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
            parser = PlumeParser(file_path)
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
