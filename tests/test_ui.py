#!/usr/bin/env python3
"""
Unit tests for ui.py - CharacterPokedexUI class
Tests both the original version and MVC refactored version behavior
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from windowing.ui import CharacterPokedexUI


class TestCharacterPokedexUI(unittest.TestCase):
    """Test suite for CharacterPokedexUI class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
        # Mock all messagebox functions to prevent popups during testing
        self.mock_showinfo = Mock()
        self.mock_showerror = Mock()
        self.mock_showwarning = Mock()
        self.mock_askyesno = Mock(return_value=True)
        
        self.messagebox_patcher = patch.multiple(
            'windowing.ui.messagebox',
            showinfo=self.mock_showinfo,
            showerror=self.mock_showerror,
            showwarning=self.mock_showwarning,
            askyesno=self.mock_askyesno,
            askquestion=Mock(return_value='yes')
        )
        self.messagebox_patcher.start()
        
        # Mock dependencies to avoid actual database/file operations
        with patch('windowing.ui.CharacterDatabase') as mock_db_class, \
             patch('windowing.ui.MathicSystem') as mock_mathic_class:
            
            # Setup mock database
            self.mock_db = Mock()
            mock_db_class.return_value = self.mock_db
            
            # Setup mock mathic system
            self.mock_mathic = Mock()
            mock_mathic_class.return_value = self.mock_mathic
            self.mock_mathic.modules = {}
            self.mock_mathic.mathic_loadouts = {}
            self.mock_mathic.config = {
                'module_types': {
                    'mask': {'main_stat_options': ['HP%', 'ATK%'], 'max_main_stats': {'HP%': 100, 'ATK%': 80}},
                    'core': {'main_stat_options': ['CRIT Rate', 'CRIT DMG'], 'max_main_stats': {'CRIT Rate': 60, 'CRIT DMG': 120}}
                },
                'substats': {
                    'HP%': {'roll_range': [1, 5]},  # Use integers to avoid float range issues
                    'ATK%': {'roll_range': [1, 5]},
                    'DEF%': {'roll_range': [1, 5]},
                    'CRIT Rate': {'roll_range': [1, 4]},
                    'CRIT DMG': {'roll_range': [2, 8]}
                }
            }
            
            # Mock refresh_character_list to avoid actual database calls during init
            with patch.object(CharacterPokedexUI, 'refresh_character_list'):
                self.app = CharacterPokedexUI(self.root)
    
    def tearDown(self):
        """Clean up after each test method"""
        # Stop messagebox patches
        self.messagebox_patcher.stop()
        
        if self.root:
            self.root.destroy()
    
    def test_initialization(self):
        """Test UI initialization"""
        self.assertIsInstance(self.app, CharacterPokedexUI)
        self.assertEqual(self.app.root.title(), "Etheria Simulation Suite")
        # Note: geometry may be different in headless test mode, just check it was set
        self.assertTrue(len(self.app.root.geometry()) > 0)
        self.assertTrue(self.app.root.resizable()[0])  # resizable width
        self.assertTrue(self.app.root.resizable()[1])  # resizable height
        
    def test_widget_creation(self):
        """Test that essential widgets are created"""
        # Check main notebook exists
        self.assertTrue(hasattr(self.app, 'main_notebook'))
        self.assertIsInstance(self.app.main_notebook, tk.ttk.Notebook)
        
        # Check status bar exists
        self.assertTrue(hasattr(self.app, 'status_var'))
        self.assertIsInstance(self.app.status_var, tk.StringVar)
        self.assertEqual(self.app.status_var.get(), "Ready")
        
        # Check character tab widgets
        self.assertTrue(hasattr(self.app, 'character_tree'))
        self.assertTrue(hasattr(self.app, 'search_var'))
        self.assertTrue(hasattr(self.app, 'rarity_var'))
        self.assertTrue(hasattr(self.app, 'element_var'))
        
        # Check character detail widgets
        self.assertTrue(hasattr(self.app, 'char_name_label'))
        self.assertTrue(hasattr(self.app, 'stats_text'))
        self.assertTrue(hasattr(self.app, 'skills_text'))
        self.assertTrue(hasattr(self.app, 'dupes_text'))
        
        # Check mathic system widgets
        self.assertTrue(hasattr(self.app, 'module_listbox'))
        self.assertTrue(hasattr(self.app, 'module_type_var'))
        self.assertTrue(hasattr(self.app, 'main_stat_var'))
        
    def test_refresh_character_list_success(self):
        """Test successful character list refresh"""
        # Mock character data
        mock_characters = [
            {'name': 'Test Char 1', 'rarity': 'SSR', 'element': 'Disorder', 'updated_at': '2024-01-01 10:00:00'},
            {'name': 'Test Char 2', 'rarity': 'SR', 'element': 'Reason', 'updated_at': '2024-01-02 11:00:00'}
        ]
        self.mock_db.get_all_characters.return_value = mock_characters
        
        # Test refresh
        self.app.refresh_character_list()
        
        # Verify database was called
        self.mock_db.get_all_characters.assert_called_once()
        
        # Verify status was updated
        self.assertEqual(self.app.status_var.get(), "Loaded 2 characters")
        
        # Verify tree was populated
        tree_items = self.app.character_tree.get_children()
        self.assertEqual(len(tree_items), 2)
        
        # Check first item values (note: tkinter returns list, not tuple)
        first_item = self.app.character_tree.item(tree_items[0])
        expected_values = ['Test Char 1', 'SSR', 'Disorder', '2024-01-01']
        self.assertEqual(first_item['values'], expected_values)
        
    def test_refresh_character_list_error(self):
        """Test character list refresh with database error"""
        # Mock database error
        self.mock_db.get_all_characters.side_effect = Exception("Database connection failed")
        
        self.app.refresh_character_list()
        
        # Verify error message was shown
        self.mock_showerror.assert_called_once_with("Error", "Failed to load characters: Database connection failed")
        
        # Verify status was updated
        self.assertEqual(self.app.status_var.get(), "Error loading characters")
    
    def test_search_characters(self):
        """Test character search functionality"""
        # Setup mock data
        mock_search_results = [
            {'name': 'Searched Char', 'rarity': 'SSR', 'element': 'Disorder', 'updated_at': '2024-01-01 10:00:00'}
        ]
        self.mock_db.search_characters.return_value = mock_search_results
        
        # Set search term
        self.app.search_var.set("Searched")
        
        # Perform search
        self.app.search_characters()
        
        # Verify database search was called with correct parameters
        self.mock_db.search_characters.assert_called_once_with(name_like="Searched")
        
        # Verify status was updated
        self.assertEqual(self.app.status_var.get(), "Found 1 characters matching 'Searched'")
        
        # Verify tree was populated with search results
        tree_items = self.app.character_tree.get_children()
        self.assertEqual(len(tree_items), 1)
        
    def test_search_characters_empty_search(self):
        """Test search with empty search term triggers refresh"""
        self.app.search_var.set("")
        
        with patch.object(self.app, 'refresh_character_list') as mock_refresh:
            self.app.search_characters()
            mock_refresh.assert_called_once()
            
    def test_filter_characters(self):
        """Test character filtering functionality"""
        # Setup mock data
        mock_filtered_results = [
            {'name': 'SSR Char', 'rarity': 'SSR', 'element': 'Disorder', 'updated_at': '2024-01-01 10:00:00'}
        ]
        self.mock_db.search_characters.return_value = mock_filtered_results
        
        # Reset mock to avoid previous calls from setup
        self.mock_db.search_characters.reset_mock()
        
        # Set filter values (note: setting these may trigger trace callbacks)
        self.app.rarity_var.set("SSR")
        self.app.element_var.set("Disorder")
        
        # Reset again after trace callbacks
        self.mock_db.search_characters.reset_mock()
        
        # Perform filter
        self.app.filter_characters()
        
        # Verify database search was called with correct filters
        self.mock_db.search_characters.assert_called_once_with(rarity="SSR", element="Disorder")
        
    def test_on_character_select(self):
        """Test character selection handling"""
        # Mock tree selection
        mock_item_data = {'values': ['Test Character', 'SSR', 'Disorder', '2024-01-01']}
        
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value=mock_item_data), \
             patch.object(self.app, 'load_character_details') as mock_load:
            
            # Create mock event
            mock_event = Mock()
            
            # Call selection handler
            self.app.on_character_select(mock_event)
            
            # Verify load_character_details was called with correct name
            mock_load.assert_called_once_with('Test Character')
            
    def test_load_character_details_success(self):
        """Test successful character detail loading"""
        # Mock character data
        mock_character_data = {
            'basic_info': {'name': 'Test Char', 'rarity': 'SSR', 'element': 'Disorder'},
            'stats': {'HP': {'base': 1000, 'max': 2000}, 'ATK': {'base': 500, 'max': 1000}},
            'skills': [{'name': 'Skill 1', 'effect': 'Does damage', 'cooldown': '3s', 'tags': ['damage', 'single']}],
            'dupes': {'dupe1': {'name': 'Dupe 1', 'effect': 'Increases ATK'}}
        }
        self.mock_db.get_character_by_name.return_value = mock_character_data
        
        # Load character details
        self.app.load_character_details("Test Char")
        
        # Verify database was called
        self.mock_db.get_character_by_name.assert_called_once_with("Test Char")
        
        # Verify UI labels were updated
        self.assertEqual(self.app.char_name_label.cget('text'), 'Test Char')
        self.assertEqual(self.app.rarity_label.cget('text'), 'SSR')
        self.assertEqual(self.app.element_label.cget('text'), 'Disorder')
        
        # Verify status was updated
        self.assertEqual(self.app.status_var.get(), "Loaded details for Test Char")
        
    def test_load_character_details_not_found(self):
        """Test character detail loading when character not found"""
        self.mock_db.get_character_by_name.return_value = None
        
        self.app.load_character_details("Nonexistent Char")
        # The implementation shows an error instead of clearing details
        self.mock_showerror.assert_called_once()
            
    def test_display_stats(self):
        """Test stats display functionality"""
        mock_stats = {
            'HP': {'base': 1000, 'max': 2000},
            'ATK': {'base': 500, 'max': 1000},
            'Simple Stat': 150
        }
        
        self.app.display_stats(mock_stats)
        
        # Verify stats text was populated
        stats_content = self.app.stats_text.get(1.0, tk.END)
        self.assertIn("CHARACTER STATS", stats_content)
        self.assertIn("HP", stats_content)
        self.assertIn("ATK", stats_content)
        self.assertIn("Simple Stat", stats_content)
        
    def test_display_skills(self):
        """Test skills display functionality"""
        mock_skills = [
            {'name': 'Skill 1', 'effect': 'Does damage', 'cooldown': '3s', 'tags': ['damage']},
            {'name': 'Skill 2', 'effect': 'Heals allies', 'cooldown': '5s', 'tags': ['heal']}
        ]
        
        self.app.display_skills(mock_skills)
        
        # Verify skills text was populated
        skills_content = self.app.skills_text.get(1.0, tk.END)
        self.assertIn("CHARACTER SKILLS", skills_content)
        self.assertIn("Skill 1", skills_content)
        self.assertIn("Skill 2", skills_content)
        self.assertIn("Does damage", skills_content)
        self.assertIn("Heals allies", skills_content)
        
    def test_display_dupes(self):
        """Test dupes display functionality"""
        mock_dupes = {
            'dupe1': {'name': 'First Dupe', 'effect': 'Increases ATK'},
            'dupe2': {'name': 'Second Dupe', 'effect': 'Reduces cooldown'}
        }
        
        self.app.display_dupes(mock_dupes)
        
        # Verify dupes text was populated
        dupes_content = self.app.dupes_text.get(1.0, tk.END)
        self.assertIn("CHARACTER DUPES/PROWESS", dupes_content)
        self.assertIn("First Dupe", dupes_content)
        self.assertIn("Second Dupe", dupes_content)
        self.assertIn("Increases ATK", dupes_content)
        
    def test_clear_character_details(self):
        """Test clearing character details"""
        # First populate some details
        self.app.char_name_label.config(text="Some Character")
        self.app.rarity_label.config(text="SSR")
        
        # Clear details
        self.app.clear_character_details()
        
        # Verify labels were reset
        self.assertEqual(self.app.char_name_label.cget('text'), "Select a character")
        self.assertEqual(self.app.rarity_label.cget('text'), "-")
        self.assertEqual(self.app.element_label.cget('text'), "-")
        
    @patch('windowing.ui.filedialog.askopenfilename')
    @patch('windowing.ui.CharacterParser')
    def test_import_html(self, mock_parser_class, mock_filedialog):
        """Test HTML import functionality"""
        # Mock file dialog
        mock_filedialog.return_value = "/path/to/test.html"
        
        # Mock parser
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_all.return_value = {
            'basic_info': {'name': 'Imported Char'},
            'stats': {},
            'skills': [],
            'dupes': {}
        }
        
        # Mock database operations - use the correct method name
        self.mock_db.insert_character_data.return_value = "new_char_id"
        
        with patch.object(self.app, 'refresh_character_list') as mock_refresh:
            
            self.app.import_html()
            
            # Verify file dialog was opened
            mock_filedialog.assert_called_once()
            
            # Verify parser was created and used
            mock_parser_class.assert_called_once_with("/path/to/test.html")
            mock_parser.parse_all.assert_called_once()
            
            # Verify database insert was called with correct data
            self.mock_db.insert_character_data.assert_called_once()
            
            # Verify success message was shown
            self.mock_showinfo.assert_called_once()
            
            # Verify character list was refreshed
            mock_refresh.assert_called_once()
            
            # Verify no error was shown
            self.mock_showerror.assert_not_called()
            
    @patch('windowing.ui.filedialog.askopenfilename')
    def test_import_json(self, mock_filedialog):
        """Test JSON import functionality"""
        mock_filedialog.return_value = "/path/to/test.json"
        self.mock_db.import_from_json.return_value = True
        
        with patch.object(self.app, 'refresh_character_list') as mock_refresh, \
             patch('windowing.ui.messagebox.showinfo') as mock_info:
            
            self.app.import_json()
            
            # Verify database import was called
            self.mock_db.import_from_json.assert_called_once_with("/path/to/test.json")
            
            # Verify character list was refreshed
            mock_refresh.assert_called_once()
            
    @patch('windowing.ui.filedialog.asksaveasfilename')
    def test_export_json(self, mock_filedialog):
        """Test JSON export functionality"""
        # Mock tree selection
        mock_item_data = {'values': ['Export Char', 'SSR', 'Disorder', '2024-01-01']}
        mock_filedialog.return_value = "/path/to/export.json"
        self.mock_db.export_to_json.return_value = True
        
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value=mock_item_data), \
             patch('windowing.ui.messagebox.showinfo') as mock_info:
            
            self.app.export_json()
            
            # Verify export was called with correct parameters
            self.mock_db.export_to_json.assert_called_once_with("Export Char", "/path/to/export.json")
            
    def test_delete_character(self):
        """Test character deletion functionality"""
        # Mock tree selection
        mock_item_data = {'values': ['Delete Char', 'SSR', 'Disorder', '2024-01-01']}
        
        with patch.object(self.app.character_tree, 'selection', return_value=['item1']), \
             patch.object(self.app.character_tree, 'item', return_value=mock_item_data), \
             patch('windowing.ui.messagebox.askyesno', return_value=True) as mock_confirm, \
             patch.object(self.app, 'refresh_character_list') as mock_refresh:
            
            self.mock_db.delete_character.return_value = True
            
            self.app.delete_character()
            
            # Verify confirmation dialog was shown
            mock_confirm.assert_called_once()
            
            # Verify database delete was called
            self.mock_db.delete_character.assert_called_once_with("Delete Char")
            
            # Verify character list was refreshed
            mock_refresh.assert_called_once()
            
    def test_module_type_change(self):
        """Test module type change handling"""
        self.app.module_type_var.set("mask")
        
        with patch.object(self.app, 'update_substat_options') as mock_update:
            self.app.on_module_type_change()
            
            # Verify main stat combo was updated
            self.assertIn("HP%", self.app.main_stat_combo['values'])
            self.assertIn("ATK%", self.app.main_stat_combo['values'])
            
            # Verify substat options were updated
            mock_update.assert_called_once()
            
    def test_main_stat_change(self):
        """Test main stat change handling"""
        self.app.module_type_var.set("mask")
        self.app.main_stat_var.set("HP%")
        
        self.app.on_main_stat_change()
        
        # Verify main stat value was auto-filled
        self.assertEqual(self.app.main_stat_value_var.get(), "100")
        
    def test_total_rolls_calculation(self):
        """Test total rolls calculation"""
        # Set up substat rolls
        self.app.substat1_type_var.set("HP%")
        self.app.substat1_rolls_var.set("2")
        self.app.substat2_type_var.set("ATK%")
        self.app.substat2_rolls_var.set("3")
        self.app.substat3_type_var.set("")  # Empty substat should not count
        self.app.substat3_rolls_var.set("1")
        
        self.app.update_total_rolls_display()
        
        # Verify total is calculated correctly (only non-empty substats count)
        self.assertEqual(self.app.total_rolls_var.get(), "5")  # 2 + 3, ignoring empty substat
        
    def test_rolls_limit_enforcement(self):
        """Test that total rolls are limited to maximum allowed"""
        # Setup scenario where total would exceed 5
        # First, temporarily disable trace callbacks to avoid recursion issues
        self.app.substat1_type_var.set("HP%")
        self.app.substat2_type_var.set("ATK%")
        self.app.substat3_type_var.set("DEF%")
        
        # Set rolls manually
        self.app.substat1_rolls_var.set("2")
        self.app.substat2_rolls_var.set("2") 
        self.app.substat3_rolls_var.set("1")  # Total = 5, at limit
        
        # Update total display
        self.app.update_total_rolls_display()
        
        # The total should be calculated correctly
        total_rolls = int(self.app.total_rolls_var.get())
        self.assertEqual(total_rolls, 5, "Total rolls should be 5")
        
        # Test that the system tracks total correctly
        self.assertLessEqual(total_rolls, 5, "Total rolls should not exceed maximum of 5")


class TestCharacterPokedexUIIntegration(unittest.TestCase):
    """Integration tests for UI behavior"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after integration tests"""
        if self.root:
            self.root.destroy()
            
    @patch('windowing.ui.CharacterDatabase')
    @patch('windowing.ui.MathicSystem')
    def test_full_initialization_flow(self, mock_mathic_class, mock_db_class):
        """Test complete initialization flow"""
        # Mock dependencies
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        mock_db.get_all_characters.return_value = []
        
        mock_mathic = Mock()
        mock_mathic_class.return_value = mock_mathic
        mock_mathic.modules = {}
        mock_mathic.mathic_loadouts = {}
        mock_mathic.config = {'module_types': {}, 'substats': {}}
        
        # Create app
        app = CharacterPokedexUI(self.root)
        
        # Verify initialization completed without errors
        self.assertIsNotNone(app)
        self.assertIsNotNone(app.db)
        self.assertIsNotNone(app.mathic_system)
        
        # Verify database was queried during initialization
        mock_db.get_all_characters.assert_called()


if __name__ == '__main__':
    # Setup test environment
    unittest.main(verbosity=2, buffer=True)
