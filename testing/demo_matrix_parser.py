"""
Matrix Effects Parser Demo
示範如何使用Matrix Effects解析程式
"""

from html_parser.parse_matrix import MatrixEffectsParser
import json

def demo_parse_matrix_effects():
    """Demo function showing how to use the MatrixEffectsParser"""
    print("Matrix Effects Parser Demo")
    print("=" * 50)
    
    # Initialize parser
    html_file = './var/MatrixEffects.html'
    parser = MatrixEffectsParser(html_file)
    
    # Parse the HTML file
    if parser.parse():
        print(f"Successfully parsed {len(parser.matrix_effects)} matrix effects\n")
        
        # Example 1: Show specific matrix by name
        print("Example 1: Find specific matrix (Battlewill)")
        battlewill = next((m for m in parser.matrix_effects if m['name'] == 'Battlewill'), None)
        if battlewill:
            print(f"Name: {battlewill['name']}")
            print(f"Type: {battlewill['type']}")
            print(f"Source: {battlewill['source']}")
            for effect in battlewill['effects']:
                print(f"{effect['required']}/{effect['total']}: {effect['effect']}")
        print()
        
        # Example 2: Filter by type
        print("Example 2: All ATK type matrices")
        atk_matrices = [m for m in parser.matrix_effects if 'ATK' in m.get('type', '')]
        for matrix in atk_matrices:
            print(f"- {matrix['name']} (Source: {matrix['source']})")
        print()
        
        # Example 3: Filter by source
        print("Example 3: All matrices from Terrormaton")
        terrormaton_matrices = [m for m in parser.matrix_effects if m.get('source') == 'Terrormaton']
        for matrix in terrormaton_matrices:
            print(f"- {matrix['name']} ({matrix['type']})")
        print()
        
        # Example 4: Show Inferno-only matrices
        print("Example 4: Inferno-only matrices")
        inferno_matrices = [m for m in parser.matrix_effects if m.get('inferno_only', False)]
        for matrix in inferno_matrices:
            print(f"- {matrix['name']} ({matrix['type']}, Source: {matrix['source']})")
        print()
        
        # Example 5: Matrices with multiple effect tiers
        print("Example 5: Matrices with multiple effect tiers")
        multi_tier_matrices = [m for m in parser.matrix_effects if len(m.get('effects', [])) > 2]
        for matrix in multi_tier_matrices:
            print(f"- {matrix['name']}: {len(matrix['effects'])} tiers")
            for effect in matrix['effects']:
                print(f"  {effect['required']}/{effect['total']}: {effect['effect']}")
        print()
        
        # Example 6: Statistics
        print("Example 6: Statistics")
        total_matrices = len(parser.matrix_effects)
        inferno_count = len([m for m in parser.matrix_effects if m.get('inferno_only', False)])
        
        # Count by type
        type_counts = {}
        for matrix in parser.matrix_effects:
            matrix_type = matrix.get('type', 'Unknown')
            type_counts[matrix_type] = type_counts.get(matrix_type, 0) + 1
        
        # Count by source
        source_counts = {}
        for matrix in parser.matrix_effects:
            source = matrix.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"Total matrices: {total_matrices}")
        print(f"Inferno-only matrices: {inferno_count}")
        print("\nBy Type:")
        for matrix_type, count in type_counts.items():
            print(f"  {matrix_type}: {count}")
        
        print("\nBy Source:")
        for source, count in source_counts.items():
            print(f"  {source}: {count}")
        
    else:
        print("Failed to parse HTML file")

if __name__ == "__main__":
    demo_parse_matrix_effects()
