"""
File handling utilities
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..models import AnalysisResults, SynergyAnalyzer
from ..config.settings import EXPORT_CONFIG


class FileHandler:
    """Handle file operations for the analyzer"""
    
    @staticmethod
    def save_results(analyzer: SynergyAnalyzer, filepath: str) -> bool:
        """Save analysis results to JSON file"""
        try:
            if not analyzer.results:
                raise ValueError("No results to save")
            
            data = analyzer.results.to_dict()
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=EXPORT_CONFIG['json_indent'])
            
            return True
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
    
    @staticmethod
    def load_results(analyzer: SynergyAnalyzer, filepath: str) -> bool:
        """Load analysis results from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore experiment info
            meta = data['metadata']
            analyzer.set_experiment_info(
                meta['additive_a'],
                meta['additive_b'],
                meta['unit'],
                meta['effect_parameter']
            )
            
            # Restore results
            analyzer.results = AnalysisResults.from_dict(data)
            
            # Restore raw data to analyzer
            analyzer.data = analyzer.results.raw_data
            
            return True
            
        except Exception as e:
            print(f"Error loading results: {e}")
            return False
    
    @staticmethod
    def export_csv(results: AnalysisResults, filepath: str) -> bool:
        """Export results summary to CSV"""
        try:
            import pandas as pd
            
            # Create summary data
            summary_data = []
            
            for comb_id, synergy in results.synergy_results.items():
                summary_data.append({
                    'combination_id': comb_id,
                    'amount_a': synergy.amount_a,
                    'amount_b': synergy.amount_b,
                    'observed_effect': round(synergy.observed_effect, EXPORT_CONFIG['float_precision']),
                    'expected_additive': round(synergy.expected_additive, EXPORT_CONFIG['float_precision']),
                    'combination_index': round(synergy.combination_index, EXPORT_CONFIG['float_precision']),
                    'enhancement_percent': round(synergy.enhancement_percent, 2),
                    'synergy_type': synergy.synergy_type,
                    'p_value': round(synergy.p_value, 4) if synergy.p_value else None,
                    'significant': synergy.is_significant
                })
            
            df = pd.DataFrame(summary_data)
            df.to_csv(filepath, index=False, sep=EXPORT_CONFIG['csv_separator'])
            
            return True
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
    
    @staticmethod
    def create_backup(analyzer: SynergyAnalyzer, backup_dir: str = "backups") -> Optional[str]:
        """Create automatic backup of current state"""
        try:
            Path(backup_dir).mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"synergy_backup_{timestamp}.json"
            filepath = Path(backup_dir) / filename
            
            if FileHandler.save_results(analyzer, str(filepath)):
                return str(filepath)
            
            return None
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def validate_file_format(filepath: str) -> bool:
        """Validate file format for loading"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check required keys
            required_keys = ['metadata', 'raw_data']
            return all(key in data for key in required_keys)
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            return False
    
    @staticmethod
    def get_file_info(filepath: str) -> Optional[Dict[str, Any]]:
        """Get information about a saved file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            meta = data.get('metadata', {})
            raw_data = data.get('raw_data', {})
            
            return {
                'additive_a': meta.get('additive_a', 'Unknown'),
                'additive_b': meta.get('additive_b', 'Unknown'),
                'effect_parameter': meta.get('effect_parameter', 'Unknown'),
                'data_points': len(raw_data),
                'timestamp': data.get('timestamp', 'Unknown'),
                'file_size': Path(filepath).stat().st_size
            }
            
        except Exception:
            return None