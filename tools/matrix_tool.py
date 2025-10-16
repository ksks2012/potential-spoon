#!/usr/bin/env python3
"""
Matrix Effects Database Management Tool
Command line tool for managing matrix effects database
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.matrix_db import MatrixDatabase


def print_help():
    """Print help information"""
    print("""
Matrix Effects Database Management Tool

Usage:
  python matrix_tool.py <command> [arguments]

Commands:
  list                              - List all matrix effects
  get <name>                        - Get specific matrix details
  source <source_name>              - List matrices by source
  type <type_name>                  - List matrices by type
  stats                            - Show database statistics
  modify <name> <req> <total> <stat> <value> - Modify a stat value
  backup <filename>                - Export database to JSON
  help                             - Show this help

Examples:
  python matrix_tool.py list
  python matrix_tool.py get Battlewill
  python matrix_tool.py source Terrormaton
  python matrix_tool.py type ATK
  python matrix_tool.py modify Fury 4 8 ATK 12%
  python matrix_tool.py stats
""")


def cmd_list(db):
    """List all matrix effects"""
    matrices = db.get_all_matrix_effects()
    print(f"Total: {len(matrices)} matrix effects\n")
    
    for i, matrix in enumerate(matrices, 1):
        types_str = ' / '.join(matrix['type'])
        print(f"{i:2d}. {matrix['name']} ({types_str}) - Source: {matrix['source']}")


def cmd_get(db, name):
    """Get specific matrix details"""
    matrix = db.get_matrix_effect_by_name(name)
    if not matrix:
        print(f"Matrix not found: {name}")
        return
    
    print(f"Name: {matrix['name']}")
    print(f"Type: {' / '.join(matrix['type'])}")
    print(f"Source: {matrix['source']}")
    print(f"Created: {matrix.get('created_at', 'Unknown')}")
    print(f"Updated: {matrix.get('updated_at', 'Unknown')}")
    print("\nEffects:")
    
    for effect in matrix['effects']:
        # Display stats
        if effect['effect']:
            stats_str = ', '.join([f"{k}: {v}" for k, v in effect['effect'].items()])
            print(f"  {effect['required']}/{effect['total']}: {stats_str}")
        else:
            print(f"  {effect['required']}/{effect['total']}: No stat bonuses")
        
        # Display extra effect
        if 'extra_effect' in effect:
            # Wrap long text
            extra_text = effect['extra_effect']
            if len(extra_text) > 80:
                words = extra_text.split()
                lines = []
                current_line = "    Extra: "
                for word in words:
                    if len(current_line) + len(word) + 1 > 80:
                        lines.append(current_line)
                        current_line = "           " + word
                    else:
                        current_line += " " + word if current_line.endswith(": ") else " " + word
                lines.append(current_line)
                for line in lines:
                    print(line)
            else:
                print(f"    Extra: {extra_text}")


def cmd_source(db, source_name):
    """List matrices by source"""
    matrices = db.get_matrix_effects_by_source(source_name)
    if not matrices:
        print(f"No matrices found for source: {source_name}")
        return
    
    print(f"Matrix effects from {source_name}: ({len(matrices)} found)\n")
    for matrix in matrices:
        types_str = ' / '.join(matrix['type'])
        print(f"- {matrix['name']} ({types_str})")


def cmd_type(db, type_name):
    """List matrices by type"""
    matrices = db.get_matrix_effects_by_type(type_name)
    if not matrices:
        print(f"No matrices found for type: {type_name}")
        return
    
    print(f"Matrix effects with type '{type_name}': ({len(matrices)} found)\n")
    for matrix in matrices:
        print(f"- {matrix['name']} (Source: {matrix['source']})")


def cmd_stats(db):
    """Show database statistics"""
    stats = db.get_stats_summary()
    print(f"Database Statistics:")
    print(f"Total matrices: {stats['total_count']}")
    
    print(f"\nBy Source:")
    for source, count in sorted(stats['source_counts'].items()):
        print(f"  {source:12s}: {count}")
    
    print(f"\nBy Type:")
    for type_name, count in sorted(stats['type_counts'].items(), key=lambda x: -x[1]):
        print(f"  {type_name:12s}: {count}")


def cmd_modify(db, matrix_name, req_count, total_count, stat_name, new_value):
    """Modify a matrix stat value"""
    # Show current value first
    matrix = db.get_matrix_effect_by_name(matrix_name)
    if not matrix:
        print(f"Matrix not found: {matrix_name}")
        return
    
    # Find the specific tier and stat
    current_value = None
    for effect in matrix['effects']:
        if effect['required'] == int(req_count) and effect['total'] == int(total_count):
            current_value = effect['effect'].get(stat_name)
            break
    
    if current_value is None:
        print(f"Stat not found: {matrix_name} {req_count}/{total_count} {stat_name}")
        return
    
    print(f"Current value: {matrix_name} {req_count}/{total_count} {stat_name} = {current_value}")
    print(f"Changing to: {new_value}")
    
    # Perform the update
    success = db.update_matrix_value(matrix_name, int(req_count), int(total_count), stat_name, new_value)
    
    if success:
        print(f"✓ Successfully updated {matrix_name}")
    else:
        print(f"✗ Failed to update {matrix_name}")


def cmd_backup(db, filename):
    """Export database to JSON file"""
    import json
    
    matrices = db.get_all_matrix_effects()
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matrices, f, indent=2, ensure_ascii=False, default=str)
        print(f"Database backed up to: {filename}")
    except Exception as e:
        print(f"Error creating backup: {e}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
        return
    
    # Initialize database
    try:
        db = MatrixDatabase()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Execute commands
    try:
        if command == 'list':
            cmd_list(db)
        
        elif command == 'get' and len(sys.argv) >= 3:
            matrix_name = ' '.join(sys.argv[2:])
            cmd_get(db, matrix_name)
        
        elif command == 'source' and len(sys.argv) >= 3:
            source_name = ' '.join(sys.argv[2:])
            cmd_source(db, source_name)
        
        elif command == 'type' and len(sys.argv) >= 3:
            type_name = ' '.join(sys.argv[2:])
            cmd_type(db, type_name)
        
        elif command == 'stats':
            cmd_stats(db)
        
        elif command == 'modify' and len(sys.argv) >= 7:
            matrix_name = sys.argv[2]
            req_count = sys.argv[3]
            total_count = sys.argv[4]
            stat_name = sys.argv[5]
            new_value = sys.argv[6]
            cmd_modify(db, matrix_name, req_count, total_count, stat_name, new_value)
        
        elif command == 'backup' and len(sys.argv) >= 3:
            filename = sys.argv[2]
            cmd_backup(db, filename)
        
        else:
            print(f"Invalid command or insufficient arguments: {' '.join(sys.argv[1:])}")
            print("Use 'python matrix_tool.py help' for usage information")
    
    except Exception as e:
        print(f"Error executing command: {e}")


if __name__ == "__main__":
    main()
