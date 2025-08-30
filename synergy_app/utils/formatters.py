"""
Result formatting utilities
"""
from typing import Any, Dict, List
import numpy as np

from ..config.settings import EXPORT_CONFIG


class ResultFormatter:
    """Format analysis results for display"""
    
    @staticmethod
    def format_number(value: float, precision: int = None) -> str:
        """Format number with appropriate precision"""
        if precision is None:
            precision = EXPORT_CONFIG['float_precision']
        
        if value == float('inf'):
            return "∞"
        elif value == float('-inf'):
            return "-∞"
        elif np.isnan(value):
            return "N/A"
        else:
            return f"{value:.{precision}f}"
    
    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """Format percentage value"""
        if np.isnan(value) or value == float('inf'):
            return "N/A"
        return f"{value:.{precision}f}%"
    
    @staticmethod
    def format_p_value(p_value: float) -> str:
        """Format p-value with appropriate precision"""
        if p_value is None or np.isnan(p_value):
            return "N/A"
        elif p_value < 0.001:
            return "< 0.001"
        elif p_value < 0.01:
            return f"{p_value:.3f}"
        else:
            return f"{p_value:.4f}"
    
    @staticmethod
    def format_confidence_interval(ci_lower: float, ci_upper: float, 
                                  precision: int = 3) -> str:
        """Format confidence interval"""
        if ci_lower is None or ci_upper is None:
            return "N/A"
        return f"[{ci_lower:.{precision}f}, {ci_upper:.{precision}f}]"
    
    @staticmethod
    def format_synergy_type(synergy_type: str) -> Dict[str, str]:
        """Format synergy type with emoji and color"""
        if "Strong Synergy" in synergy_type:
            return {"text": synergy_type, "emoji": "🟢", "color": "green"}
        elif "Moderate Synergy" in synergy_type:
            return {"text": synergy_type, "emoji": "🟡", "color": "orange"}
        elif "Additive" in synergy_type:
            return {"text": synergy_type, "emoji": "⚪", "color": "gray"}
        elif "Weak Antagonism" in synergy_type:
            return {"text": synergy_type, "emoji": "🟠", "color": "orange"}
        elif "Strong Antagonism" in synergy_type:
            return {"text": synergy_type, "emoji": "🔴", "color": "red"}
        else:
            return {"text": synergy_type, "emoji": "❓", "color": "gray"}
    
    @staticmethod
    def format_condition_name(key: str, additive_a_name: str = "", 
                             additive_b_name: str = "") -> str:
        """Format condition name for display"""
        if key == 'base':
            return 'Base Electrolyte'
        elif key == 'additive_a':
            return f'{additive_a_name} Only' if additive_a_name else 'Additive A Only'
        elif key == 'additive_b':
            return f'{additive_b_name} Only' if additive_b_name else 'Additive B Only'
        elif key.startswith('combination_'):
            return f'Combination {key.split("_")[1]}'
        else:
            return key.replace('_', ' ').title()
    
    @staticmethod
    def create_summary_dict(results: Any) -> Dict[str, Any]:
        """Create summary dictionary for export"""
        summary = results.get_summary_stats()
        
        # Calculate additional metrics
        if results.synergy_results:
            ci_values = [s.combination_index for s in results.synergy_results.values() 
                        if s.combination_index != float('inf')]
            
            summary.update({
                'mean_ci': np.mean(ci_values) if ci_values else None,
                'median_ci': np.median(ci_values) if ci_values else None,
                'min_ci': np.min(ci_values) if ci_values else None,
                'max_ci': np.max(ci_values) if ci_values else None,
                'best_combination': ResultFormatter._find_best_combination(results.synergy_results)
            })
        
        return summary
    
    @staticmethod
    def _find_best_combination(synergy_results: Dict[str, Any]) -> Dict[str, Any]:
        """Find the best synergistic combination"""
        best_synergy = None
        best_ci = float('inf')
        
        for comb_id, synergy in synergy_results.items():
            if synergy.combination_index < best_ci and synergy.combination_index > 0:
                best_ci = synergy.combination_index
                best_synergy = {
                    'combination_id': comb_id,
                    'composition': f"{synergy.amount_a} + {synergy.amount_b}",
                    'ci': synergy.combination_index,
                    'enhancement_percent': synergy.enhancement_percent,
                    'synergy_type': synergy.synergy_type
                }
        
        return best_synergy
    
    @staticmethod
    def format_table_data(synergy_results: Dict[str, Any], 
                         additive_a_name: str, additive_b_name: str, 
                         unit: str) -> List[Dict[str, str]]:
        """Format data for table display"""
        table_data = []
        
        for comb_id, synergy in synergy_results.items():
            # Format synergy type
            synergy_fmt = ResultFormatter.format_synergy_type(synergy.synergy_type)
            
            table_data.append({
                'Combination': f"{synergy.amount_a} + {synergy.amount_b} {unit}",
                'Observed': ResultFormatter.format_number(synergy.observed_effect),
                'Expected': ResultFormatter.format_number(synergy.expected_additive),
                'CI': ResultFormatter.format_number(synergy.combination_index),
                'Enhancement': ResultFormatter.format_percentage(synergy.enhancement_percent),
                'P-value': ResultFormatter.format_p_value(synergy.p_value),
                'Type': f"{synergy_fmt['emoji']} {synergy_fmt['text']}",
                'Significant': '✅' if synergy.is_significant else '❌'
            })
        
        return table_data