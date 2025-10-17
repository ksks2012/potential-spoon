"""
Matrix Database Demo
示範如何使用 Matrix Database 進行查詢和修改操作
"""

from db.matrix_db import MatrixDatabase
import sys


def demo_database_operations():
    """Demonstrate various database operations for matrix effects"""
    print("Matrix Database Operations Demo")
    print("=" * 50)
    
    # Initialize database
    db = MatrixDatabase()
    
    # 1. Show all matrix effects
    print("\n1. All Matrix Effects:")
    all_matrices = db.get_all_matrix_effects()
    print(f"Total: {len(all_matrices)} matrices")
    for i, matrix in enumerate(all_matrices[:3], 1):  # Show first 3
        print(f"{i}. {matrix['name']} ({matrix['source']})")
    
    # 2. Filter by source
    print("\n2. Matrix Effects by Source (Terrormaton):")
    terrormaton_matrices = db.get_matrix_effects_by_source("Terrormaton")
    for matrix in terrormaton_matrices:
        print(f"- {matrix['name']} ({' / '.join(matrix['type'])})")
    
    # 3. Filter by type
    print("\n3. Matrix Effects by Type (ATK):")
    atk_matrices = db.get_matrix_effects_by_type("ATK")
    for matrix in atk_matrices:
        print(f"- {matrix['name']} (Source: {matrix['source']})")
    
    # 4. Get specific matrix details
    print("\n4. Specific Matrix Details (Battlewill):")
    battlewill = db.get_matrix_effect_by_name("Battlewill")
    if battlewill:
        print(f"Name: {battlewill['name']}")
        print(f"Type: {' / '.join(battlewill['type'])}")
        print(f"Source: {battlewill['source']}")
        print("Effects:")
        for effect in battlewill['effects']:
            stats = ', '.join([f"{k}: {v}" for k, v in effect['effect'].items()])
            print(f"  {effect['required']}/{effect['total']}: {stats}")
            if 'extra_effect' in effect:
                print(f"    Extra: {effect['extra_effect']}")
    
    # 5. Database statistics
    print("\n5. Database Statistics:")
    stats = db.get_stats_summary()
    print(f"Total matrices: {stats['total_count']}")
    
    print("\nBy Source:")
    for source, count in stats['source_counts'].items():
        print(f"  {source}: {count}")
    
    print("\nBy Type:")
    for type_name, count in stats['type_counts'].items():
        print(f"  {type_name}: {count}")
    
    return db


def demo_value_modification(db):
    """Demonstrate modifying matrix effect values"""
    print("\n" + "=" * 50)
    print("Value Modification Demo")
    print("=" * 50)
    
    # Get original value
    print("\n1. Original Battlewill 4/8 ATK value:")
    battlewill = db.get_matrix_effect_by_name("Battlewill")
    if battlewill:
        for effect in battlewill['effects']:
            if effect['required'] == 4 and effect['total'] == 8:
                original_value = effect['effect'].get('ATK', 'Not found')
                print(f"Original ATK value: {original_value}")
                break
    
    # Modify the value
    print("\n2. Modifying ATK value from 10% to 15%...")
    success = db.update_matrix_value("Battlewill", 4, 8, "ATK", "15%")
    if success:
        print("✓ Successfully updated ATK value")
    else:
        print("✗ Failed to update ATK value")
    
    # Verify the change
    print("\n3. Verifying the change:")
    battlewill_updated = db.get_matrix_effect_by_name("Battlewill")
    if battlewill_updated:
        for effect in battlewill_updated['effects']:
            if effect['required'] == 4 and effect['total'] == 8:
                new_value = effect['effect'].get('ATK', 'Not found')
                print(f"New ATK value: {new_value}")
                break
    
    # Restore original value
    print("\n4. Restoring original value...")
    success = db.update_matrix_value("Battlewill", 4, 8, "ATK", "10%")
    if success:
        print("✓ Successfully restored original ATK value")
    else:
        print("✗ Failed to restore original ATK value")


def interactive_query_mode(db):
    """Interactive mode for querying matrix effects"""
    print("\n" + "=" * 50)
    print("Interactive Query Mode")
    print("Commands:")
    print("  list - Show all matrices")
    print("  source <name> - Show matrices by source")
    print("  type <name> - Show matrices by type")
    print("  get <name> - Show specific matrix details")
    print("  modify <matrix> <req> <total> <stat> <value> - Modify stat value")
    print("  stats - Show database statistics")
    print("  quit - Exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\nEnter command: ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'list':
                matrices = db.get_all_matrix_effects()
                for i, matrix in enumerate(matrices, 1):
                    print(f"{i:2d}. {matrix['name']} ({matrix['source']})")
            
            elif cmd == 'source' and len(command) > 1:
                source_name = ' '.join(command[1:])
                matrices = db.get_matrix_effects_by_source(source_name)
                if matrices:
                    for matrix in matrices:
                        print(f"- {matrix['name']}")
                else:
                    print(f"No matrices found for source: {source_name}")
            
            elif cmd == 'type' and len(command) > 1:
                type_name = ' '.join(command[1:])
                matrices = db.get_matrix_effects_by_type(type_name)
                if matrices:
                    for matrix in matrices:
                        print(f"- {matrix['name']} (Source: {matrix['source']})")
                else:
                    print(f"No matrices found for type: {type_name}")
            
            elif cmd == 'get' and len(command) > 1:
                matrix_name = ' '.join(command[1:])
                matrix = db.get_matrix_effect_by_name(matrix_name)
                if matrix:
                    print(f"Name: {matrix['name']}")
                    print(f"Type: {' / '.join(matrix['type'])}")
                    print(f"Source: {matrix['source']}")
                    print("Effects:")
                    for effect in matrix['effects']:
                        stats = ', '.join([f"{k}: {v}" for k, v in effect['effect'].items()])
                        print(f"  {effect['required']}/{effect['total']}: {stats}")
                        if 'extra_effect' in effect:
                            print(f"    Extra: {effect['extra_effect']}")
                else:
                    print(f"Matrix not found: {matrix_name}")
            
            elif cmd == 'modify' and len(command) >= 6:
                matrix_name = command[1]
                req_count = int(command[2])
                total_count = int(command[3])
                stat_name = command[4]
                new_value = command[5]
                
                success = db.update_matrix_value(matrix_name, req_count, total_count, stat_name, new_value)
                if success:
                    print(f"✓ Updated {matrix_name} {req_count}/{total_count} {stat_name} to {new_value}")
                else:
                    print(f"✗ Failed to update {matrix_name}")
            
            elif cmd == 'stats':
                stats = db.get_stats_summary()
                print(f"Total matrices: {stats['total_count']}")
                print("\nBy Source:")
                for source, count in stats['source_counts'].items():
                    print(f"  {source}: {count}")
                print("\nBy Type:")
                for type_name, count in stats['type_counts'].items():
                    print(f"  {type_name}: {count}")
            
            else:
                print("Invalid command or insufficient parameters")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function"""
    print("Matrix Database Demo Application")
    
    # Run basic demo
    db = demo_database_operations()
    
    # Run value modification demo
    demo_value_modification(db)
    
    # Check if user wants interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_query_mode(db)
    else:
        print(f"\nDemo completed! Run with 'interactive' argument for interactive mode:")
        print(f"python demo_matrix_db.py interactive")


if __name__ == "__main__":
    main()
