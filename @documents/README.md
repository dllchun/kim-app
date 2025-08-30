# Battery Electrolyte Synergy Analyzer

## Overview
A comprehensive scientific tool for analyzing synergistic effects between additives in battery electrolyte formulations. This application helps researchers optimize electrolyte compositions by quantifying interactions between multiple additives.

## Key Features

### 1. Statistical Analysis
- **ANOVA** - One-way analysis of variance with post-hoc Tukey HSD
- **Confidence Intervals** - 95% CI using t-distribution
- **Effect Size Calculation** - Cohen's d for practical significance
- **P-value Testing** - Statistical significance determination

### 2. Synergy Models
- **Combination Index (CI)** - Classic synergy quantification
- **Loewe Additivity Model** - Dose-response based analysis
- **Bliss Independence Model** - Probabilistic independence assessment
- **Response Surface Modeling** - 2D polynomial surface fitting

### 3. Data Management
- **Flexible Data Input** - Support for variable replicates
- **JSON Import/Export** - Save and load experiments
- **Batch Processing** - Multiple combinations analysis
- **Data Validation** - Automatic error checking

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

### Basic Workflow
1. **Setup Experiment** - Enter additive names, units, and effect parameter
2. **Input Data** - Add replicate measurements for:
   - Base electrolyte (control)
   - Additive A alone
   - Additive B alone
   - Combinations of A+B
3. **Run Analysis** - Calculate synergy metrics and statistics
4. **View Results** - Interactive visualizations and reports
5. **Export Data** - Download JSON or markdown reports

## Understanding Results

### Combination Index (CI)
- **CI < 0.5**: Strong synergy
- **CI 0.5-0.9**: Moderate synergy
- **CI 0.9-1.1**: Additive effect
- **CI 1.1-2.0**: Weak antagonism
- **CI > 2.0**: Strong antagonism

### Statistical Significance
- **p < 0.05**: Statistically significant difference
- **p ≥ 0.05**: No significant difference

### Effect Measurements
Common parameters for battery research:
- Cycle Life (number of cycles)
- Coulombic Efficiency (%)
- Capacity Retention (%)
- Energy/Power Density
- Ionic Conductivity
- Thermal Stability

## Use Cases

### Battery Research
- Electrolyte formulation optimization
- Additive screening and selection
- Performance prediction
- Quality control

### Applications
- Lithium-ion batteries
- Solid-state batteries
- Flow batteries
- Supercapacitors

## File Structure
```
project/
├── app.py                 # Streamlit GUI application
├── synergy_analyzer.py    # Core analysis module
├── requirements.txt       # Python dependencies
└── @documents/           # Documentation
    ├── README.md         # This file
    ├── USER_GUIDE.md     # Detailed user guide
    └── API_REFERENCE.md  # API documentation
```

## Technical Details

### Dependencies
- **Data Processing**: pandas, numpy
- **Statistics**: scipy, scikit-learn
- **Visualization**: matplotlib, seaborn
- **GUI**: streamlit
- **File I/O**: json, datetime

### System Requirements
- Python 3.8+
- 4GB RAM minimum
- Modern web browser
- Internet connection (for Streamlit)

## Support
For issues or questions, please refer to the documentation or contact the development team.