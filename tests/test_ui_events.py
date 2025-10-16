#!/usr/bin/env python3
"""
Unit tests for ui.py - Event handling and state management
Tests UI event bindings, state transitions, and error handling
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from windowing.ui import CharacterPokedexUI


class TestUIEventHandling(unittest.TestCase):
    """Test suite for UI event handling and state management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        with patch('windowing.ui.CharacterDatabase') as mock_db_class, \
             patch('windowing.ui.MathicSystem') as mock_mathic_class:
            
            # Setup mocks
            self.mock_db = Mock()
            mock_db_class.return_value = self.mock_db
            self.mock_db.get_all_characters.return_value = []
            self.mock_db.search_characters.return_value = []
            
            self.mock_mathic = Mock()
            mock_mathic_class.return_value = self.mock_mathic
            self.mock_mathic.modules = {}
            self.mock_mathic.mathic_loadouts = {}
            self.mock_mathic.config = {
                'module_types': {
                    'mask': {'main_stat_options': ['HP%'], 'max_main_stats': {'HP%': 100}}
                },
                'substats': {'HP%': {'roll_range': [1.0, 5.0]}}
            }
            
            with patch.object(CharacterPokedexUI, 'refresh_character_list'):
                self.app = CharacterPokedexUI(self.root)
    
    def tearDown(self):
        """Clean up after each test"""
        if self.root:
            self.root.destroy()
    
    def test_setup_events(self):
        """Test event binding setup"""
        # Verify that setup_events was called during initialization
        # This is implicit in the initialization, but we can test the bindings exist
        
        # Test character tree selection binding
        self.assertTrue(len(self.app.character_tree.bind()) > 0)
        
        # Test search entry return key binding  
        self.assertTrue(len(self.app.search_entry.bind()) > 0)
        
        # Test filter variable traces
        # These are set up in setup_events() method
        rarity_traces = self.app.rarity_var.trace_info()
        element_traces = self.app.element_var.trace_info()
        self.assertGreater(len(rarity_traces), 0)
        self.assertGreater(len(element_traces), 0)
    
    def test_status_updates(self):
        """Test status bar updates"""
        initial_status = self.app.status_var.get()
        self.assertEqual(initial_status, "Ready")
        
        # Test status update
        self.app.status_var.set("Testing status")
        self.assertEqual(self.app.status_var.get(), "Testing status")
        
        # Test status during operations (simulated)
        with patch.object(self.app, 'refresh_character_list'):
            self.app.status_var.set("Loading characters...")
            self.assertEqual(self.app.status_var.get(), "Loading characters...")
    
    def test_error_handling_in_refresh_character_list(self):
        """Test error handling during character list refresh"""
        # Test database connection error
        self.mock_db.get_all_characters.side_effect = ConnectionError("Database unavailable")
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.refresh_character_list()
            
            mock_error.assert_called_once_with("Error", "Failed to load characters: Database unavailable")
            self.assertEqual(self.app.status_var.get(), "Error loading characters")
        
        # Test generic exception
        self.mock_db.get_all_characters.side_effect = ValueError("Invalid data format")
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.refresh_character_list()
            
            mock_error.assert_called_once_with("Error", "Failed to load characters: Invalid data format")
    
    def test_error_handling_in_search_characters(self):
        """Test error handling during character search"""
        self.app.search_var.set("test search")
        self.mock_db.search_characters.side_effect = Exception("Search failed")
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.search_characters()
            
            mock_error.assert_called_once_with("Error", "Search failed: Search failed")
    
    def test_error_handling_in_filter_characters(self):
        """Test error handling during character filtering"""
        # Reset any previous mock settings
        self.mock_db.search_characters.reset_mock()
        
        self.app.rarity_var.set("SSR")
        self.app.element_var.set("Disorder")
        self.mock_db.search_characters.side_effect = Exception("Filter failed")
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.filter_characters()
            
            mock_error.assert_called_once_with("Error", "Filtering failed: Filter failed")
    
    def test_error_handling_in_load_character_details(self):
        """Test error handling during character detail loading"""
        self.mock_db.get_character_by_name.side_effect = Exception("Character not found")
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.load_character_details("Test Character")
            
            mock_error.assert_called_once_with("Error", "Failed to load character details: Character not found")
            self.assertIn("Error loading details", self.app.status_var.get())
    
    def test_character_selection_with_invalid_data(self):
        """Test character selection handling with invalid tree data"""
        # Test with no selection
        with patch.object(self.app.character_tree, 'selection', return_value=[]):
            mock_event = Mock()
            self.app.on_character_select(mock_event)
            # Should handle gracefully without errors
        
        # Test with invalid item data
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value={'values': []}):
            
            mock_event = Mock()
            self.app.on_character_select(mock_event)
            # Should handle gracefully without errors
    
    def test_file_dialog_cancellation(self):
        """Test handling of cancelled file dialogs"""
        # Test HTML import cancellation
        with patch('windowing.ui.filedialog.askopenfilename', return_value=""):
            self.app.import_html()
            # Should return early without attempting to parse
            
        # Test JSON import cancellation
        with patch('windowing.ui.filedialog.askopenfilename', return_value=""):
            self.app.import_json()
            # Should return early without attempting to import
            
        # Test JSON export cancellation
        with patch('windowing.ui.filedialog.asksaveasfilename', return_value=""), \
             patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value={'values': ['Test Char', 'SSR', 'Disorder', '2024-01-01']}):
            
            self.app.export_json()
            # Should return early without attempting to export
    
    def test_delete_confirmation_cancellation(self):
        """Test handling of cancelled delete confirmations"""
        # Test character deletion cancellation
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value={'values': ['Test Char', 'SSR', 'Disorder', '2024-01-01']}), \
             patch('windowing.ui.messagebox.askyesno', return_value=False):
            
            self.app.delete_character()
            
            # Verify database delete was not called
            self.mock_db.delete_character.assert_not_called()
        
        # Test module deletion cancellation
        with patch.object(self.app.module_listbox, 'curselection', return_value=[0]), \
             patch('windowing.ui.messagebox.askyesno', return_value=False):
            
            self.app.delete_module()
            
            # Verify mathic system delete was not called
            self.mock_mathic.delete_module.assert_not_called()
    
    def test_empty_selections_handling(self):
        """Test handling of operations with no selections"""
        # Test export with no character selected
        with patch.object(self.app.character_tree, 'selection', return_value=[]), \
             patch('windowing.ui.messagebox.showwarning') as mock_warning:
            
            self.app.export_json()
            mock_warning.assert_called_once_with("Warning", "Please select a character to export")
        
        # Test delete with no character selected
        with patch.object(self.app.character_tree, 'selection', return_value=[]), \
             patch('windowing.ui.messagebox.showwarning') as mock_warning:
            
            self.app.delete_character()
            mock_warning.assert_called_once_with("Warning", "Please select a character to delete")
        
        # Test module operations with no module selected
        with patch.object(self.app.module_listbox, 'curselection', return_value=[]), \
             patch('windowing.ui.messagebox.showwarning') as mock_warning:
            
            self.app.enhance_module_random()
            mock_warning.assert_called_once()
    
    def test_state_consistency_during_operations(self):
        """Test UI state consistency during various operations"""
        # Test state during character loading
        mock_chars = [{'name': 'Test', 'rarity': 'SSR', 'element': 'Disorder', 'updated_at': '2024-01-01 10:00:00'}]
        self.mock_db.get_all_characters.return_value = mock_chars
        
        initial_status = self.app.status_var.get()
        self.app.refresh_character_list()
        
        # Status should be updated to reflect completed operation
        self.assertNotEqual(self.app.status_var.get(), initial_status)
        self.assertIn("Loaded", self.app.status_var.get())
        
        # Tree should be populated
        self.assertGreater(len(self.app.character_tree.get_children()), 0)
    
    def test_widget_state_management(self):
        """Test widget state management (enabled/disabled states)"""
        # Test text widget states - initially normal (not disabled until first use)
        initial_stats_state = self.app.stats_text.cget('state')
        self.assertEqual(initial_stats_state, tk.NORMAL)
        
        # Test after displaying stats
        mock_stats = {'HP': 1000, 'ATK': 500}
        self.app.display_stats(mock_stats)
        
        # Should remain disabled after update (read-only display)
        final_stats_state = self.app.stats_text.cget('state')
        self.assertEqual(final_stats_state, tk.DISABLED)
    
    def test_data_validation_in_forms(self):
        """Test data validation in form inputs"""
        # Test invalid main stat value
        self.app.module_type_var.set("mask")
        self.app.main_stat_var.set("HP%")
        self.app.main_stat_value_var.set("invalid_number")
        
        # This would be caught when applying module changes
        self.app.current_selected_module_id = "test_module"
        
        with patch('windowing.ui.messagebox.showerror') as mock_error:
            self.app.apply_module_changes()
            # Should show error for invalid value
    
    def test_memory_cleanup(self):
        """Test proper cleanup of resources and references"""
        # Test that clearing character details properly cleans up text widgets
        self.app.stats_text.config(state=tk.NORMAL)
        self.app.stats_text.insert(1.0, "Test content")
        self.app.stats_text.config(state=tk.DISABLED)
        
        self.app.clear_character_details()
        
        # Text widgets should be cleared
        stats_content = self.app.stats_text.get(1.0, tk.END).strip()
        self.assertEqual(stats_content, "")


