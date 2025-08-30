# API Reference - Synergy Analyzer Module

## Class: `AdvancedSynergyAnalyzer`

Main class for performing synergy analysis on experimental data.

### Constructor
```python
analyzer = AdvancedSynergyAnalyzer()
```
Creates a new analyzer instance with empty data structures.

### Methods

#### `set_experiment_info(additive_a, additive_b, unit, effect_parameter)`
Configure experiment metadata.

**Parameters:**
- `additive_a` (str): Name of first additive
- `additive_b` (str): Name of second additive
- `unit` (str): Concentration unit (M, mM, vol%, etc.)
- `effect_parameter` (str): Measured effect (e.g., "Cycle Life")

**Example:**
```python
analyzer.set_experiment_info("LiPF6", "VC", "M", "Capacity Retention (%)")
```

---

#### `add_data_point(condition_name, amount_a, amount_b, values)`
Add experimental data for a specific condition.

**Parameters:**
- `condition_name` (str): Identifier for condition ("base", "additive_a", etc.)
- `amount_a` (float): Concentration of additive A
- `amount_b` (float): Concentration of additive B
- `values` (List[float]): Replicate measurements

**Example:**
```python
analyzer.add_data_point("base", 0, 0, [85.0, 84.5, 85.2])
analyzer.add_data_point("combination_1", 1.0, 0.5, [95.0, 94.8, 95.5])
```

---

#### `calculate_synergy_metrics() -> Dict[str, Any]`
Calculate comprehensive synergy metrics for all combinations.

**Returns:**
Dictionary containing:
- `base_effect`: Control measurement
- `a_effect`: Additive A alone effect
- `b_effect`: Additive B alone effect
- `expected_additive`: Theoretical additive effect
- `combinations`: Dict of combination results

**Combination Results Include:**
- `observed_effect`: Measured effect
- `combination_index`: CI value
- `enhancement`: Absolute improvement
- `enhancement_percent`: Relative improvement
- `synergy_type`: Classification string
- `p_value`: Statistical significance

**Example:**
```python
results = analyzer.calculate_synergy_metrics()
print(f"CI: {results['combinations']['combination_1']['combination_index']}")
```

---

#### `perform_anova_analysis() -> Dict[str, Any]`
Perform one-way ANOVA across all conditions.

**Returns:**
Dictionary containing:
- `f_statistic`: F-test statistic
- `p_value`: ANOVA p-value
- `groups_tested`: List of group names
- `significant`: Boolean significance flag
- `tukey`: Post-hoc test results (if applicable)

**Example:**
```python
anova = analyzer.perform_anova_analysis()
if anova['significant']:
    print("Groups are significantly different")
```

---

#### `calculate_confidence_intervals(values, confidence=0.95) -> Tuple[float, float]`
Calculate confidence intervals using t-distribution.

**Parameters:**
- `values` (List[float]): Data values
- `confidence` (float): Confidence level (default 0.95)

**Returns:**
- Tuple of (lower_bound, upper_bound) or (None, None) if n≤1

**Example:**
```python
lower, upper = analyzer.calculate_confidence_intervals([95.0, 94.8, 95.5])
print(f"95% CI: [{lower:.2f}, {upper:.2f}]")
```

---

#### `fit_response_surface() -> Dict[str, Any]`
Fit 2D polynomial response surface model.

**Returns:**
Dictionary containing:
- `r_squared`: Model R² score
- `coefficients`: Model coefficients
- `intercept`: Y-intercept
- `feature_names`: Polynomial feature names

**Requirements:**
- At least 5 data points
- Variable concentrations

**Example:**
```python
surface = analyzer.fit_response_surface()
print(f"Model R²: {surface['r_squared']:.4f}")
```

---

#### `generate_plots() -> Dict[str, plt.Figure]`
Generate visualization figures.

