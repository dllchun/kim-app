"""
Data models and structures for synergy analysis
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import numpy as np


@dataclass 
class ParameterData:
    """Data for a single parameter measurement"""
    parameter_name: str
    unit: str
    values: List[float]
    mean: float = field(init=False)
    std: float = field(init=False)
    n: int = field(init=False)
    ci_lower: Optional[float] = field(init=False)
    ci_upper: Optional[float] = field(init=False)
    
    def __post_init__(self):
        """Calculate statistics after initialization"""
        self.mean = np.mean(self.values)
        self.std = np.std(self.values, ddof=1) if len(self.values) > 1 else 0
        self.n = len(self.values)
        self.ci_lower = None
        self.ci_upper = None


@dataclass
class ExperimentData:
    """Data structure for experiment conditions with multiple parameters"""
    amount_a: float
    amount_b: float
    parameters: Dict[str, ParameterData] = field(default_factory=dict)
    condition_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_parameter(self, param_name: str, unit: str, values: List[float]):
        """Add a parameter measurement"""
        self.parameters[param_name] = ParameterData(param_name, unit, values)
    
    def get_parameter_names(self) -> List[str]:
        """Get list of measured parameters"""
        return list(self.parameters.keys())
    
    @property
    def primary_parameter(self) -> Optional[ParameterData]:
        """Get the first/primary parameter for backward compatibility"""
        if self.parameters:
            return next(iter(self.parameters.values()))
        return None
    
    # Backward compatibility properties
    @property
    def values(self) -> List[float]:
        """Get values from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.values
        return []
    
    @property 
    def mean(self) -> float:
        """Get mean from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.mean
        return 0.0
    
    @property
    def std(self) -> float:
        """Get std from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.std
        return 0.0
    
    @property
    def n(self) -> int:
        """Get n from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.n
        return 0
    
    @property
    def ci_lower(self) -> Optional[float]:
        """Get CI lower from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.ci_lower
        return None
    
    @property
    def ci_upper(self) -> Optional[float]:
        """Get CI upper from primary parameter"""
        if self.primary_parameter:
            return self.primary_parameter.ci_upper
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'condition_name': self.condition_name,
            'amount_a': self.amount_a,
            'amount_b': self.amount_b,
            'parameters': {
                name: {
                    'parameter_name': param.parameter_name,
                    'unit': param.unit,
                    'values': param.values,
                    'mean': param.mean,
                    'std': param.std,
                    'n': param.n,
                    'ci_lower': param.ci_lower,
                    'ci_upper': param.ci_upper
                }
                for name, param in self.parameters.items()
            },
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentData':
        """Create from dictionary"""
        # Handle both old and new format
        if 'parameters' in data:
            # New multi-parameter format
            parameters = {}
            for name, param_data in data['parameters'].items():
                param = ParameterData(
                    parameter_name=param_data['parameter_name'],
                    unit=param_data['unit'],
                    values=param_data['values']
                )
                param.ci_lower = param_data.get('ci_lower')
                param.ci_upper = param_data.get('ci_upper')
                parameters[name] = param
            
            obj = cls(
                amount_a=data['amount_a'],
                amount_b=data['amount_b'],
                parameters=parameters,
                condition_name=data.get('condition_name', '')
            )
        else:
            # Legacy single-parameter format
            param = ParameterData(
                parameter_name="Legacy Parameter",
                unit="",
                values=data['values']
            )
            param.ci_lower = data.get('ci_lower')
            param.ci_upper = data.get('ci_upper')
            
            obj = cls(
                amount_a=data['amount_a'],
                amount_b=data['amount_b'],
                parameters={"primary": param},
                condition_name=data.get('condition_name', '')
            )
        
        return obj


@dataclass
class ParameterSynergyResult:
    """Synergy results for a single parameter"""
    parameter_name: str
    observed_effect: float
    expected_additive: float
    expected_bliss: float
    combination_index: float
    enhancement: float
    enhancement_percent: float
    bliss_deviation: float
    synergy_type: str
    p_value: Optional[float] = None
    cohens_d: Optional[float] = None
    confidence_interval: Tuple[Optional[float], Optional[float]] = (None, None)
    
    @property
    def is_synergistic(self) -> bool:
        """Check if effect is synergistic"""
        return self.combination_index < 1.0
    
    @property
    def is_antagonistic(self) -> bool:
        """Check if effect is antagonistic"""
        return self.combination_index > 1.0
    
    @property
    def is_significant(self) -> bool:
        """Check if result is statistically significant"""
        return self.p_value is not None and self.p_value < 0.05


