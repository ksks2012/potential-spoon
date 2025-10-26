#!/usr/bin/env python3
"""
Module Editor View for the Etheria Simulation Suite
"""

import tkinter as tk
from tkinter import ttk
from .base_view import BaseView


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
        
        # Create substat header labels
        self._create_substat_headers(edit_frame)
        
        # Create substat control frames
        self._create_substat_controls(edit_frame)
        
        # Apply changes button
        ttk.Button(edit_frame, text="Apply Changes", 
                  command=lambda: self.controller.apply_module_changes() if self.controller else None).grid(row=7, column=0, pady=(10, 0))
    
    def _create_substat_headers(self, parent):
        """Create header labels for substat controls"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Headers aligned with substat controls
        ttk.Label(header_frame, text="", width=3).grid(row=0, column=0, padx=(0, 5))  # Number column
        ttk.Label(header_frame, text="Type", font=('Arial', 9, 'bold')).grid(row=0, column=1, padx=(0, 5))
        ttk.Label(header_frame, text="Value", font=('Arial', 9, 'bold')).grid(row=0, column=2, padx=(0, 5))
        ttk.Label(header_frame, text="Rolls", font=('Arial', 9, 'bold')).grid(row=0, column=3)
    
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
            row = 3 + i  # Start from row 3 because header is at row 2
            
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
        # Preserve selection by module id
        try:
            current_selection = self.get_selected_module_index()
            selected_id = None
            if current_selection is not None and hasattr(self, 'module_ids'):
                if 0 <= current_selection < len(self.module_ids):
                    selected_id = self.module_ids[current_selection]
        except Exception:
            selected_id = None

        # Rebuild module id list and listbox entries
        self.module_listbox.delete(0, tk.END)
        self.module_ids = list(modules.keys())
        for module_id in self.module_ids:
            module = modules[module_id]
            display_text = f"{module.module_type} - {module.main_stat} ({module.level}) - {module.matrix} ({'' if getattr(module, 'matrix', '') == '' else getattr(module, 'matrix_count', '')})"
            self.module_listbox.insert(tk.END, display_text)

        # Restore previous selection if possible
        if selected_id and selected_id in self.module_ids:
            idx = self.module_ids.index(selected_id)
            self.module_listbox.selection_set(idx)
            self.module_listbox.activate(idx)
    
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
                # Set value if substat exists; show 0 when rolls exist but value is 0
                if substat.stat_name:
                    if substat.current_value is not None and substat.current_value > 0:
                        value_var.set(str(int(substat.current_value)))
                    elif substat.rolls_used and substat.rolls_used > 0:
                        value_var.set(str(int(substat.current_value or 0)))
                    else:
                        value_var.set("")
                # Set rolls, minimum 1 if stat name exists
                if substat.stat_name and substat.rolls_used > 0:
                    rolls_var.set(str(substat.rolls_used))
                elif substat.stat_name:
                    rolls_var.set("1")  # Default to 1 roll if stat exists but no rolls recorded
                else:
                    rolls_var.set("0")
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
        """Update substat combo options (legacy method for compatibility)"""
        for combo, _, _, _, _, _ in self.substat_controls:
            combo.configure(values=options)
    
    def update_substat_options_individually(self, base_options, existing_substats):
        """Update each substat combo with individually filtered options"""
        for i, (combo, _, _, type_var, _, _) in enumerate(self.substat_controls):
            # Get current selection for this substat
            current_selection = type_var.get()
            
            # Create filtered options: exclude other substats but keep current selection
            filtered_options = [""]  # Always include empty option
            for option in base_options:
                if option not in existing_substats or option == current_selection:
                    filtered_options.append(option)
            
            # Update combo values
            combo.configure(values=filtered_options)
            
            # Preserve current selection if it's still valid
            if current_selection and current_selection not in filtered_options:
                type_var.set("")  # Clear invalid selection
    
    def update_substat_value_options(self, substat_index, options):
        """Update value options for specific substat"""
        if 0 <= substat_index - 1 < len(self.substat_controls):
            _, value_combo, _, _, value_var, _ = self.substat_controls[substat_index - 1]
            value_combo.configure(values=options)
            
            # Set default value if options available and current value not in options
            if options:
                current_value = value_var.get()
                if not current_value or current_value not in options:
                    # Set to the first (minimum) available value
                    value_var.set(options[0])
            else:
                # Clear value if no options
                value_var.set("")
    
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
            stat_name = type_var.get().strip()
            value_str = value_var.get().strip()
            rolls_str = rolls_var.get().strip()
            
            # Only process if stat name exists
            current_value = 0
            rolls_used = 0
            
            if stat_name:
                try:
                    current_value = float(value_str) if value_str else 0
                    rolls_used = int(rolls_str) if rolls_str else 1  # Default to 1 roll if stat exists
                except (ValueError, TypeError):
                    current_value = 0
                    rolls_used = 1 if stat_name else 0
            
            substats_data.append({
                'stat_name': stat_name,
                'current_value': current_value,
                'rolls_used': rolls_used,
                'rolls': rolls_used
            })
        
        # Coerce main stat value to number when possible
        main_val_str = self.main_stat_value_var.get().strip()
        try:
            main_stat_value = float(main_val_str) if main_val_str != "" else 0.0
        except (ValueError, TypeError):
            main_stat_value = 0.0

        # Ensure rolls and numeric fields are proper types
        for d in substats_data:
            # normalize keys for model compatibility
            if 'rolls_used' in d and 'rolls' not in d:
                d['rolls'] = int(d.get('rolls_used', 0))
            # ensure numeric types
            try:
                d['current_value'] = float(d.get('current_value', 0))
            except (ValueError, TypeError):
                d['current_value'] = 0.0
            try:
                d['rolls'] = int(d.get('rolls', 0))
            except (ValueError, TypeError):
                d['rolls'] = 0

        return {
            'module_type': self.module_type_var.get(),
            'main_stat': self.main_stat_var.get(),
            'main_stat_value': main_stat_value,
            'substats_data': substats_data,
            'max_enhancements': int(self.max_enhancements_var.get()) if self.max_enhancements_var.get().isdigit() else 5
        }
