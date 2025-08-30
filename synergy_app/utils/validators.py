"""
Data validation utilities
"""
from typing import List, Dict, Any, Tuple
import numpy as np

from ..config.settings import VALIDATION_RULES


class DataValidator:
    """Validate experimental data and inputs"""
    
    @staticmethod
    def validate_experiment_info(additive_a: str, additive_b: str, 
                                unit: str, effect_parameter: str) -> Tuple[bool, str]:
        """Validate experiment setup information"""
        errors = []
        
        # Check required fields
        if not additive_a.strip():
            errors.append("Additive A name is required")
        elif len(additive_a) > VALIDATION_RULES['max_name_length']:
            errors.append(f"Additive A name too long (max {VALIDATION_RULES['max_name_length']} chars)")
        
        if not additive_b.strip():
            errors.append("Additive B name is required")
        elif len(additive_b) > VALIDATION_RULES['max_name_length']:
            errors.append(f"Additive B name too long (max {VALIDATION_RULES['max_name_length']} chars)")
        
        if not unit.strip():
            errors.append("Unit is required")
        elif len(unit) > VALIDATION_RULES['max_unit_length']:
            errors.append(f"Unit too long (max {VALIDATION_RULES['max_unit_length']} chars)")
        
        if not effect_parameter.strip():
            errors.append("Effect parameter is required")
        
        # Check for duplicate names
        if additive_a.strip().lower() == additive_b.strip().lower():
            errors.append("Additive names must be different")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""
    
    @staticmethod
    def validate_concentration(amount: float, unit: str) -> Tuple[bool, str]:
        """Validate concentration value"""
        if amount < 0:
            return False, "Concentration cannot be negative"
        
        # Unit-specific validation
        if unit in ['%', 'vol%', 'wt%', 'mol%']:
            if amount > 100:
                return False, f"Percentage values cannot exceed 100% (got {amount}%)"
        
        # General range check
        min_val, max_val = VALIDATION_RULES['value_range']
        if not min_val <= amount <= max_val:
            return False, f"Value outside valid range [{min_val}, {max_val}]"
        
        return True, ""
    
    @staticmethod
    def validate_replicate_values(values: List[float]) -> Tuple[bool, str]:
        """Validate replicate measurement values"""
        if not values:
            return False, "At least one value is required"
        
        if len(values) > VALIDATION_RULES.get('max_replicates', 50):
            return False, f"Too many replicates (max: {VALIDATION_RULES.get('max_replicates', 50)})"
        
        # Check for valid numbers
        min_val, max_val = VALIDATION_RULES['value_range']
        
        for i, value in enumerate(values):
            if not isinstance(value, (int, float)):
                return False, f"Value {i+1} is not a number"
            
            if np.isnan(value) or np.isinf(value):
                return False, f"Value {i+1} is invalid (NaN or Inf)"
            
            if not min_val <= value <= max_val:
                return False, f"Value {i+1} ({value}) outside valid range"
        
        # Check for excessive variability (CV > 50%)
        if len(values) > 1:
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if mean_val != 0:
                cv = (std_val / abs(mean_val)) * 100
                if cv > 50:
                    return False, f"High variability detected (CV = {cv:.1f}%). Check for outliers."
        
        return True, ""
    
    @staticmethod
    def validate_data_completeness(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that minimum data requirements are met"""
        errors = []
        
        # Check required conditions
        required_conditions = ['base', 'additive_a', 'additive_b']
        missing_conditions = [cond for cond in required_conditions if cond not in data]
        
        if missing_conditions:
            errors.append(f"Missing required conditions: {', '.join(missing_conditions)}")
        
        # Check for at least one combination
        combinations = [key for key in data.keys() if key.startswith('combination_')]
        if not combinations:
            errors.append("At least one combination is required")
        
        # Check data quality
        total_points = len(data)
        if total_points < VALIDATION_RULES['min_data_points']:
            errors.append(f"Insufficient data points (need {VALIDATION_RULES['min_data_points']}, have {total_points})")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""
    
    @staticmethod
    def check_outliers(values: List[float], threshold: float = 2.5) -> List[int]:
        """Detect potential outliers using modified Z-score"""
        if len(values) < 3:
            return []
        
        values = np.array(values)
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        
        if mad == 0:
            return []
        
        modified_z_scores = 0.6745 * (values - median) / mad
        outlier_indices = np.where(np.abs(modified_z_scores) > threshold)[0].tolist()
        
        return outlier_indices
    
    @staticmethod
    def suggest_data_improvements(data: Dict[str, Any]) -> List[str]:
        """Suggest improvements to data quality"""
        suggestions = []
        
        # Check replicate counts
        low_replicate_conditions = []
        for key, condition_data in data.items():
            n_replicates = len(condition_data.get('values', []))
            if n_replicates < 3:
                low_replicate_conditions.append(key)
        
        if low_replicate_conditions:
            suggestions.append(
                f"Consider adding more replicates to: {', '.join(low_replicate_conditions)} "
                f"(currently < 3 replicates)"
            )
        
        # Check for concentration ranges
        combinations = [data[key] for key in data.keys() if key.startswith('combination_')]
        if len(combinations) < 3:
            suggestions.append("Add more combination ratios to improve model fitting")
        
        # Check for outliers
        for key, condition_data in data.items():
            values = condition_data.get('values', [])
            outliers = DataValidator.check_outliers(values)
            if outliers:
                suggestions.append(
                    f"Potential outliers detected in {key} at positions: {outliers}. "
                    f"Consider reviewing these measurements."
                )
        
        return suggestions