@dataclass
class SynergyResult:
    """Results for a single combination across multiple parameters"""
    combination_id: str
    amount_a: float
    amount_b: float
    parameter_results: Dict[str, ParameterSynergyResult] = field(default_factory=dict)
    
    def add_parameter_result(self, param_name: str, result: ParameterSynergyResult):
        """Add results for a specific parameter"""
        self.parameter_results[param_name] = result
    
    def get_parameter_names(self) -> List[str]:
        """Get list of analyzed parameters"""
        return list(self.parameter_results.keys())
    
    @property
    def primary_result(self) -> Optional[ParameterSynergyResult]:
        """Get primary parameter result for backward compatibility"""
        if self.parameter_results:
            return next(iter(self.parameter_results.values()))
        return None
    
    # Backward compatibility properties
    @property
    def observed_effect(self) -> float:
        """Get observed effect from primary parameter"""
        return self.primary_result.observed_effect if self.primary_result else 0.0
    
    @property
    def expected_additive(self) -> float:
        """Get expected additive from primary parameter"""
        return self.primary_result.expected_additive if self.primary_result else 0.0
    
    @property
    def expected_bliss(self) -> float:
        """Get expected bliss from primary parameter"""
        return self.primary_result.expected_bliss if self.primary_result else 0.0
    
    @property
    def combination_index(self) -> float:
        """Get combination index from primary parameter"""
        return self.primary_result.combination_index if self.primary_result else float('inf')
    
    @property
    def enhancement(self) -> float:
        """Get enhancement from primary parameter"""
        return self.primary_result.enhancement if self.primary_result else 0.0
    
    @property
    def enhancement_percent(self) -> float:
        """Get enhancement percent from primary parameter"""
        return self.primary_result.enhancement_percent if self.primary_result else 0.0
    
    @property
    def bliss_deviation(self) -> float:
        """Get bliss deviation from primary parameter"""
        return self.primary_result.bliss_deviation if self.primary_result else 0.0
    
    @property
    def synergy_type(self) -> str:
        """Get synergy type from primary parameter"""
        return self.primary_result.synergy_type if self.primary_result else "Unknown"
    
    @property
    def p_value(self) -> Optional[float]:
        """Get p-value from primary parameter"""
        return self.primary_result.p_value if self.primary_result else None
    
    @property
    def cohens_d(self) -> Optional[float]:
        """Get Cohen's d from primary parameter"""
        return self.primary_result.cohens_d if self.primary_result else None
    
    @property
    def confidence_interval(self) -> Tuple[Optional[float], Optional[float]]:
        """Get confidence interval from primary parameter"""
        return self.primary_result.confidence_interval if self.primary_result else (None, None)
    
    @property
    def is_synergistic(self) -> bool:
        """Check if primary effect is synergistic"""
        return self.primary_result.is_synergistic if self.primary_result else False
    
    @property
    def is_antagonistic(self) -> bool:
        """Check if primary effect is antagonistic"""
        return self.primary_result.is_antagonistic if self.primary_result else False
    
    @property
    def is_significant(self) -> bool:
        """Check if primary result is statistically significant"""
        return self.primary_result.is_significant if self.primary_result else False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'combination_id': self.combination_id,
            'amount_a': self.amount_a,
            'amount_b': self.amount_b,
            'observed_effect': self.observed_effect,
            'expected_additive': self.expected_additive,
            'expected_bliss': self.expected_bliss,
            'combination_index': self.combination_index,
            'enhancement': self.enhancement,
            'enhancement_percent': self.enhancement_percent,
            'bliss_deviation': self.bliss_deviation,
            'synergy_type': self.synergy_type,
            'p_value': self.p_value,
            'cohens_d': self.cohens_d,
            'confidence_interval': self.confidence_interval
        }
    
    @property
    def is_synergistic(self) -> bool:
        """Check if effect is synergistic"""
        return self.combination_index < 1.0
    
    @property
    def is_antagonistic(self) -> bool:
        """Check if effect is antagonistic"""
        return self.combination_index > 1.0
    
    @property
    def is_significant(self) -> bool:
        """Check if result is statistically significant"""
        return self.p_value is not None and self.p_value < 0.05


@dataclass
class AnalysisResults:
    """Complete analysis results container"""
    metadata: Dict[str, Any]
    raw_data: Dict[str, ExperimentData]
    synergy_results: Dict[str, SynergyResult]
    statistical_results: Dict[str, Any]
    model_results: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            'metadata': self.metadata,
            'raw_data': {k: v.to_dict() for k, v in self.raw_data.items()},
            'synergy_results': {k: v.to_dict() for k, v in self.synergy_results.items()},
            'statistical_results': self.statistical_results,
            'model_results': self.model_results,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResults':
        """Create from dictionary"""
        raw_data = {
            k: ExperimentData.from_dict(v) 
            for k, v in data['raw_data'].items()
        }
        
        synergy_results = {}
        for k, v in data.get('synergy_results', {}).items():
            synergy_results[k] = SynergyResult(**v)
        
        return cls(
            metadata=data['metadata'],
            raw_data=raw_data,
            synergy_results=synergy_results,
            statistical_results=data.get('statistical_results', {}),
            model_results=data.get('model_results', {})
        )
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        synergistic = sum(1 for r in self.synergy_results.values() if r.is_synergistic)
        antagonistic = sum(1 for r in self.synergy_results.values() if r.is_antagonistic)
        significant = sum(1 for r in self.synergy_results.values() if r.is_significant)
        
        return {
            'total_combinations': len(self.synergy_results),
            'synergistic': synergistic,
            'antagonistic': antagonistic,
            'additive': len(self.synergy_results) - synergistic - antagonistic,
            'significant': significant,
            'data_points': len(self.raw_data)
        }