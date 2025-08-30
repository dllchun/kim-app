"""
Core synergy analysis engine
"""
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from typing import Dict, List, Tuple, Optional, Any

from .data_models import ExperimentData, SynergyResult, AnalysisResults
from ..config.settings import ANALYSIS_CONFIG, SYNERGY_THRESHOLDS


class SynergyAnalyzer:
    """Advanced analyzer for battery electrolyte additive synergy"""
    
    def __init__(self):
        self.additive_a_name: str = ""
        self.additive_b_name: str = ""
        self.unit: str = ""
        self.effect_parameter: str = ""
        self.data: Dict[str, ExperimentData] = {}
        self.results: Optional[AnalysisResults] = None
        
    def set_experiment_info(self, additive_a: str, additive_b: str, 
                           unit: str, effect_parameter: str):
        """Set experiment information"""
        self.additive_a_name = additive_a
        self.additive_b_name = additive_b
        self.unit = unit
        self.effect_parameter = effect_parameter
    
    def add_data_point(self, condition_name: str, amount_a: float, 
                       amount_b: float, values: List[float]) -> ExperimentData:
        """Add experimental data point"""
        data_point = ExperimentData(
            amount_a=amount_a,
            amount_b=amount_b,
            values=values,
            condition_name=condition_name
        )
        
        # Calculate confidence intervals
        if len(values) > 1:
            ci_lower, ci_upper = self._calculate_confidence_intervals(values)
            data_point.ci_lower = ci_lower
            data_point.ci_upper = ci_upper
        
        self.data[condition_name] = data_point
        return data_point
    
    def analyze(self) -> AnalysisResults:
        """Perform complete analysis"""
        if not self._validate_data():
            raise ValueError("Insufficient data for analysis")
        
        # Calculate synergy metrics
        synergy_results = self._calculate_synergy_metrics()
        
        # Perform statistical tests
        statistical_results = self._perform_statistical_tests()
        
        # Fit models
        model_results = self._fit_models()
        
        # Create metadata
        metadata = {
            'additive_a': self.additive_a_name,
            'additive_b': self.additive_b_name,
            'unit': self.unit,
            'effect_parameter': self.effect_parameter
        }
        
        self.results = AnalysisResults(
            metadata=metadata,
            raw_data=self.data,
            synergy_results=synergy_results,
            statistical_results=statistical_results,
            model_results=model_results
        )
        
        return self.results
    
    def _validate_data(self) -> bool:
        """Validate minimum data requirements"""
        required = ['base', 'additive_a', 'additive_b']
        if not all(key in self.data for key in required):
            return False
        
        # Check for at least one combination
        combinations = [k for k in self.data.keys() if k.startswith('combination_')]
        return len(combinations) >= 1
    
    def _calculate_confidence_intervals(self, values: List[float], 
                                       confidence: float = ANALYSIS_CONFIG['confidence_level']) -> Tuple[Optional[float], Optional[float]]:
        """Calculate confidence intervals for given values"""
        if len(values) <= 1:
            return None, None
        
        n = len(values)
        mean = np.mean(values)
        std_err = stats.sem(values)
        
        alpha = 1 - confidence
        t_critical = stats.t.ppf(1 - alpha/2, df=n-1)
        
        margin_error = t_critical * std_err
        ci_lower = mean - margin_error
        ci_upper = mean + margin_error
        
        return ci_lower, ci_upper
    
    def _calculate_synergy_metrics(self) -> Dict[str, SynergyResult]:
        """Calculate comprehensive synergy metrics"""
        base_mean = self.data['base'].mean
        a_mean = self.data['additive_a'].mean
        b_mean = self.data['additive_b'].mean
        
        # Expected additive effect
        expected_additive = base_mean + (a_mean - base_mean) + (b_mean - base_mean)
        
        results = {}
        
        # Analyze each combination
        for key, data in self.data.items():
            if not key.startswith('combination_'):
                continue
            
            comb_mean = data.mean
            
            # Combination Index
            ci = expected_additive / comb_mean if comb_mean != 0 else float('inf')
            
            # Enhancement
            enhancement = comb_mean - expected_additive
            enhancement_percent = (enhancement / expected_additive * 100) if expected_additive != 0 else 0
            
            # Bliss Independence
            fa = (a_mean - base_mean) / base_mean if base_mean != 0 else 0
            fb = (b_mean - base_mean) / base_mean if base_mean != 0 else 0
            expected_bliss = base_mean * (1 + fa + fb + fa * fb)
            bliss_deviation = ((comb_mean - expected_bliss) / expected_bliss * 100) if expected_bliss != 0 else 0
            
            # Statistical significance
            p_value = None
            cohens_d = None
            
            if data.n > 1:
                # T-test against expected additive
                t_stat, p_value = stats.ttest_1samp(data.values, expected_additive)
                
                # Cohen's d effect size
                pooled_std = np.sqrt(
                    ((data.n - 1) * data.std**2 + 
                     (self.data['base'].n - 1) * self.data['base'].std**2) / 
                    (data.n + self.data['base'].n - 2)
                )
                cohens_d = (comb_mean - base_mean) / pooled_std if pooled_std != 0 else 0
            
            # Classify synergy
            synergy_type = self._classify_synergy(ci, p_value)
            
            results[key] = SynergyResult(
                combination_id=key,
                amount_a=data.amount_a,
                amount_b=data.amount_b,
                observed_effect=comb_mean,
                expected_additive=expected_additive,
                expected_bliss=expected_bliss,
                combination_index=ci,
                enhancement=enhancement,
                enhancement_percent=enhancement_percent,
                bliss_deviation=bliss_deviation,
                synergy_type=synergy_type,
                p_value=p_value,
                cohens_d=cohens_d,
                confidence_interval=(data.ci_lower, data.ci_upper)
            )
        
        return results
    
    def _classify_synergy(self, ci: float, p_value: Optional[float] = None) -> str:
        """Classify synergy type based on CI and significance"""
        significance = " (NS)" if p_value and p_value >= ANALYSIS_CONFIG['significance_threshold'] else ""
        
        thresholds = SYNERGY_THRESHOLDS
        
        if ci < thresholds['strong_synergy']:
            return f"Strong Synergy{significance}"
        elif ci < thresholds['moderate_synergy']:
            return f"Moderate Synergy{significance}"
        elif ci <= thresholds['additive_upper']:
            return f"Additive Effect{significance}"
        elif ci <= thresholds['weak_antagonism']:
            return f"Weak Antagonism{significance}"
        else:
            return f"Strong Antagonism{significance}"
    
    def _perform_statistical_tests(self) -> Dict[str, Any]:
        """Perform comprehensive statistical tests"""
        results = {}
        
        # ANOVA
        groups = []
        group_names = []
        
        for key, data in self.data.items():
            if data.n > 1:
                groups.append(data.values)
                group_names.append(key)
        
        if len(groups) >= 2:
            f_stat, p_value = stats.f_oneway(*groups)
            
            results['anova'] = {
                'f_statistic': f_stat,
                'p_value': p_value,
                'groups_tested': group_names,
                'significant': p_value < ANALYSIS_CONFIG['significance_threshold']
            }
            
            # Post-hoc Tukey HSD if significant and available
            if p_value < ANALYSIS_CONFIG['significance_threshold'] and len(groups) > 2:
                try:
                    from scipy.stats import tukey_hsd
                    tukey_result = tukey_hsd(*groups)
                    results['tukey'] = {
                        'pairwise_pvalues': tukey_result.pvalue.tolist(),
                        'group_names': group_names
                    }
                except ImportError:
                    results['tukey'] = {"error": "Tukey HSD requires scipy >= 1.7.0"}
        
        # Normality tests
        normality_results = {}
        for key, data in self.data.items():
            if data.n >= 3:
                stat, p = stats.shapiro(data.values)
                normality_results[key] = {
                    'statistic': stat,
                    'p_value': p,
                    'normal': p > ANALYSIS_CONFIG['significance_threshold']
                }
        
        if normality_results:
            results['normality'] = normality_results
        
        return results
    
    def _fit_models(self) -> Dict[str, Any]:
        """Fit various models to the data"""
        results = {}
        
        # Response surface model
        if len(self.data) >= 5:
            surface_result = self._fit_response_surface()
            if surface_result:
                results['response_surface'] = surface_result
        
        # Dose-response curves for individual additives
        dose_response = self._fit_dose_response()
        if dose_response:
            results['dose_response'] = dose_response
        
        return results
    
    def _fit_response_surface(self) -> Optional[Dict[str, Any]]:
        """Fit polynomial response surface model"""
        try:
            X = []
            y = []
            
            for data in self.data.values():
                X.append([data.amount_a, data.amount_b])
                y.append(data.mean)
            
            X = np.array(X)
            y = np.array(y)
            
            # Fit polynomial surface
            poly_features = PolynomialFeatures(
                degree=ANALYSIS_CONFIG['polynomial_degree'], 
                include_bias=False
            )
            X_poly = poly_features.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Calculate metrics
            r2 = model.score(X_poly, y)
            predictions = model.predict(X_poly)
            rmse = np.sqrt(np.mean((y - predictions) ** 2))
            
            return {
                'r_squared': r2,
                'rmse': rmse,
                'coefficients': model.coef_.tolist(),
                'intercept': float(model.intercept_),
                'feature_names': poly_features.get_feature_names_out(['A', 'B']).tolist(),
                'degree': ANALYSIS_CONFIG['polynomial_degree']
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _fit_dose_response(self) -> Optional[Dict[str, Any]]:
        """Fit dose-response curves"""
        results = {}
        
        # Collect dose-response data for additive A
        a_doses = []
        a_effects = []
        for data in self.data.values():
            if data.amount_b == 0 and data.amount_a > 0:
                a_doses.append(data.amount_a)
                a_effects.append(data.mean)
        
        if len(a_doses) >= 3:
            fit_result = self._fit_hill_equation(a_doses, a_effects)
            if fit_result:
                results['additive_a'] = fit_result
        
        # Similar for additive B
        b_doses = []
        b_effects = []
        for data in self.data.values():
            if data.amount_a == 0 and data.amount_b > 0:
                b_doses.append(data.amount_b)
                b_effects.append(data.mean)
        
        if len(b_doses) >= 3:
            fit_result = self._fit_hill_equation(b_doses, b_effects)
            if fit_result:
                results['additive_b'] = fit_result
        
        return results if results else None
    
    def _fit_hill_equation(self, doses: List[float], effects: List[float]) -> Optional[Dict[str, Any]]:
        """Fit Hill equation to dose-response data"""
        def hill_equation(dose, top, bottom, ic50, hill_slope):
            return bottom + (top - bottom) / (1 + (dose / ic50) ** hill_slope)
        
        try:
            doses = np.array(doses)
            effects = np.array(effects)
            
            # Initial parameter guesses
            p0 = [max(effects), min(effects), np.median(doses), 1]
            
            popt, pcov = curve_fit(hill_equation, doses, effects, p0=p0, maxfev=5000)
            
            # Calculate R²
            predicted = hill_equation(doses, *popt)
            ss_res = np.sum((effects - predicted) ** 2)
            ss_tot = np.sum((effects - np.mean(effects)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            
            return {
                'top': popt[0],
                'bottom': popt[1],
                'ic50': popt[2],
                'hill_slope': popt[3],
                'r_squared': r2,
                'parameter_errors': np.sqrt(np.diag(pcov)).tolist()
            }
        except:
            return None