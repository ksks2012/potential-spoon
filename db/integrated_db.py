import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from .shells_db import ShellsDatabase
from .matrix_db import MatrixDatabase


class IntegratedDatabase:
    """Integrated database handler for Shells and Matrix Effects"""
    
    def __init__(self, shells_db_path: str = "./db/shells.db", matrix_db_path: str = "./db/matrix_effects.db"):
        """Initialize both database connections"""
        self.shells_db = ShellsDatabase(shells_db_path)
        self.matrix_db = MatrixDatabase(matrix_db_path)
    
    def get_shell_with_matrix_effects(self, shell_name: str) -> Optional[Dict]:
        """Get shell data with detailed matrix effects information"""
        shell_data = self.shells_db.get_shell_by_name(shell_name)
        if not shell_data:
            return None
        
        # Get detailed matrix effects for each set
        if 'sets' in shell_data:
            detailed_sets = []
            for set_name in shell_data['sets']:
                matrix_effect = self.matrix_db.get_matrix_effect_by_name(set_name)
                if matrix_effect:
                    detailed_sets.append(matrix_effect)
                else:
                    # If matrix effect not found, keep the name
                    detailed_sets.append({'name': set_name, 'status': 'not_found'})
            
            shell_data['matrix_effects'] = detailed_sets
        
        return shell_data
    
    def get_shells_compatible_with_matrix(self, matrix_name: str) -> List[Dict]:
        """Get all shells that can use a specific matrix effect"""
        shells = self.shells_db.get_shells_by_matrix_set(matrix_name)
        return shells
    
    def get_matrix_usage_analysis(self) -> Dict:
        """Analyze matrix set usage across shells"""
        shells_summary = self.shells_db.get_stats_summary()
        matrix_summary = self.matrix_db.get_stats_summary()
        
        # Get all matrix sets used by shells
        all_shells = self.shells_db.get_all_shells()
        used_matrix_sets = set()
        
        for shell in all_shells:
            if 'sets' in shell:
                used_matrix_sets.update(shell['sets'])
        
        # Get all available matrix effects
        all_matrix_effects = self.matrix_db.get_all_matrix_effects()
        available_matrix_names = {matrix['name'] for matrix in all_matrix_effects}
        
        # Find missing matrix effects (referenced by shells but not in matrix DB)
        missing_matrix_effects = used_matrix_sets - available_matrix_names
        
        # Find unused matrix effects (in matrix DB but not used by any shell)
        unused_matrix_effects = available_matrix_names - used_matrix_sets
        
        return {
            'shells_summary': shells_summary,
            'matrix_summary': matrix_summary,
            'used_matrix_sets': list(used_matrix_sets),
            'missing_matrix_effects': list(missing_matrix_effects),
            'unused_matrix_effects': list(unused_matrix_effects),
            'total_matrix_sets_used': len(used_matrix_sets),
            'total_matrix_effects_available': len(available_matrix_names),
            'coverage_percentage': len(used_matrix_sets & available_matrix_names) / max(len(used_matrix_sets), 1) * 100
        }
    
    def validate_shell_matrix_references(self) -> Dict:
        """Validate that all shell matrix set references exist in matrix database"""
        validation_results = {
            'valid_references': [],
            'invalid_references': [],
            'shells_with_invalid_refs': []
        }
        
        all_shells = self.shells_db.get_all_shells()
        
        for shell in all_shells:
            shell_name = shell.get('name', 'Unknown')
            shell_sets = shell.get('sets', [])
            
            invalid_refs_for_shell = []
            
            for set_name in shell_sets:
                matrix_effect = self.matrix_db.get_matrix_effect_by_name(set_name)
                if matrix_effect:
                    validation_results['valid_references'].append({
                        'shell': shell_name,
                        'matrix_set': set_name
                    })
                else:
                    validation_results['invalid_references'].append({
                        'shell': shell_name,
                        'matrix_set': set_name
                    })
                    invalid_refs_for_shell.append(set_name)
            
            if invalid_refs_for_shell:
                validation_results['shells_with_invalid_refs'].append({
                    'shell': shell_name,
                    'invalid_sets': invalid_refs_for_shell
                })
        
        return validation_results
    
    def create_missing_matrix_effects(self, default_source: str = "auto_generated") -> int:
        """Create placeholder matrix effects for missing references"""
        validation = self.validate_shell_matrix_references()
        created_count = 0
        
        # Get unique missing matrix set names
        missing_sets = set()
        for invalid_ref in validation['invalid_references']:
            missing_sets.add(invalid_ref['matrix_set'])
        
        for set_name in missing_sets:
            # Create a basic placeholder matrix effect
            placeholder_data = {
                'name': set_name,
                'source': default_source,
                'type': ['Unknown'],
                'effects': [
                    {
                        'required': 2,
                        'total': 4,
                        'effect': {
                            'placeholder': 'Effect data not available'
                        }
                    },
                    {
                        'required': 4,
                        'total': 4,
                        'effect': {
                            'placeholder': 'Full set effect not available'
                        }
                    }
                ]
            }
            
            try:
                matrix_id = self.matrix_db.insert_matrix_effect(placeholder_data)
                if matrix_id:
                    created_count += 1
                    print(f"Created placeholder matrix effect: {set_name} (ID: {matrix_id})")
            except Exception as e:
                print(f"Error creating placeholder for {set_name}: {e}")
        
        return created_count
    
    def get_shell_recommendations(self, matrix_effects: List[str]) -> List[Dict]:
        """Get shell recommendations based on available matrix effects"""
        recommendations = []
        
        all_shells = self.shells_db.get_all_shells()
        
        for shell in all_shells:
            shell_name = shell.get('name', 'Unknown')
            shell_sets = shell.get('sets', [])
            
            # Calculate compatibility score
            compatible_sets = [s for s in shell_sets if s in matrix_effects]
            compatibility_score = len(compatible_sets) / len(shell_sets) if shell_sets else 0
            
            if compatibility_score > 0:
                recommendations.append({
                    'shell': shell_name,
                    'shell_data': shell,
                    'compatible_sets': compatible_sets,
                    'total_sets': len(shell_sets),
                    'compatibility_score': compatibility_score,
                    'missing_sets': [s for s in shell_sets if s not in matrix_effects]
                })
        
        # Sort by compatibility score (highest first)
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return recommendations
    
    def export_combined_data(self, output_file: str = "combined_shells_matrix_data.json"):
        """Export combined shells and matrix data to JSON"""
        combined_data = {
            'shells': [],
            'matrix_effects': self.matrix_db.get_all_matrix_effects(),
            'analysis': self.get_matrix_usage_analysis(),
            'validation': self.validate_shell_matrix_references()
        }
        
        # Get all shells with matrix effects details
        all_shells = self.shells_db.get_all_shells()
        for shell in all_shells:
            shell_with_matrix = self.get_shell_with_matrix_effects(shell['name'])
            combined_data['shells'].append(shell_with_matrix)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            print(f"Combined data exported to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting combined data: {e}")
            return False
    
    def clear_all_data(self):
        """Clear all data from both databases"""
        self.shells_db.clear_all_data()
        self.matrix_db.clear_all_data()
        print("All data cleared from both shells and matrix databases")
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics from both databases"""
        shells_stats = self.shells_db.get_stats_summary()
        matrix_stats = self.matrix_db.get_stats_summary()
        usage_analysis = self.get_matrix_usage_analysis()
        
        return {
            'shells': shells_stats,
            'matrix_effects': matrix_stats,
            'integration': {
                'total_matrix_references': usage_analysis['total_matrix_sets_used'],
                'missing_matrix_effects': len(usage_analysis['missing_matrix_effects']),
                'unused_matrix_effects': len(usage_analysis['unused_matrix_effects']),
                'coverage_percentage': usage_analysis['coverage_percentage']
            }
        }
