#!/usr/bin/env python3
"""
Views for the Etheria Simulation Suite
Contains UI components separated from business logic
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from abc import ABC, abstractmethod
import os
from PIL import Image, ImageTk


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
        
        # Enhancement configuration variables
        self.max_enhancements_var = tk.StringVar(value="5")
        self.remaining_enhancements_var = tk.StringVar(value="5")
        
        # Matrix variables
        self.matrix_var = tk.StringVar()
        self.matrix_count_var = tk.StringVar(value="3")
        
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
        self.substat1_rolls_var = tk.StringVar(value="1")
        
        self.substat2_type_var = tk.StringVar()
        self.substat2_value_var = tk.StringVar()
        self.substat2_rolls_var = tk.StringVar(value="1")
        
        self.substat3_type_var = tk.StringVar()
        self.substat3_value_var = tk.StringVar()
        self.substat3_rolls_var = tk.StringVar(value="1")
        
        self.substat4_type_var = tk.StringVar()
        self.substat4_value_var = tk.StringVar()
        self.substat4_rolls_var = tk.StringVar(value="1")
    
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
        
        # Module type and main stat row
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
        
        # Matrix row
        ttk.Label(type_frame, text="Matrix:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        self.matrix_combo = ttk.Combobox(type_frame, textvariable=self.matrix_var,
                                       state="readonly", width=20)
        self.matrix_combo.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=(10, 0), sticky=(tk.W,))
        self.matrix_combo.bind('<<ComboboxSelected>>', 
                              lambda e: self.controller.on_matrix_change() if self.controller else None)
        
        ttk.Label(type_frame, text="Count:").grid(row=1, column=3, padx=(0, 5), pady=(10, 0))
        self.matrix_count_spinbox = ttk.Spinbox(type_frame, textvariable=self.matrix_count_var, 
                                              from_=1, to=3, width=5)
        self.matrix_count_spinbox.grid(row=1, column=4, pady=(10, 0))
        self.matrix_count_spinbox.bind('<KeyRelease>', 
                                     lambda e: self.controller.on_matrix_count_change() if self.controller else None)
        self.matrix_count_spinbox.bind('<Button-1>', 
                                     lambda e: self.controller.on_matrix_count_change() if self.controller else None)
        
        # Clear matrix button
        ttk.Button(type_frame, text="Clear", 
                  command=lambda: self.controller.clear_matrix() if self.controller else None).grid(row=1, column=5, padx=(5, 0), pady=(10, 0))
    
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
        
        # Enhancement configuration
        enhancement_frame = ttk.LabelFrame(edit_frame, text="Enhancement Configuration", padding="5")
        enhancement_frame.grid(row=0, column=3, columnspan=3, sticky=(tk.W, tk.E), padx=(20, 0))
        
        # Max enhancements setting with slider
        ttk.Label(enhancement_frame, text="Max Enhancements:").grid(row=0, column=0, padx=(0, 5))
        max_enh_scale = tk.Scale(enhancement_frame, from_=0, to=5, orient=tk.HORIZONTAL,
                               variable=self.max_enhancements_var, 
                               command=lambda v: self._on_max_enhancements_change())
        max_enh_scale.grid(row=0, column=1, padx=(0, 10))
        max_enh_scale.configure(length=100, width=15)
        
        # Remaining enhancements display
        ttk.Label(enhancement_frame, text="Remaining:").grid(row=0, column=2, padx=(10, 5))
        remaining_label = ttk.Label(enhancement_frame, textvariable=self.remaining_enhancements_var,
                                  font=('Arial', 10, 'bold'), foreground="darkgreen")
        remaining_label.grid(row=0, column=3)
        
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
            rolls_spinbox = ttk.Spinbox(substat_frame, textvariable=rolls_var, from_=1, to=6, width=5)
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
            display_text = f"{module.module_type} - {module.main_stat} ({module.level}) - {module.matrix} ({"" if module.matrix == "" else module.matrix_count})"
            self.module_listbox.insert(tk.END, display_text)
    
    def update_module_details(self, module):
        """Update module details display"""
        if not module:
            return
        
        # Update basic info
        self.module_type_var.set(module.module_type)
        self.main_stat_var.set(module.main_stat)
        self.main_stat_value_var.set(str(module.main_stat_value))
        
        # Trigger module type change to update options while preserving current values
        if self.controller:
            self.controller.on_module_type_change(preserve_current_values=True)
        
        # Update matrix info
        self.matrix_var.set(module.matrix if hasattr(module, 'matrix') else "")
        self.matrix_count_var.set(str(module.matrix_count) if hasattr(module, 'matrix_count') else "3")
        
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
                # Only set value if there are rolls, otherwise leave empty
                if substat.rolls_used > 0 and substat.current_value:
                    value_var.set(str(int(substat.current_value)))
                else:
                    value_var.set("")
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
    
    def update_matrix_options(self, options):
        """Update matrix combo options"""
        self.matrix_combo.configure(values=options)
    
    def get_matrix_info(self):
        """Get current matrix info"""
        return {
            'matrix': self.matrix_var.get(),
            'matrix_count': int(self.matrix_count_var.get()) if self.matrix_count_var.get().isdigit() else 3
        }
    
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
    
    def _on_max_enhancements_change(self):
        """Handle max enhancements change"""
        if self.controller:
            self.controller.on_max_enhancements_change()
    
    def update_remaining_enhancements_display(self, remaining):
        """Update remaining enhancements display"""
        self.remaining_enhancements_var.set(str(remaining))
    
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
            'substats_data': substats_data,
            'max_enhancements': int(self.max_enhancements_var.get()) if self.max_enhancements_var.get().isdigit() else 5
        }


class EnhanceSimulatorView(BaseView):
    """View for enhance simulator"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.enhance_module_var = tk.StringVar()
        
        # UI elements
        self.enhance_module_combo = None
        self.current_module_text = None
        self.enhancement_log = None
        self.probability_tree = None
        self.value_analysis_text = None
        
    def create_widgets(self):
        """Create enhance simulator widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(1, weight=1)
        
        # Top frame - Module selection
        top_frame = ttk.Frame(self.parent)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(top_frame, text="Select Module for Enhancement:").grid(row=0, column=0, padx=(0, 10))
        self.enhance_module_combo = ttk.Combobox(top_frame, textvariable=self.enhance_module_var,
                                               state="readonly", width=30)
        self.enhance_module_combo.grid(row=0, column=1, padx=(0, 10))
        self.enhance_module_combo.bind('<<ComboboxSelected>>', 
                                     lambda e: self.controller.on_enhance_module_select() if self.controller else None)
        
        ttk.Button(top_frame, text="Refresh Modules", 
                  command=lambda: self.controller.refresh_enhance_modules() if self.controller else None).grid(row=0, column=2)
        
        # Left panel - Enhancement controls
        self._create_enhancement_controls()
        
        # Right panel - Statistics and analysis
        self._create_statistics_panel()
        
        return self.parent
    
    def _create_enhancement_controls(self):
        """Create enhancement controls panel"""
        left_panel = ttk.LabelFrame(self.parent, text="Enhancement Controls", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Current module info
        current_info_frame = ttk.LabelFrame(left_panel, text="Current Module", padding="10")
        current_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.current_module_text = tk.Text(current_info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.current_module_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Enhancement buttons
        enhance_buttons_frame = ttk.Frame(left_panel)
        enhance_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(enhance_buttons_frame, text="Enhance Once", 
                  command=lambda: self.controller.enhance_once() if self.controller else None).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance 5 Times", 
                  command=lambda: self.controller.enhance_five_times() if self.controller else None).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(enhance_buttons_frame, text="Enhance to Max", 
                  command=lambda: self.controller.enhance_to_max() if self.controller else None).grid(row=0, column=2)
        
        # Enhancement log
        log_frame = ttk.LabelFrame(left_panel, text="Enhancement Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.enhancement_log = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.enhancement_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.enhancement_log.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.enhancement_log.configure(yscrollcommand=log_scroll.set)
        
        # Configure grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        current_info_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _create_statistics_panel(self):
        """Create statistics and analysis panel"""
        right_panel = ttk.LabelFrame(self.parent, text="Statistics & Analysis", padding="10")
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
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        prob_frame.columnconfigure(0, weight=1)
        value_frame.columnconfigure(0, weight=1)
        value_frame.rowconfigure(0, weight=1)
    
    def update_display(self, data):
        """Update module list for enhance simulator"""
        module_options = []
        for module_id, module in data.items():
            display_text = f"{module_id}: {module.module_type} - {module.main_stat}"
            module_options.append(display_text)
        
        self.enhance_module_combo.configure(values=module_options)
        if module_options and not self.enhance_module_var.get():
            self.enhance_module_var.set(module_options[0])
            if self.controller:
                self.controller.on_enhance_module_select()
    
    def update_current_module_display(self, module, config):
        """Update current module information display"""
        self.current_module_text.config(state=tk.NORMAL)
        self.current_module_text.delete(1.0, tk.END)
        
        # Sync enhancement tracking before display to ensure accuracy
        module.sync_enhancement_tracking()
        
        info_text = f"Module: {module.module_type}\n"
        info_text += f"Main Stat: {module.main_stat} ({int(module.main_stat_value)})\n"
        info_text += f"Level: {module.level} (Used: {module.total_enhancement_rolls} / Remaining: {module.remaining_enhancements})\n"
        info_text += f"Substats: {len(module.substats)}/4\n\n"
        
        if module.substats:
            info_text += "Current Substats:\n"
            for i, substat in enumerate(module.substats, 1):
                max_val = config["substats"][substat.stat_name]["max_value"]
                efficiency = substat.get_efficiency_percentage(max_val)
                info_text += f"{i}. {substat.stat_name}: {int(substat.current_value)} "
                info_text += f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}%)\n"
        else:
            info_text += "No substats yet\n"
        
        self.current_module_text.insert(1.0, info_text)
        self.current_module_text.config(state=tk.DISABLED)
    
    def update_probability_display(self, probabilities):
        """Update probability display for next enhancement"""
        # Clear existing items
        for item in self.probability_tree.get_children():
            self.probability_tree.delete(item)
        
        if probabilities:
            for stat_name, prob in probabilities.items():
                self.probability_tree.insert('', tk.END, text=stat_name, 
                                            values=(f"{prob*100:.1f}%",))
        else:
            self.probability_tree.insert('', tk.END, text="No enhancements possible", 
                                        values=("0.0%",))
    
    def update_value_analysis_display(self, value_data):
        """Update module value analysis display with categorized scoring"""
        self.value_analysis_text.config(state=tk.NORMAL)
        self.value_analysis_text.delete(1.0, tk.END)
        
        analysis_text = "MODULE VALUE ANALYSIS\n"
        analysis_text += "="*30 + "\n\n"
        
        # Overall scores
        analysis_text += f"Total Value Score: {value_data['total_value']:.2f}\n"
        analysis_text += f"Overall Efficiency: {value_data['efficiency']:.1f}%\n"
        analysis_text += f"Roll Efficiency: {value_data['roll_efficiency']:.1f}%\n\n"
        
        # Category scores
        analysis_text += "CATEGORY SCORES\n"
        analysis_text += "-" * 20 + "\n"
        analysis_text += f"Defense Score:  {value_data.get('defense_score', 0):.2f}\n"
        analysis_text += f"Support Score:  {value_data.get('support_score', 0):.2f}\n"
        analysis_text += f"Offense Score:  {value_data.get('offense_score', 0):.2f}\n\n"
        
        # Determine primary category
        scores = {
            'Defense': value_data.get('defense_score', 0),
            'Support': value_data.get('support_score', 0),
            'Offense': value_data.get('offense_score', 0)
        }
        primary_category = max(scores, key=scores.get) if max(scores.values()) > 0 else "General"
        analysis_text += f"Primary Focus: {primary_category}\n\n"
        
        if value_data.get('details'):
            analysis_text += "SUBSTAT BREAKDOWN\n"
            analysis_text += "-" * 20 + "\n"
            
            # Group substats by category for better display
            categories = {"defense": [], "support": [], "offense": [], "general": []}
            
            for stat_name, details in value_data['details'].items():
                category = details.get('category_type', 'general')
                categories[category].append((stat_name, details))
            
            # Display each category
            category_names = {"defense": "Defense Stats", "support": "Support Stats", 
                            "offense": "Offense Stats", "general": "Other Stats"}
            
            for category, stats in categories.items():
                if stats:
                    analysis_text += f"\n{category_names[category]}:\n"
                    for stat_name, details in stats:
                        analysis_text += f"  {stat_name}:\n"
                        analysis_text += f"    Value: {int(details['current_value'])}\n"
                        analysis_text += f"    Efficiency: {details['efficiency']:.1f}%\n"
                        analysis_text += f"    Rolls: {details['rolls_used']}/5\n"
                        analysis_text += f"    Score: {details['substat_value']:.2f}\n"
                        analysis_text += f"    Weight: {details['category_weight']:.1f}x\n"
        
        self.value_analysis_text.insert(1.0, analysis_text)
        self.value_analysis_text.config(state=tk.DISABLED)
    
    def log_enhancement(self, message):
        """Add message to enhancement log"""
        self.enhancement_log.config(state=tk.NORMAL)
        self.enhancement_log.insert(tk.END, message + "\n")
        self.enhancement_log.config(state=tk.DISABLED)
        self.enhancement_log.see(tk.END)
    
    def get_selected_module_id(self):
        """Get currently selected module ID"""
        selection = self.enhance_module_var.get()
        if selection:
            return selection.split(":")[0]
        return None


class LoadoutManagerView(BaseView):
    """View for loadout manager"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.loadout_var = tk.StringVar()
        
        # UI elements
        self.loadout_combo = None
        self.slot_frames = {}
        self.slot_combos = {}
        self.slot_vars = {}
        self.slot_substats_labels = {}
        self.stats_summary_text = None
        
    def create_widgets(self):
        """Create loadout manager widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=2)  # Left side for slots
        self.parent.columnconfigure(1, weight=1)  # Right side for stats
        self.parent.rowconfigure(1, weight=1)
        
        # Top frame - Loadout selection
        self._create_loadout_selection()
        
        # Loadout slots frame (left side)
        self._create_equipment_slots()
        
        # Stats summary frame (right side)
        self._create_stats_summary()
        
        return self.parent
    
    def _create_loadout_selection(self):
        """Create loadout selection controls"""
        top_frame = ttk.Frame(self.parent)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
        
        ttk.Label(top_frame, text="Loadout:").grid(row=0, column=0, padx=(0, 5))
        self.loadout_combo = ttk.Combobox(top_frame, textvariable=self.loadout_var,
                                        state="readonly", width=20)
        self.loadout_combo.grid(row=0, column=1, padx=(0, 10))
        self.loadout_combo.bind('<<ComboboxSelected>>', 
                               lambda e: self.controller.on_loadout_select() if self.controller else None)
        
        ttk.Button(top_frame, text="New Loadout", 
                  command=lambda: self.controller.new_loadout() if self.controller else None).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(top_frame, text="Delete Loadout", 
                  command=lambda: self.controller.delete_loadout() if self.controller else None).grid(row=0, column=3)
    
    def _create_equipment_slots(self):
        """Create equipment slots display"""
        slots_frame = ttk.LabelFrame(self.parent, text="Equipment Slots", padding="10")
        slots_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=5)
        
        # Create 6 slots in 2x3 layout
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
                                         lambda e, s=slot_id: self.controller.on_slot_module_change(s) if self.controller else None)
            
            # Substats display area
            substats_frame = ttk.Frame(slot_frame)
            substats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            
            # Create 4 labels for substats in vertical layout
            self.slot_substats_labels[slot_id] = []
            for j in range(4):
                substat_label = ttk.Label(substats_frame, text="", font=("Arial", 10), foreground="darkblue")
                substat_label.grid(row=j, column=0, sticky=tk.W, pady=1)
                self.slot_substats_labels[slot_id].append(substat_label)
        
        # Configure grid weights for 2x3 layout
        slots_frame.columnconfigure(0, weight=1)
        slots_frame.columnconfigure(1, weight=1)
        slots_frame.rowconfigure(0, weight=1)
        slots_frame.rowconfigure(1, weight=1)
        slots_frame.rowconfigure(2, weight=1)
    
    def _create_stats_summary(self):
        """Create stats summary display"""
        stats_frame = ttk.LabelFrame(self.parent, text="Total Stats", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=5)
        
        self.stats_summary_text = tk.Text(stats_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
    
    def update_display(self, data):
        """Update loadout list"""
        loadouts = data if isinstance(data, list) else list(data.keys())
        self.loadout_combo.configure(values=loadouts)
        if loadouts and not self.loadout_var.get():
            self.loadout_var.set(loadouts[0])
            if self.controller:
                self.controller.on_loadout_select()
    
    def update_slot_module_options(self, slot_restrictions, modules):
        """Update module options for all slots with type restrictions"""
        for slot_id in range(1, 7):
            allowed_types = slot_restrictions.get(slot_id, [])
            
            # Filter modules by allowed types for this slot
            slot_module_options = ["None"]
            for mid, mod in modules.items():
                if mod.module_type in allowed_types:
                    slot_module_options.append(f"{mid}: {mod.module_type} - {mod.main_stat}")
            
            self.slot_combos[slot_id].configure(values=slot_module_options)
    
    def update_loadout_display(self, loadout, modules):
        """Update loadout slots display"""
        for slot_id in range(1, 7):
            module_id = loadout.get(slot_id)
            if module_id and module_id in modules:
                module = modules[module_id]
                self.slot_vars[slot_id].set(f"{module_id}: {module.module_type} - {module.main_stat}")
                
                # Update substats display
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
                for substat_label in self.slot_substats_labels[slot_id]:
                    substat_label.config(text="")
    
    def update_stats_summary(self, total_stats):
        """Update total stats display"""
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
    
    def get_selected_loadout(self):
        """Get currently selected loadout name"""
        return self.loadout_var.get()
    
    def get_slot_selection(self, slot_id):
        """Get module selection for specific slot"""
        return self.slot_vars[slot_id].get()


class ShellListView(BaseView):
    """View for shell list and details with matrix filtering"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.search_var = tk.StringVar()
        self.class_var = tk.StringVar(value="All")
        self.rarity_var = tk.StringVar(value="All")
        self.filter_mode_var = tk.StringVar(value="all")
        
        # Matrix selection variables
        self.matrix_vars = {}
        self.selected_matrices = []
        
        # Matrix images cache
        self.matrix_images = {}
        self.matrix_image_path = "./img/matrices/"
        
        # Shell images cache
        self.shell_images = {}
        self.shell_image_path = "./img/shells/"
        
        # Shell details widgets
        self.shell_name_label = None
        self.shell_rarity_label = None
        self.shell_class_label = None
        self.shell_cooldown_label = None
        self.stats_text = None
        self.skills_text = None
        self.matrices_text = None
        
        # Shell list widget
        self.shell_listbox = None
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Main container with horizontal split
        main_paned = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel for list and filters
        left_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(left_frame, weight=1)
        
        # Right panel for details
        right_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(right_frame, weight=2)
        
        self._create_filter_section(left_frame)
        self._create_shell_list(left_frame)
        self._create_shell_details(right_frame)
    
    def _create_filter_section(self, parent):
        """Create filter controls section"""
        filter_frame = ttk.LabelFrame(parent, text="Filters", padding="5")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        parent.columnconfigure(0, weight=1)
        
        # Search
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # Class filter
        ttk.Label(filter_frame, text="Class:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.class_combo = ttk.Combobox(filter_frame, textvariable=self.class_var, width=17)
        self.class_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.class_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Rarity filter
        ttk.Label(filter_frame, text="Rarity:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.rarity_combo = ttk.Combobox(filter_frame, textvariable=self.rarity_var, width=17)
        self.rarity_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.rarity_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Matrix filter mode
        ttk.Label(filter_frame, text="Matrix Filter:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        mode_frame = ttk.Frame(filter_frame)
        mode_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Radiobutton(mode_frame, text="All", variable=self.filter_mode_var, 
                       value="all", command=self._on_filter_change).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Any", variable=self.filter_mode_var, 
                       value="any", command=self._on_filter_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # Matrix selection area
        matrix_frame = ttk.LabelFrame(filter_frame, text="Matrix Effects", padding="5")
        matrix_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Scrollable matrix checkboxes
        matrix_canvas = tk.Canvas(matrix_frame, height=150)
        matrix_scrollbar = ttk.Scrollbar(matrix_frame, orient="vertical", command=matrix_canvas.yview)
        self.matrix_scroll_frame = ttk.Frame(matrix_canvas)
        
        self.matrix_scroll_frame.bind(
            "<Configure>",
            lambda e: matrix_canvas.configure(scrollregion=matrix_canvas.bbox("all"))
        )
        
        matrix_canvas.create_window((0, 0), window=self.matrix_scroll_frame, anchor="nw")
        matrix_canvas.configure(yscrollcommand=matrix_scrollbar.set)
        
        matrix_canvas.pack(side="left", fill="both", expand=True)
        matrix_scrollbar.pack(side="right", fill="y")
        
        # Clear and Apply buttons
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(button_frame, text="Clear All", command=self._clear_matrix_selection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Apply Filter", command=self._apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        
        filter_frame.columnconfigure(1, weight=1)
    
    def _create_shell_list(self, parent):
        """Create shell list display"""
        list_frame = ttk.LabelFrame(parent, text="Shells", padding="5")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        parent.rowconfigure(1, weight=1)
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.shell_listbox = tk.Listbox(listbox_frame, height=15)
        shell_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.shell_listbox.yview)
        self.shell_listbox.configure(yscrollcommand=shell_scrollbar.set)
        
        self.shell_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        shell_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.shell_listbox.bind('<<ListboxSelect>>', self._on_shell_select)
    
    def _create_shell_details(self, parent):
        """Create shell details display"""
        details_frame = ttk.LabelFrame(parent, text="Shell Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main container with shell image and info
        main_info_frame = ttk.Frame(details_frame)
        main_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Shell image
        image_frame = ttk.Frame(main_info_frame)
        image_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Shell image display (64x64 pixels)
        self.shell_image_label = ttk.Label(image_frame, text="No Image", relief=tk.SUNKEN, width=10)
        self.shell_image_label.pack()
        
        # Right side - Basic info section
        info_frame = ttk.Frame(main_info_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Name
        ttk.Label(info_frame, text="Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.shell_name_label = ttk.Label(info_frame, text="-", font=("Arial", 10))
        self.shell_name_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Rarity
        ttk.Label(info_frame, text="Rarity:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W)
        self.shell_rarity_label = ttk.Label(info_frame, text="-")
        self.shell_rarity_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Class
        ttk.Label(info_frame, text="Class:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W)
        self.shell_class_label = ttk.Label(info_frame, text="-")
        self.shell_class_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Cooldown
        ttk.Label(info_frame, text="Cooldown:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W)
        self.shell_cooldown_label = ttk.Label(info_frame, text="-")
        self.shell_cooldown_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Create notebook for detailed information
        details_notebook = ttk.Notebook(details_frame)
        details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Stats tab
        stats_frame = ttk.Frame(details_notebook, padding="5")
        details_notebook.add(stats_frame, text="Stats")
        
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Skills tab
        skills_frame = ttk.Frame(details_notebook, padding="5")
        details_notebook.add(skills_frame, text="Skills")
        
        self.skills_text = tk.Text(skills_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        skills_scrollbar = ttk.Scrollbar(skills_frame, orient=tk.VERTICAL, command=self.skills_text.yview)
        self.skills_text.configure(yscrollcommand=skills_scrollbar.set)
        
        self.skills_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        skills_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Matrix Effects tab
        matrices_frame = ttk.Frame(details_notebook, padding="5")
        details_notebook.add(matrices_frame, text="Matrix Effects")
        
        self.matrices_text = tk.Text(matrices_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        matrices_scrollbar = ttk.Scrollbar(matrices_frame, orient=tk.VERTICAL, command=self.matrices_text.yview)
        self.matrices_text.configure(yscrollcommand=matrices_scrollbar.set)
        
        self.matrices_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        matrices_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _on_search_change(self, event=None):
        """Handle search text change"""
        if self.controller:
            self.controller.search_shells()
    
    def _on_filter_change(self, event=None):
        """Handle filter change"""
        if self.controller:
            self.controller.apply_filters()
    
    def _clear_matrix_selection(self):
        """Clear all matrix selections"""
        for var in self.matrix_vars.values():
            var.set(False)
        self.selected_matrices = []
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters"""
        # Update selected matrices list
        self.selected_matrices = [
            matrix for matrix, var in self.matrix_vars.items() 
            if var.get()
        ]
        
        if self.controller:
            self.controller.apply_filters()
    
    def _on_shell_select(self, event=None):
        """Handle shell selection"""
        selection = self.shell_listbox.curselection()
        if selection and self.controller:
            shell_name = self.shell_listbox.get(selection[0])
            self.controller.select_shell(shell_name)
    
    def update_display(self, shells):
        """Update shell list display"""
        self.shell_listbox.delete(0, tk.END)
        for shell in shells:
            display_name = f"{shell['name']} ({shell['rarity']} {shell['class']})"
            self.shell_listbox.insert(tk.END, display_name)
    
    def update_filter_options(self, classes, rarities, matrices):
        """Update filter dropdown options"""
        # Update class filter
        self.class_combo['values'] = ["All"] + classes
        
        # Update rarity filter
        self.rarity_combo['values'] = ["All"] + rarities
        
        # Update matrix checkboxes
        self._create_matrix_checkboxes(matrices)
    
    def _create_matrix_checkboxes(self, matrices):
        """Create matrix effect checkboxes with images"""
        # Clear existing checkboxes
        for widget in self.matrix_scroll_frame.winfo_children():
            widget.destroy()
        
        self.matrix_vars = {}
        
        # Create checkboxes in a grid layout
        col_count = 2
        for i, matrix in enumerate(matrices):
            row = i // col_count
            col = i % col_count
            
            var = tk.BooleanVar()
            self.matrix_vars[matrix] = var
            
            # Load matrix image
            matrix_image = self._load_matrix_image(matrix)
            
            # Create frame for checkbox with image
            checkbox_frame = ttk.Frame(self.matrix_scroll_frame)
            checkbox_frame.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
            # Create checkbox with image
            if matrix_image:
                checkbox = ttk.Checkbutton(
                    checkbox_frame, 
                    text=f"  {matrix}",  # Add space for image
                    variable=var,
                    command=self._apply_filters,
                    image=matrix_image,
                    compound=tk.LEFT
                )
            else:
                checkbox = ttk.Checkbutton(
                    checkbox_frame, 
                    text=matrix, 
                    variable=var,
                    command=self._apply_filters
                )
            
            checkbox.pack(side=tk.LEFT, anchor=tk.W)
    
    def _load_matrix_image(self, matrix_name):
        """Load and cache matrix image"""
        if matrix_name in self.matrix_images:
            return self.matrix_images[matrix_name]
        
        try:
            # Convert matrix name to file name format
            file_name = f"set_{matrix_name.lower()}.webp"
            image_path = os.path.join(self.matrix_image_path, file_name)
            
            if os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path)
                # Resize to a small size for checkbox (24x24 pixels)
                pil_image = pil_image.resize((24, 24), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(pil_image)
                
                # Cache the image
                self.matrix_images[matrix_name] = tk_image
                return tk_image
            else:
                print(f"Warning: Image not found for matrix '{matrix_name}' at {image_path}")
                return None
                
        except Exception as e:
            print(f"Error loading image for matrix '{matrix_name}': {e}")
            return None
    
    def _load_shell_image(self, shell_name):
        """Load and cache shell image"""
        if shell_name in self.shell_images:
            return self.shell_images[shell_name]
        
        try:
            # Convert shell name to file name format
            # Replace spaces with underscores and convert to lowercase
            file_name = f"shell_{shell_name.lower().replace(' ', '_').replace('-', '_')}.webp"
            image_path = os.path.join(self.shell_image_path, file_name)
            
            if os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path)
                # Resize to 64x64 pixels for shell details display
                pil_image = pil_image.resize((64, 64), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(pil_image)
                
                # Cache the image
                self.shell_images[shell_name] = tk_image
                return tk_image
            else:
                print(f"Warning: Image not found for shell '{shell_name}' at {image_path}")
                return None
                
        except Exception as e:
            print(f"Error loading image for shell '{shell_name}': {e}")
            return None
    
    def update_shell_details(self, shell_data):
        """Update shell details display"""
        if not shell_data:
            self._clear_shell_details()
            return
        
        shell_name = shell_data.get('name', '')
        
        # Update shell image
        shell_image = self._load_shell_image(shell_name)
        if shell_image:
            self.shell_image_label.config(image=shell_image, text="")
        else:
            self.shell_image_label.config(image="", text="No Image")
        
        # Update basic info
        self.shell_name_label.config(text=shell_name or '-')
        self.shell_rarity_label.config(text=shell_data.get('rarity', '-'))
        self.shell_class_label.config(text=shell_data.get('class', '-'))
        self.shell_cooldown_label.config(text=f"{shell_data.get('cooldown', '-')}s")
        
        # Update stats
        self._update_text_widget(self.stats_text, self._format_stats(shell_data.get('stats', {})))
        
        # Update skills
        self._update_text_widget(self.skills_text, self._format_skills(shell_data.get('skills', {})))
        
        # Update matrix effects
        self._update_text_widget(self.matrices_text, self._format_matrices(shell_data.get('sets', [])))
    
    def _clear_shell_details(self):
        """Clear shell details display"""
        # Clear shell image
        self.shell_image_label.config(image="", text="No Image")
        
        self.shell_name_label.config(text="-")
        self.shell_rarity_label.config(text="-")
        self.shell_class_label.config(text="-")
        self.shell_cooldown_label.config(text="-")
        
        self._update_text_widget(self.stats_text, "No shell selected")
        self._update_text_widget(self.skills_text, "No shell selected")
        self._update_text_widget(self.matrices_text, "No shell selected")
    
    def _update_text_widget(self, widget, content):
        """Update text widget content"""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, content)
        widget.config(state=tk.DISABLED)
    
    def _format_stats(self, stats):
        """Format stats for display"""
        if not stats:
            return "No stats available"
        
        formatted = []
        for stat_name, value in stats.items():
            formatted.append(f"{stat_name}: {value}")
        
        return "\n".join(formatted)
    
    def _format_skills(self, skills):
        """Format skills for display"""
        if not skills:
            return "No skills available"
        
        formatted = []
        for skill_type, skill_content in skills.items():
            formatted.append(f"{skill_type.upper()}:")
            if isinstance(skill_content, str):
                formatted.append(f"  {skill_content}")
            else:
                formatted.append(f"  {skill_content}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_matrices(self, matrices):
        """Format matrix effects for display"""
        if not matrices:
            return "No matrix effects available"
        
        formatted = []
        formatted.append("Compatible Matrix Effects:")
        formatted.append("")
        
        for matrix in matrices:
            formatted.append(f"• {matrix}")
        
        return "\n".join(formatted)
    
    def get_search_text(self):
        """Get current search text"""
        return self.search_var.get().strip()
    
    def get_selected_class(self):
        """Get selected class filter"""
        return self.class_var.get()
    
    def get_selected_rarity(self):
        """Get selected rarity filter"""
        return self.rarity_var.get()
    
    def get_selected_matrices(self):
        """Get selected matrix effects"""
        return self.selected_matrices
    
    def get_filter_mode(self):
        """Get matrix filter mode (all/any)"""
        return self.filter_mode_var.get()


class SystemOverviewView(BaseView):
    """View for system overview"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.overview_text = None
        
    def create_widgets(self):
        """Create system overview widgets"""
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.overview_text = tk.Text(self.parent, wrap=tk.WORD, state=tk.DISABLED)
        self.overview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                               padx=(10, 0), pady=10)
        
        overview_scroll = ttk.Scrollbar(self.parent, orient=tk.VERTICAL,
                                      command=self.overview_text.yview)
        overview_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S), 
                           padx=(0, 10), pady=10)
        self.overview_text.configure(yscrollcommand=overview_scroll.set)
        
        # Scrollbar column should not expand
        self.parent.columnconfigure(1, weight=0)
        
        return self.parent
    
    def update_display(self, overview_data):
        """Update system overview display"""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete(1.0, tk.END)
        
        overview = "Mathic System Overview\n" + "="*50 + "\n\n"
        
        # Module and loadout counts
        module_count = overview_data.get('module_count', 0)
        loadout_count = overview_data.get('loadout_count', 0)
        
        overview += f"Total Modules: {module_count}\n"
        overview += f"Total Loadouts: {loadout_count}\n\n"
        
        if module_count > 0:
            # Module type distribution
            type_counts = overview_data.get('type_counts', {})
            overview += "Module Distribution:\n"
            for module_type, count in sorted(type_counts.items()):
                overview += f"  {module_type}: {count}\n"
            
            # Enhancement statistics
            avg_level = overview_data.get('avg_level', 0)
            max_level = overview_data.get('max_level', 0)
            overview += f"\nEnhancement Stats:\n"
            overview += f"  Average Level: {avg_level:.1f}\n"
            overview += f"  Highest Level: {max_level}\n\n"
            
            # Loadout information
            loadout_info = overview_data.get('loadout_info', {})
            overview += "Loadouts:\n"
            for loadout_name, equipped_count in loadout_info.items():
                overview += f"  {loadout_name}: {equipped_count}/6 slots\n"
        else:
            overview += "No modules created yet.\n"
            overview += "Use the Module Editor to create your first module!\n"
        
        self.overview_text.insert(1.0, overview)
        self.overview_text.config(state=tk.DISABLED)


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
        self.shell_view = None
        self.module_editor_view = None
        self.enhance_simulator_view = None
        self.loadout_manager_view = None
        self.system_overview_view = None
        
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
        
        # Create Shell Pokedex tab
        shell_frame = ttk.Frame(self.main_notebook, padding="10")
        self.main_notebook.add(shell_frame, text="Shell Pokedex")
        self.shell_view = ShellListView(shell_frame)
        self.shell_view.create_widgets()
        
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
        
        # Enhance Simulator tab
        enhance_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(enhance_frame, text="Enhance Simulator")
        self.enhance_simulator_view = EnhanceSimulatorView(enhance_frame)
        self.enhance_simulator_view.create_widgets()
        
        # Loadout Manager tab
        loadout_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(loadout_frame, text="Loadout Manager")
        self.loadout_manager_view = LoadoutManagerView(loadout_frame)
        self.loadout_manager_view.create_widgets()
        
        # System Overview tab
        overview_frame = ttk.Frame(mathic_notebook, padding="10")
        mathic_notebook.add(overview_frame, text="System Overview")
        self.system_overview_view = SystemOverviewView(overview_frame)
        self.system_overview_view.create_widgets()
    
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
    
    def get_shell_view(self):
        """Get shell view"""
        return self.shell_view
    
    def get_module_editor_view(self):
        """Get module editor view"""
        return self.module_editor_view
    
    def get_enhance_simulator_view(self):
        """Get enhance simulator view"""
        return self.enhance_simulator_view
    
    def get_loadout_manager_view(self):
        """Get loadout manager view"""
        return self.loadout_manager_view
    
    def get_system_overview_view(self):
        """Get system overview view"""
        return self.system_overview_view