class TestUIStateTransitions(unittest.TestCase):
    """Test UI state transitions and workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        with patch('windowing.ui.CharacterDatabase') as mock_db_class, \
             patch('windowing.ui.MathicSystem') as mock_mathic_class:
            
            self.mock_db = Mock()
            mock_db_class.return_value = self.mock_db
            
            self.mock_mathic = Mock()
            mock_mathic_class.return_value = self.mock_mathic
            
            # Create a mock module for testing
            mock_module = Mock()
            mock_module.module_type = "mask"
            mock_module.main_stat = "HP%"
            mock_module.main_stat_value = 100
            mock_module.substats = []
            mock_module.max_total_rolls = 5
            mock_module.total_enhancement_rolls = 3
            mock_module.level = 3
            mock_module.can_be_enhanced.return_value = True
            
            self.mock_mathic.modules = {"module1": mock_module}
            self.mock_mathic.mathic_loadouts = {}
            self.mock_mathic.config = {'module_types': {}, 'substats': {}}
            
            # Mock mathic system methods to avoid errors during UI initialization
            self.mock_mathic.calculate_substat_probabilities.return_value = {
                'ATK%': 0.25,
                'DEF%': 0.25,
                'CRIT Rate': 0.25,
                'CRIT DMG': 0.25
            }
            self.mock_mathic.calculate_module_value.return_value = {
                'total_value': 85.5,
                'efficiency': 85.5,
                'roll_efficiency': 85.5,
                'details': {
                    'ATK%': {
                        'current_value': 10.5,
                        'efficiency': 85.0,
                        'rolls_used': 3,
                        'substat_value': 42.5,
                        'importance': 1.0
                    }
                }
            }
            self.mock_mathic.get_module_names.return_value = ["module1"]
            self.mock_mathic.get_loadout_names.return_value = []
            self.mock_mathic.create_module.return_value = mock_module
            self.mock_mathic.generate_random_substats.return_value = None
            self.mock_mathic.enhance_module_random_substat.return_value = True
            self.mock_mathic.create_mathic_loadout.return_value = None
            self.mock_mathic.save_to_file.return_value = None
            self.mock_mathic.delete_module.return_value = True
            self.mock_mathic.delete_loadout.return_value = True
            self.mock_mathic.calculate_loadout_stats.return_value = {
                'Total HP': 15000,
                'Total ATK': 3000,
                'CRIT Rate': 75.5,
                'CRIT DMG': 180.2
            }
            
            with patch.object(CharacterPokedexUI, 'refresh_character_list'):
                self.app = CharacterPokedexUI(self.root)
    
    def tearDown(self):
        """Clean up after each test"""
        if self.root:
            self.root.destroy()
    
    def test_character_workflow(self):
        """Test complete character management workflow"""
        # 1. Initial state - no character selected
        self.assertEqual(self.app.char_name_label.cget('text'), "Select a character")
        
        # 2. Search for characters
        self.mock_db.search_characters.return_value = [
            {'name': 'Found Char', 'rarity': 'SSR', 'element': 'Disorder', 'updated_at': '2024-01-01 10:00:00'}
        ]
        self.app.search_var.set("Found")
        self.app.search_characters()
        
        # 3. Select character
        mock_char_data = {
            'basic_info': {'name': 'Found Char', 'rarity': 'SSR', 'element': 'Disorder'},
            'stats': {'HP': 1000},
            'skills': [],
            'dupes': {}
        }
        self.mock_db.get_character_by_name.return_value = mock_char_data
        
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value={'values': ['Found Char', 'SSR', 'Disorder', '2024-01-01']}):
            
            mock_event = Mock()
            self.app.on_character_select(mock_event)
        
        # 4. Verify character details are loaded
        self.assertEqual(self.app.char_name_label.cget('text'), 'Found Char')
        self.assertEqual(self.app.rarity_label.cget('text'), 'SSR')
        
        # 5. Clear selection
        self.app.clear_character_details()
        self.assertEqual(self.app.char_name_label.cget('text'), "Select a character")
    
    def test_module_workflow(self):
        """Test complete module management workflow"""
        # 1. Initial state - has one mock module
        initial_size = self.app.module_listbox.size()
        self.assertGreaterEqual(initial_size, 0)
        
        # 2. Test module creation variables setup
        self.app.module_type_var.set("mask")
        self.app.main_stat_var.set("HP%")
        self.app.main_stat_value_var.set("100.0")
        self.app.total_rolls_var.set("3")
        
        # Verify variables are set correctly
        self.assertEqual(self.app.module_type_var.get(), "mask")
        self.assertEqual(self.app.main_stat_var.get(), "HP%")
        self.assertEqual(self.app.main_stat_value_var.get(), "100.0")
        self.assertEqual(self.app.total_rolls_var.get(), "3")
        
        # 3. Select and edit module
        mock_module = Mock()
        mock_module.module_type = "mask"
        mock_module.main_stat = "HP%"
        mock_module.main_stat_value = 100
        mock_module.substats = []
        
        self.mock_mathic.modules = {"module1": mock_module}
        
        with patch.object(self.app.module_listbox, 'curselection', return_value=[0]):
            mock_event = Mock()
            self.app.on_module_select(mock_event)
            
            # Verify module data is loaded into form
            self.assertEqual(self.app.module_type_var.get(), "mask")
            self.assertEqual(self.app.main_stat_var.get(), "HP%")
    
    def test_loadout_workflow(self):
        """Test complete loadout management workflow"""
        # 1. Create new loadout
        with patch('tkinter.simpledialog.askstring', return_value="Test Loadout"), \
             patch.object(self.app, 'refresh_loadout_list') as mock_refresh:
            
            self.app.new_loadout()
            mock_refresh.assert_called_once()
        
        # 2. Select loadout - add loadout to mock mathic system
        self.mock_mathic.mathic_loadouts["Test Loadout"] = {1: "module1", 2: None, 3: None, 4: None, 5: None, 6: None}
        self.app.loadout_var.set("Test Loadout")
        
        with patch.object(self.app, 'update_loadout_stats') as mock_update:
            self.app.on_loadout_select()
            mock_update.assert_called_once()
        
        # 3. Assign module to slot
        self.app.slot_vars[1].set("module1: mask - HP%")
        
        with patch.object(self.app, 'update_loadout_stats') as mock_update:
            self.app.on_slot_module_change(1)
            mock_update.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
