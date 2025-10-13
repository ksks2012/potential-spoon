#!/usr/bin/env python3
"""
Etheria Simulation Suite - Main Launcher
Provides access to all system components
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def show_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("🌟 ETHERIA SIMULATION SUITE 🌟")
    print("="*60)
    print("1. 🎮 Integrated Suite (Character Pokedex + Mathic System)")
    print("2. 🔧 Standalone Mathic System")
    print("3. 🧪 Parse HTML Character Data")
    print("4. 📊 Run Mathic System Demo")
    print("5. 🧾 Run System Tests")
    print("6. ❌ Exit")
    print("="*60)
    
def launch_character_pokedex():
    """Launch the integrated Character Pokedex and Mathic System GUI"""
    try:
        from windowing.ui import CharacterPokedexUI
        import tkinter as tk
        
        print("🚀 Launching Etheria Simulation Suite (Character Pokedex + Mathic System)...")
        root = tk.Tk()
        app = CharacterPokedexUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

def launch_mathic_system():
    """Launch the mathic system GUI"""
    try:
        print("🚀 Launching Mathic System...")
        # Import and run the mathic main
        import subprocess
        result = subprocess.run([sys.executable, "mathic/mathic_main.py"], 
                              cwd=project_root, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
    except Exception as e:
        print(f"❌ Error launching mathic system: {e}")

def parse_character_data():
    """Parse character data from HTML"""
    try:
        from html_parser.parse_char import main as parse_main
        print("🔍 Parsing character data...")
        parse_main()
        print("✅ Character parsing completed")
    except Exception as e:
        print(f"❌ Error parsing character data: {e}")

def run_mathic_demo():
    """Run the mathic system demonstration"""
    try:
        print("🎮 Running Mathic System Demo...")
        import subprocess
        result = subprocess.run([sys.executable, "mathic/demo_mathic.py"], 
                              cwd=project_root)
    except Exception as e:
        print(f"❌ Error running mathic demo: {e}")

def run_tests():
    """Run system tests"""
    print("\n🧪 Running System Tests...")
    
    # Test mathic system
    try:
        print("\n--- Testing Mathic System ---")
        import subprocess
        result = subprocess.run([sys.executable, "mathic/test_mathic.py"], 
                              cwd=project_root)
        print("✅ Mathic system test completed")
    except Exception as e:
        print(f"❌ Mathic system test failed: {e}")
    
    # Test database
    try:
        print("\n--- Testing Database System ---")
        from db.db_routing import CharacterDatabase
        
        db = CharacterDatabase()
        # Basic test
        test_data = {
            "name": "Test Character",
            "rarity": "Epic", 
            "element": "Fire",
            "base_stats": {"ATK": 100, "HP": 1000, "DEF": 80},
            "skills": [],
            "dupes": []
        }
        
        # Test insert
        char_id = db.insert_character_data(test_data)
        if char_id:
            print("✅ Database insert test passed")
            
            # Test retrieval
            retrieved = db.get_character_by_name("Test Character")
            if retrieved:
                print("✅ Database retrieval test passed")
            else:
                print("❌ Database retrieval test failed")
        else:
            print("❌ Database insert test failed")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")

def main():
    """Main program loop"""
    print("🌟 Welcome to Etheria Simulation Suite!")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n🎯 Enter your choice (1-6): ").strip()
            
            if choice == '1':
                launch_character_pokedex()
            elif choice == '2':
                launch_mathic_system()
            elif choice == '3':
                parse_character_data()
            elif choice == '4':
                run_mathic_demo()
            elif choice == '5':
                run_tests()
            elif choice == '6':
                print("\n👋 Thanks for using Etheria Simulation Suite!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        # Wait for user input before showing menu again
        if choice != '6':
            input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main()
