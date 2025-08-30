"""
Data models and structures for synergy analysis
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import numpy as np


@dataclass
class ExperimentData:
    """Data structure for experiment conditions"""
    amount_a: float
    amount_b: float
    values: List[float]
    condition_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'condition_name': self.condition_name,
            'amount_a': self.amount_a,
            'amount_b': self.amount_b,
            'values': self.values,
            'mean': self.mean,
            'std': self.std,
            'n': self.n,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentData':
        """Create from dictionary"""
        obj = cls(
            amount_a=data['amount_a'],
            amount_b=data['amount_b'],
            values=data['values'],
            condition_name=data.get('condition_name', '')
        )
        if 'ci_lower' in data:
            obj.ci_lower = data['ci_lower']
        if 'ci_upper' in data:
            obj.ci_upper = data['ci_upper']
        return obj


@dataclass
class SynergyResult:
    """Results for a single combination"""
    combination_id: str
    amount_a: float
    amount_b: float
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