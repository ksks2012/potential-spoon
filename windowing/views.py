#!/usr/bin/env python3
"""
Views for the Etheria Simulation Suite
Contains UI components separated from business logic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from abc import ABC, abstractmethod


class BaseView(ABC):
    """Abstract base class for all views"""
    
    def __init__(self, parent):
        self.parent = parent
        self.controller = None
        
    def set_controller(self, controller):
        """Set the controller for this view"""
        self.controller = controller
    
    @abstractmethod
    def create_widgets(self):
        """Create and layout widgets"""
        pass
    
    @abstractmethod
    def update_display(self, data):
        """Update display with new data"""
        pass


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
            # Handle both formats: direct fields or nested basic_info
            if 'basic_info' in char:
                name = char['basic_info']['name']
                rarity = char['basic_info']['rarity']
                element = char['basic_info']['element']
            else:
                name = char.get('name', 'Unknown')
                rarity = char.get('rarity', 'Unknown')
                element = char.get('element', 'Unknown')
            
            self.character_tree.insert('', 'end', values=(
                name,
                rarity,
                element,
                char.get('updated_at', char.get('last_updated', 'Unknown'))
            ))
    
    def update_character_details(self, character_data):
        """Update character details display"""
        if not character_data:
            self.clear_character_details()
            return
        
        # Update basic info
        basic_info = character_data['basic_info']
        self.char_name_label.config(text=basic_info['name'])
        self.rarity_label.config(text=basic_info['rarity'])
        self.element_label.config(text=basic_info['element'])
        
        # Update tabs
        self._update_stats_display(character_data['stats'])
        self._update_skills_display(character_data['skills'])
        self._update_dupes_display(character_data['dupes'])
    
    def _update_stats_display(self, stats):
        """Update stats display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "CHARACTER STATS\n")
        self.stats_text.insert(tk.END, "="*50 + "\n\n")
        
        for stat_name, stat_data in stats.items():
            if isinstance(stat_data, dict):
                self.stats_text.insert(tk.END, f"{stat_name}:\n")
                for key, value in stat_data.items():
                    self.stats_text.insert(tk.END, f"  {key}: {value}\n")
            else:
                self.stats_text.insert(tk.END, f"{stat_name}: {stat_data}\n")
            self.stats_text.insert(tk.END, "\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def _update_skills_display(self, skills):
        """Update skills display"""
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
    
    def _update_dupes_display(self, dupes):
        """Update dupes display"""
        self.dupes_text.config(state=tk.NORMAL)
        self.dupes_text.delete(1.0, tk.END)
        
        self.dupes_text.insert(tk.END, "CHARACTER DUPES/PROWESS\n")
        self.dupes_text.insert(tk.END, "="*50 + "\n\n")
        
        for dupe_id, dupe_data in dupes.items():
            if isinstance(dupe_data, dict):
                dupe_name = dupe_data.get('name', dupe_id)
                dupe_effect = dupe_data.get('effect', 'No description available')
            else:
                dupe_name = str(dupe_data)
                dupe_effect = 'No description available'
            
            self.dupes_text.insert(tk.END, f"{dupe_id} - {dupe_name}\n")
            self.dupes_text.insert(tk.END, f"Effect: {dupe_effect}\n")
            self.dupes_text.insert(tk.END, "-" * 40 + "\n\n")
        
        self.dupes_text.config(state=tk.DISABLED)
    
    def clear_character_details(self):
        """Clear character details display"""
        self.char_name_label.config(text="Select a character")
        self.rarity_label.config(text="-")
        self.element_label.config(text="-")
        
        for text_widget in [self.stats_text, self.skills_text, self.dupes_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
    
    def get_selected_character(self):
        """Get currently selected character"""
        selection = self.character_tree.selection()
        if selection:
            item = self.character_tree.item(selection[0])
            if item and 'values' in item and item['values']:
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


class ModuleEditorView(BaseView):
    """View for module editing"""
    
    def __init__(self, parent):
        super().__init__(parent)
        # Get root window reference
        self.root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else None
        
        self.module_type_var = tk.StringVar(value="mask")
        self.main_stat_var = tk.StringVar()
        self.main_stat_value_var = tk.StringVar()
        self.total_rolls_var = tk.StringVar(value="0")
        
        # Substat variables
        self._create_substat_vars()
        
        # UI elements
        self.module_listbox = None
        self.substats_tree = None
        self.substat_controls = []
        
        # State tracking
        self.current_selected_module_id = None
        self.adjusting_rolls = False
        self.pending_warning = None
        self.rolls_change_depth = 0
    
    def _create_substat_vars(self):
        """Create substat StringVar objects"""
        self.substat1_type_var = tk.StringVar()
        self.substat1_value_var = tk.StringVar()
        self.substat1_rolls_var = tk.StringVar(value="0")
        
        self.substat2_type_var = tk.StringVar()
        self.substat2_value_var = tk.StringVar()
        self.substat2_rolls_var = tk.StringVar(value="0")
        
        self.substat3_type_var = tk.StringVar()
        self.substat3_value_var = tk.StringVar()
        self.substat3_rolls_var = tk.StringVar(value="0")
        
        self.substat4_type_var = tk.StringVar()
        self.substat4_value_var = tk.StringVar()
        self.substat4_rolls_var = tk.StringVar(value="0")
    
    def create_widgets(self):
        """Create module editor widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1) 
        self.parent.rowconfigure(0, weight=1)
        
        # Left panel - Module list
        self._create_module_list_panel()
        
        # Right panel - Module details
        self._create_module_details_panel()
        
        return self.parent
    
    def _create_module_list_panel(self):
        """Create module list panel"""
        left_panel = ttk.LabelFrame(self.parent, text="Modules", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Module list
        self.module_listbox = tk.Listbox(left_panel, height=15)
        self.module_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.module_listbox.bind('<<ListboxSelect>>', 
                                lambda e: self.controller.on_module_select() if self.controller else None)
        
        module_scroll = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.module_listbox.yview)
        module_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.module_listbox.configure(yscrollcommand=module_scroll.set)
        
        # Module controls
        controls_frame = ttk.Frame(left_panel)
        controls_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(controls_frame, text="New Module", 
                  command=lambda: self.controller.new_module() if self.controller else None).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(controls_frame, text="Delete Module", 
                  command=lambda: self.controller.delete_module() if self.controller else None).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(controls_frame, text="Manual Enhance", 
                  command=lambda: self.controller.enhance_module_manual() if self.controller else None).grid(row=0, column=2)
        
        # Configure grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
    
    def _create_module_details_panel(self):
        """Create module details panel"""
        right_panel = ttk.LabelFrame(self.parent, text="Module Details", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Module type and main stat
        self._create_module_type_controls(right_panel)
        
        # Substats display
        self._create_substats_display(right_panel)
        
        # Module editing controls
        self._create_editing_controls(right_panel)
        
        # Configure grid weights
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
    
    def _create_module_type_controls(self, parent):
        """Create module type and main stat controls"""
        type_frame = ttk.Frame(parent)
        type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(type_frame, text="Type:").grid(row=0, column=0, padx=(0, 5))
        self.module_type_combo = ttk.Combobox(type_frame, textvariable=self.module_type_var,
                                            values=["mask", "transistor", "wristwheel", "core"],
                                            state="readonly", width=15)
        self.module_type_combo.grid(row=0, column=1, padx=(0, 10))
        self.module_type_combo.bind('<<ComboboxSelected>>', 
                                   lambda e: self.controller.on_module_type_change() if self.controller else None)
        
        ttk.Label(type_frame, text="Main Stat:").grid(row=0, column=2, padx=(0, 5))
        self.main_stat_combo = ttk.Combobox(type_frame, textvariable=self.main_stat_var,
                                          state="readonly", width=12)
        self.main_stat_combo.grid(row=0, column=3, padx=(0, 10))
        self.main_stat_combo.bind('<<ComboboxSelected>>', 
                                 lambda e: self.controller.on_main_stat_change() if self.controller else None)
        
        ttk.Label(type_frame, text="Value:").grid(row=0, column=4, padx=(0, 5))
        self.main_stat_entry = ttk.Entry(type_frame, textvariable=self.main_stat_value_var, 
                                       width=8, state="readonly")
        self.main_stat_entry.grid(row=0, column=5)
    
    def _create_substats_display(self, parent):
        """Create substats display tree"""
        substats_frame = ttk.LabelFrame(parent, text="Substats", padding="10")
        substats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
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
        
        # Configure grid weights
        substats_frame.columnconfigure(0, weight=1)
        substats_frame.rowconfigure(0, weight=1)
    
    def _create_editing_controls(self, parent):
        """Create module editing controls"""
        edit_frame = ttk.LabelFrame(parent, text="Module Editing", padding="10")
        edit_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Total rolls display (read-only)
        ttk.Label(edit_frame, text="Total Rolls:").grid(row=0, column=0, padx=(0, 5))
        self.total_rolls_label = ttk.Label(edit_frame, textvariable=self.total_rolls_var,
                                         font=('Arial', 10, 'bold'), foreground="darkblue")
        self.total_rolls_label.grid(row=0, column=1, padx=(0, 10))
        ttk.Label(edit_frame, text="(auto-calculated)", font=('Arial', 8), foreground="gray").grid(row=0, column=2, padx=(0, 10))
        
        # Substat editing controls
        ttk.Label(edit_frame, text="Edit Substat:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        
        # Create substat control frames
        self._create_substat_controls(edit_frame)
        
        # Apply changes button
        ttk.Button(edit_frame, text="Apply Changes", 
                  command=lambda: self.controller.apply_module_changes() if self.controller else None).grid(row=6, column=0, pady=(10, 0))
    
    def _create_substat_controls(self, parent):
        """Create individual substat controls"""
        substat_vars = [
            (self.substat1_type_var, self.substat1_value_var, self.substat1_rolls_var),
            (self.substat2_type_var, self.substat2_value_var, self.substat2_rolls_var),
            (self.substat3_type_var, self.substat3_value_var, self.substat3_rolls_var),
            (self.substat4_type_var, self.substat4_value_var, self.substat4_rolls_var),
        ]
        
        self.substat_controls = []
        
        for i, (type_var, value_var, rolls_var) in enumerate(substat_vars):
            row = 2 + i
            
            # Create frame for this substat
            substat_frame = ttk.Frame(parent)
            substat_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5 if i > 0 else 0, 0))
            
            # Label
            ttk.Label(substat_frame, text=f"{i+1}:").grid(row=0, column=0, padx=(0, 5))
            
            # Type combo
            type_combo = ttk.Combobox(substat_frame, textvariable=type_var, width=12, state="readonly")
            type_combo.grid(row=0, column=1, padx=(0, 5))
            
            # Value combo
            value_combo = ttk.Combobox(substat_frame, textvariable=value_var, width=8)
            value_combo.grid(row=0, column=2, padx=(0, 5))
            
            # Rolls spinbox
            rolls_spinbox = ttk.Spinbox(substat_frame, textvariable=rolls_var, from_=0, to=5, width=5)
            rolls_spinbox.grid(row=0, column=3)
            
            # Store controls for easy access
            self.substat_controls.append((type_combo, value_combo, rolls_spinbox, type_var, value_var, rolls_var))
            
            # Bind events
            substat_index = i + 1
            type_combo.bind('<<ComboboxSelected>>', 
                           lambda e, idx=substat_index: self.controller.on_substat_type_change(idx) if self.controller else None)
            type_var.trace('w', 
                          lambda *args, idx=substat_index: self.controller.on_substat_type_change(idx) if self.controller else None)
            rolls_var.trace('w', 
                           lambda *args, idx=substat_index: self.controller.on_substat_rolls_change(idx) if self.controller else None)
    
    def update_display(self, modules):
        """Update module list display"""
        self.module_listbox.delete(0, tk.END)
        for module_id, module in modules.items():
            display_text = f"{module.module_type} - {module.main_stat} ({module.level})"
            self.module_listbox.insert(tk.END, display_text)
    
    def update_module_details(self, module):
        """Update module details display"""
        if not module:
            return
        
        # Update basic info
        self.module_type_var.set(module.module_type)
        self.main_stat_var.set(module.main_stat)
        self.main_stat_value_var.set(str(module.main_stat_value))
        
        # Update substats tree
        for item in self.substats_tree.get_children():
            self.substats_tree.delete(item)
        
        for substat in module.substats:
            if substat.stat_name:
                efficiency = f"{(substat.current_value / (substat.rolls_used * 10)) * 100:.1f}%" if substat.rolls_used > 0 else "0%"
                self.substats_tree.insert('', 'end', values=(
                    substat.stat_name,
                    int(substat.current_value),
                    substat.rolls_used,
                    efficiency
                ))
        
        # Update editing controls
        self.update_editing_controls(module)
    
    def update_editing_controls(self, module):
        """Update editing controls with module data"""
        # Set substat data
        for i in range(4):
            combo, value_combo, spinbox, type_var, value_var, rolls_var = self.substat_controls[i]
            if i < len(module.substats):
                substat = module.substats[i]
                type_var.set(substat.stat_name or "")
                value_var.set(str(int(substat.current_value)) if substat.current_value else "")
                rolls_var.set(str(substat.rolls_used))
            else:
                type_var.set("")
                value_var.set("")
                rolls_var.set("0")
        
        # Update total rolls display
        self.update_total_rolls_display()
    
    def update_main_stat_options(self, options):
        """Update main stat combo options"""
        self.main_stat_combo.configure(values=options)
        if options:
            self.main_stat_var.set(options[0])
    
    def update_substat_options(self, options):
        """Update substat combo options"""
        for combo, _, _, _, _, _ in self.substat_controls:
            combo.configure(values=options)
    
    def update_substat_value_options(self, substat_index, options):
        """Update value options for specific substat"""
        if 0 <= substat_index - 1 < len(self.substat_controls):
            _, value_combo, _, _, _, _ = self.substat_controls[substat_index - 1]
            value_combo.configure(values=options)
    
    def update_total_rolls_display(self):
        """Update total rolls display"""
        try:
            total = 0
            for _, _, _, type_var, _, rolls_var in self.substat_controls:
                if type_var.get():  # Only count non-empty substats
                    total += int(rolls_var.get() or 0)
            self.total_rolls_var.set(str(total))
        except ValueError:
            self.total_rolls_var.set("0")
    
    def get_selected_module_index(self):
        """Get selected module index"""
        selection = self.module_listbox.curselection()
        return selection[0] if selection else None
    
    def get_module_form_data(self):
        """Get current form data"""
        substats_data = []
        for type_var, value_var, rolls_var in [(self.substat1_type_var, self.substat1_value_var, self.substat1_rolls_var),
                                              (self.substat2_type_var, self.substat2_value_var, self.substat2_rolls_var),
                                              (self.substat3_type_var, self.substat3_value_var, self.substat3_rolls_var),
                                              (self.substat4_type_var, self.substat4_value_var, self.substat4_rolls_var)]:
            substats_data.append({
                'stat_name': type_var.get(),
                'current_value': float(value_var.get()) if value_var.get() else 0,
                'rolls_used': int(rolls_var.get()) if rolls_var.get() else 0,
                'rolls': int(rolls_var.get()) if rolls_var.get() else 0
            })
        
        return {
            'module_type': self.module_type_var.get(),
            'main_stat': self.main_stat_var.get(),
            'main_stat_value': self.main_stat_value_var.get(),
            'substats_data': substats_data
        }


class MainView:
    """Main application view that contains all sub-views"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Etheria Simulation Suite")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        
        # Sub-views
        self.character_view = None
        self.module_editor_view = None
        
    def create_widgets(self):
        """Create main window widgets"""
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
        char_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(char_frame, text="Character Pokedex")
        self.character_view = CharacterListView(char_frame)
        self.character_view.create_widgets()
        
        # Create Mathic System tab  
        mathic_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(mathic_frame, text="Mathic System")
        self._create_mathic_tabs(mathic_frame)
        
        # Action buttons for character tab
        self._create_character_action_buttons(char_frame)
        
        # Status bar
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        return main_frame
    
    def _create_mathic_tabs(self, parent):
        """Create mathic system tabs"""
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Create notebook for mathic subsystems
        mathic_notebook = ttk.Notebook(parent)
        mathic_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Module Editor tab
        module_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(module_frame, text="Module Editor")
        self.module_editor_view = ModuleEditorView(module_frame)
        self.module_editor_view.create_widgets()
        
        # Placeholder for other tabs
        enhance_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(enhance_frame, text="Enhance Simulator")
        ttk.Label(enhance_frame, text="Enhance Simulator - Coming Soon").pack(pady=20)
        
        loadout_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(loadout_frame, text="Loadout Manager")
        ttk.Label(loadout_frame, text="Loadout Manager - Coming Soon").pack(pady=20)
        
        overview_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(overview_frame, text="System Overview")
        ttk.Label(overview_frame, text="System Overview - Coming Soon").pack(pady=20)
    
    def _create_character_action_buttons(self, parent):
        """Create action buttons for character tab"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        self.import_html_btn = ttk.Button(button_frame, text="Import HTML")
        self.import_html_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.import_json_btn = ttk.Button(button_frame, text="Import JSON")
        self.import_json_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_json_btn = ttk.Button(button_frame, text="Export JSON")
        self.export_json_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_character_btn = ttk.Button(button_frame, text="Delete Character")
        self.delete_character_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_list_btn = ttk.Button(button_frame, text="Refresh List")
        self.refresh_list_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def set_status(self, message):
        """Set status message"""
        self.status_var.set(message)
    
    def get_character_view(self):
        """Get character view"""
        return self.character_view
    
    def get_module_editor_view(self):
        """Get module editor view"""
        return self.module_editor_view
