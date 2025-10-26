#!/usr/bin/env python3
"""
Character View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView


class CharacterListView(BaseView):
    """View for character list and details"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.search_var = tk.StringVar()
        self.rarity_var = tk.StringVar(value="All")
        self.element_var = tk.StringVar(value="All")
        
        # Character details widgets
        self.char_name_label = None
        self.rarity_label = None
        self.element_label = None
        self.stats_text = None
        self.skills_text = None
        self.dupes_text = None
        
    def create_widgets(self):
        """Create character list and details widgets"""
        # Configure grid weights
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Left panel - Character list
        left_frame = ttk.LabelFrame(self.parent, text="Character List", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.rowconfigure(1, weight=1)
        
        # Search and filter controls
        self._create_search_controls(left_frame)
        
        # Character treeview
        self._create_character_list(left_frame)
        
        # Right panel - Character details
        right_frame = ttk.LabelFrame(self.parent, text="Character Details", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Character info and details tabs
        self._create_character_details(right_frame)
        
        # Action buttons
        self._create_action_buttons()
        
        return self.parent
    
    def _create_search_controls(self, parent):
        """Create search and filter controls"""
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        search_btn = ttk.Button(search_frame, text="Search", 
                               command=lambda: self.controller.search_characters() if self.controller else None)
        search_btn.grid(row=0, column=2)
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        ttk.Label(filter_frame, text="Rarity:").grid(row=0, column=0, padx=(0, 5))
        rarity_combo = ttk.Combobox(filter_frame, textvariable=self.rarity_var, 
                                   values=["All", "SSR", "SR", "R"], state="readonly", width=8)
        rarity_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(filter_frame, text="Element:").grid(row=0, column=2, padx=(0, 5))
        element_combo = ttk.Combobox(filter_frame, textvariable=self.element_var,
                                    values=["All", "Disorder", "Reason", "Hollow", "Odd", "Constant"],
                                    state="readonly", width=10)
        element_combo.grid(row=0, column=3)
        
        # Bind filter events
        rarity_combo.bind('<<ComboboxSelected>>', lambda e: self.controller.filter_characters() if self.controller else None)
        element_combo.bind('<<ComboboxSelected>>', lambda e: self.controller.filter_characters() if self.controller else None)
        self.search_entry.bind('<Return>', lambda e: self.controller.search_characters() if self.controller else None)
    
    def _create_character_list(self, parent):
        """Create character list treeview"""
        list_frame = ttk.Frame(parent)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
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
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.character_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.character_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.character_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.character_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind selection event
        self.character_tree.bind('<<TreeviewSelect>>', 
                                lambda e: self.controller.on_character_select() if self.controller else None)
    
    def _create_character_details(self, parent):
        """Create character details display"""
        # Character info frame
        info_frame = ttk.Frame(parent)
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
        
        # Details notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self._create_stats_tab()
        self._create_skills_tab()
        self._create_dupes_tab()
    
    def _create_stats_tab(self):
        """Create stats tab"""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Stats")
        
        stats_text_frame = ttk.Frame(self.stats_frame)
        stats_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_text_frame.columnconfigure(0, weight=1)
        stats_text_frame.rowconfigure(0, weight=1)
        
        self.stats_text = tk.Text(stats_text_frame, wrap=tk.WORD, height=15, width=40)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_scrollbar = ttk.Scrollbar(stats_text_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.rowconfigure(0, weight=1)
    
    def _create_skills_tab(self):
        """Create skills tab"""
        self.skills_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.skills_frame, text="Skills")
        
        skills_text_frame = ttk.Frame(self.skills_frame)
        skills_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        skills_text_frame.columnconfigure(0, weight=1)
        skills_text_frame.rowconfigure(0, weight=1)
        
        self.skills_text = tk.Text(skills_text_frame, wrap=tk.WORD, height=15, width=40)
        self.skills_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        skills_scrollbar = ttk.Scrollbar(skills_text_frame, orient=tk.VERTICAL, command=self.skills_text.yview)
        skills_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.skills_text.configure(yscrollcommand=skills_scrollbar.set)
        
        self.skills_frame.columnconfigure(0, weight=1)
        self.skills_frame.rowconfigure(0, weight=1)
    
    def _create_dupes_tab(self):
        """Create dupes tab"""
        self.dupes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dupes_frame, text="Dupes/Prowess")
        
        dupes_text_frame = ttk.Frame(self.dupes_frame)
        dupes_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dupes_text_frame.columnconfigure(0, weight=1)
        dupes_text_frame.rowconfigure(0, weight=1)
        
        self.dupes_text = tk.Text(dupes_text_frame, wrap=tk.WORD, height=15, width=40)
        self.dupes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        dupes_scrollbar = ttk.Scrollbar(dupes_text_frame, orient=tk.VERTICAL, command=self.dupes_text.yview)
        dupes_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dupes_text.configure(yscrollcommand=dupes_scrollbar.set)
        
        self.dupes_frame.columnconfigure(0, weight=1)
        self.dupes_frame.rowconfigure(0, weight=1)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        # This will be added to the main frame by the controller
        pass
    
    def update_display(self, data):
        """Update character list display"""
        # Clear existing items
        for item in self.character_tree.get_children():
            self.character_tree.delete(item)
        
        # Add characters to tree
        for char in data:
            values = (
                char.get('name', 'Unknown'),
                char.get('rarity', 'Unknown'),
                char.get('element', 'Unknown'),
                char.get('updated_at', 'Unknown')
            )
            self.character_tree.insert('', tk.END, values=values)
    
    def update_character_details(self, character_data):
        """Update character details display"""
        if not character_data:
            self.clear_character_details()
            return
        
        # Update basic info
        basic_info = character_data.get('basic_info', {})
        self.char_name_label.config(text=basic_info.get('name', 'Unknown'))
        self.rarity_label.config(text=basic_info.get('rarity', 'Unknown'))
        self.element_label.config(text=basic_info.get('element', 'Unknown'))
        
        # Update tabs
        self._update_stats_display(character_data.get('stats', {}))
        self._update_skills_display(character_data.get('skills', []))
        self._update_dupes_display(character_data.get('dupes', {}))
    
    def _update_stats_display(self, stats):
        """Update stats display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "CHARACTER STATS\n")
        self.stats_text.insert(tk.END, "="*50 + "\n\n")
        
        for stat_name, stat_data in stats.items():
            if isinstance(stat_data, dict):
                self.stats_text.insert(tk.END, f"{stat_name.upper()}:\n")
                for key, value in stat_data.items():
                    self.stats_text.insert(tk.END, f"  {key}: {value}\n")
                self.stats_text.insert(tk.END, "\n")
            else:
                self.stats_text.insert(tk.END, f"{stat_name}: {stat_data}\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def _update_skills_display(self, skills):
        """Update skills display"""
        self.skills_text.config(state=tk.NORMAL)
        self.skills_text.delete(1.0, tk.END)
        
        self.skills_text.insert(tk.END, "CHARACTER SKILLS\n")
        self.skills_text.insert(tk.END, "="*50 + "\n\n")
        
        for i, skill in enumerate(skills, 1):
            self.skills_text.insert(tk.END, f"Skill {i}: {skill.get('name', 'Unknown')}\n")
            self.skills_text.insert(tk.END, f"Description: {skill.get('description', 'No description')}\n\n")
        
        self.skills_text.config(state=tk.DISABLED)
    
    def _update_dupes_display(self, dupes):
        """Update dupes display"""
        self.dupes_text.config(state=tk.NORMAL)
        self.dupes_text.delete(1.0, tk.END)
        
        self.dupes_text.insert(tk.END, "CHARACTER DUPES/PROWESS\n")
        self.dupes_text.insert(tk.END, "="*50 + "\n\n")
        
        for dupe_id, dupe_data in dupes.items():
            self.dupes_text.insert(tk.END, f"{dupe_id}: {dupe_data.get('description', 'No description')}\n\n")
        
        self.dupes_text.config(state=tk.DISABLED)
    
    def clear_character_details(self):
        """Clear character details display"""
        self.char_name_label.config(text="Select a character")
        self.rarity_label.config(text="-")
        self.element_label.config(text="-")
        
        for text_widget in [self.stats_text, self.skills_text, self.dupes_text]:
            if text_widget:
                text_widget.config(state=tk.NORMAL)
                text_widget.delete(1.0, tk.END)
                text_widget.config(state=tk.DISABLED)
    
    def get_selected_character(self):
        """Get currently selected character"""
        selection = self.character_tree.selection()
        if selection:
            item = self.character_tree.item(selection[0])
            return item['values'][0]  # Return character name
        return None
    
    def get_search_term(self):
        """Get current search term"""
        return self.search_var.get().strip()
    
    def get_filter_values(self):
        """Get current filter values"""
        return {
            'rarity': self.rarity_var.get(),
            'element': self.element_var.get()
        }
