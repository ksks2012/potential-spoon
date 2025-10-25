#!/usr/bin/env python3
"""
Shell View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from .base_view import BaseView


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


