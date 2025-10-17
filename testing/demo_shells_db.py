#!/usr/bin/env python3
"""
Demo script for shells database functionality
Shows integration between shells and matrix effects
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.shells_db import ShellsDatabase
from db.matrix_db import MatrixDatabase  
from db.integrated_db import IntegratedDatabase
import json


def demo_shells_database():
    """Demonstrate shells database functionality"""
    print("=== Shells Database Demo ===")
    
    shells_db = ShellsDatabase()
    
    # Get basic statistics
    stats = shells_db.get_stats_summary()
    print(f"\nShells Database Statistics:")
    print(f"Total shells: {stats['total_count']}")
    
    if stats['rarity_counts']:
        print("\nBy Rarity:")
        for rarity, count in stats['rarity_counts'].items():
            print(f"  {rarity}: {count}")
    
    if stats['class_counts']:
        print("\nBy Class:")
        for shell_class, count in stats['class_counts'].items():
            print(f"  {shell_class}: {count}")
    
    if stats['matrix_set_counts']:
        print("\nTop Matrix Sets Used:")
        for set_name, count in list(stats['matrix_set_counts'].items())[:5]:
            print(f"  {set_name}: {count} shells")
    
    # Show a few example shells
    all_shells = shells_db.get_all_shells()
    if all_shells:
        print(f"\nExample Shells (first 3):")
        for i, shell in enumerate(all_shells[:3]):
            print(f"\n{i+1}. {shell['name']} ({shell['rarity']}, {shell['class']})")
            if 'stats' in shell:
                print(f"   Stats: {shell['stats']}")
            if 'sets' in shell:
                print(f"   Matrix Sets: {', '.join(shell['sets'])}")


def demo_matrix_integration():
    """Demonstrate matrix integration functionality"""
    print("\n=== Matrix Integration Demo ===")
    
    integrated_db = IntegratedDatabase()
    
    # Analyze matrix usage
    analysis = integrated_db.get_matrix_usage_analysis()
    
    print(f"\nIntegration Analysis:")
    print(f"Total matrix sets referenced by shells: {analysis['total_matrix_sets_used']}")
    print(f"Total matrix effects in database: {analysis['total_matrix_effects_available']}")
    print(f"Coverage percentage: {analysis['coverage_percentage']:.1f}%")
    
    if analysis['missing_matrix_effects']:
        print(f"\nMissing Matrix Effects ({len(analysis['missing_matrix_effects'])}):")
        for missing in analysis['missing_matrix_effects'][:5]:
            print(f"  - {missing}")
        if len(analysis['missing_matrix_effects']) > 5:
            print(f"  ... and {len(analysis['missing_matrix_effects']) - 5} more")
    
    # Validate references
    validation = integrated_db.validate_shell_matrix_references()
    print(f"\nReference Validation:")
    print(f"Valid references: {len(validation['valid_references'])}")
    print(f"Invalid references: {len(validation['invalid_references'])}")
    
    if validation['shells_with_invalid_refs']:
        print(f"\nShells with invalid references:")
        for shell_info in validation['shells_with_invalid_refs'][:3]:
            print(f"  {shell_info['shell']}: {', '.join(shell_info['invalid_sets'])}")


def demo_shell_with_matrix_details():
    """Demonstrate getting shell with detailed matrix information"""
    print("\n=== Shell with Matrix Details Demo ===")
    
    integrated_db = IntegratedDatabase()
    shells_db = ShellsDatabase()
    
    # Get first shell as example
    all_shells = shells_db.get_all_shells()
    if not all_shells:
        print("No shells found in database")
        return
    
    example_shell = all_shells[0]
    shell_name = example_shell['name']
    
    print(f"\nDetailed information for: {shell_name}")
    
    # Get shell with matrix effects details
    detailed_shell = integrated_db.get_shell_with_matrix_effects(shell_name)
    
    if detailed_shell:
        print(f"Basic Info:")
        print(f"  Name: {detailed_shell['name']}")
        print(f"  Rarity: {detailed_shell['rarity']}")
        print(f"  Class: {detailed_shell['class']}")
        print(f"  Cooldown: {detailed_shell['cooldown']}")
        
        if 'skills' in detailed_shell:
            print(f"Skills:")
            for skill_type, content in detailed_shell['skills'].items():
                print(f"  {skill_type}: {content[:80]}...")
        
        if 'stats' in detailed_shell:
            print(f"Stats: {detailed_shell['stats']}")
        
        if 'matrix_effects' in detailed_shell:
            print(f"\nMatrix Effects Details:")
            for matrix_effect in detailed_shell['matrix_effects']:
                if 'status' in matrix_effect and matrix_effect['status'] == 'not_found':
                    print(f"  - {matrix_effect['name']}: [Matrix data not available]")
                else:
                    print(f"  - {matrix_effect['name']}: {len(matrix_effect.get('effects', []))} tiers available")
                    if 'type' in matrix_effect:
                        print(f"    Types: {', '.join(matrix_effect['type'])}")


def demo_matrix_recommendations():
    """Demonstrate matrix recommendations based on available effects"""
    print("\n=== Matrix Recommendations Demo ===")
    
    integrated_db = IntegratedDatabase()
    matrix_db = MatrixDatabase()
    
    # Get available matrix effects
    all_matrix_effects = matrix_db.get_all_matrix_effects()
    available_matrices = [matrix['name'] for matrix in all_matrix_effects[:10]]  # Use first 10
    
    if not available_matrices:
        print("No matrix effects found in database")
        return
    
    print(f"Available matrix effects: {', '.join(available_matrices)}")
    
    # Get recommendations
    recommendations = integrated_db.get_shell_recommendations(available_matrices)
    
    print(f"\nShell Recommendations (top 5):")
    for i, rec in enumerate(recommendations[:5]):
        print(f"\n{i+1}. {rec['shell']} (Compatibility: {rec['compatibility_score']:.1%})")
        print(f"   Compatible sets: {', '.join(rec['compatible_sets'])}")
        if rec['missing_sets']:
            print(f"   Missing sets: {', '.join(rec['missing_sets'])}")


def demo_comprehensive_stats():
    """Show comprehensive statistics from both databases"""
    print("\n=== Comprehensive Statistics ===")
    
    integrated_db = IntegratedDatabase()
    stats = integrated_db.get_comprehensive_stats()
    
    print(f"\nShells Statistics:")
    print(f"  Total shells: {stats['shells']['total_count']}")
    print(f"  Rarity distribution: {stats['shells']['rarity_counts']}")
    print(f"  Class distribution: {stats['shells']['class_counts']}")
    
    print(f"\nMatrix Effects Statistics:")
    print(f"  Total matrix effects: {stats['matrix_effects']['total_count']}")
    print(f"  Source distribution: {stats['matrix_effects']['source_counts']}")
    
    print(f"\nIntegration Statistics:")
    print(f"  Matrix references by shells: {stats['integration']['total_matrix_references']}")
    print(f"  Missing matrix effects: {stats['integration']['missing_matrix_effects']}")
    print(f"  Unused matrix effects: {stats['integration']['unused_matrix_effects']}")
    print(f"  Coverage: {stats['integration']['coverage_percentage']:.1f}%")


def main():
    """Run all database demos"""
    print("Starting Shells Database Integration Demo")
    print("=" * 50)
    
    try:
        demo_shells_database()
        demo_matrix_integration()
        demo_shell_with_matrix_details()
        demo_matrix_recommendations()
        demo_comprehensive_stats()
        
        print(f"\n{'=' * 50}")
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