**Returns:**
Dictionary of matplotlib figures:
- `effects_comparison`: Bar chart of all conditions
- `synergy_analysis`: Observed vs expected comparison

**Example:**
```python
figures = analyzer.generate_plots()
figures['effects_comparison'].savefig('effects.png')
```

---

#### `save_results(filename)`
Save complete analysis to JSON file.

**Parameters:**
- `filename` (str): Output file path

**Saves:**
- Metadata (additives, units, parameters)
- Raw data with statistics
- Analysis results
- Model outputs

**Example:**
```python
analyzer.save_results('experiment_001.json')
```

---

#### `load_results(filename)`
Load previous analysis from JSON file.

**Parameters:**
- `filename` (str): Input file path

**Restores:**
- All experiment data
- Previous calculations
- Model results

**Example:**
```python
analyzer.load_results('experiment_001.json')
```

---

## Class: `ExperimentData`

Data container for experimental conditions (dataclass).

### Attributes
- `amount_a` (float): Additive A concentration
- `amount_b` (float): Additive B concentration
- `values` (List[float]): Replicate measurements
- `mean` (float): Calculated mean
- `std` (float): Standard deviation
- `n` (int): Number of replicates

### Auto-calculated Properties
Mean, std, and n are automatically calculated from values during initialization.

---

## Constants

### `COMMON_EFFECTS`
Dictionary of standard effect measurements:
```python
{
    "Cycle Life (number of cycles)": "cycles",
    "Coulombic Efficiency (CE) (%)": "%",
    "Capacity Retention (%)": "%",
    "Energy Density (Wh/kg or Wh/L)": "Wh/kg",
    "Power Density (W/kg or W/L)": "W/kg",
    "Specific Capacity (mAh/g)": "mAh/g",
    "Voltage Stability (V)": "V",
    "Thermal Stability (°C)": "°C",
    "Ionic Conductivity (S/cm)": "S/cm",
    "Viscosity (cP)": "cP"
}
```

---

## Usage Example

### Complete Workflow
```python
from synergy_analyzer import AdvancedSynergyAnalyzer

# Initialize analyzer
analyzer = AdvancedSynergyAnalyzer()

# Set experiment info
analyzer.set_experiment_info(
    additive_a="LiPF6",
    additive_b="VC",
    unit="M",
    effect_parameter="Capacity Retention (%)"
)

# Add experimental data
analyzer.add_data_point("base", 0, 0, [85.0, 84.5, 85.2])
analyzer.add_data_point("additive_a", 1.0, 0, [90.0, 89.8, 90.3])
analyzer.add_data_point("additive_b", 0, 0.5, [88.0, 87.5, 88.2])
analyzer.add_data_point("combination_1", 1.0, 0.5, [95.0, 94.8, 95.5])

# Run analysis
results = analyzer.calculate_synergy_metrics()
anova = analyzer.perform_anova_analysis()

# Check synergy
ci = results['combinations']['combination_1']['combination_index']
if ci < 1:
    print(f"Synergistic effect detected (CI = {ci:.3f})")

# Generate plots
figures = analyzer.generate_plots()

# Save results
analyzer.save_results('synergy_analysis.json')
```

---

## Error Handling

### Common Exceptions
- `ValueError`: Invalid data format
- `KeyError`: Missing required data points
- `ImportError`: Missing optional dependencies

### Validation Rules
1. Minimum 4 data points required (base + 2 additives + 1 combination)
2. At least 1 replicate per condition
3. Non-zero denominators for CI calculation
4. Valid concentration values (≥0)

---

## Performance Considerations

### Memory Usage
- Linear with number of data points
- ~1KB per data point with 10 replicates

### Computation Time
- Synergy metrics: O(n) where n = combinations
- ANOVA: O(n*m) where m = replicates
- Response surface: O(n³) for polynomial fitting

### Recommended Limits
- Maximum 100 data points
- Maximum 50 replicates per condition
- Polynomial degree ≤ 3 for response surface