# User Guide - Battery Synergy Analyzer

## Table of Contents
1. [Getting Started](#getting-started)
2. [Data Input](#data-input)
3. [Running Analysis](#running-analysis)
4. [Interpreting Results](#interpreting-results)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### First-Time Setup
1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   streamlit run app.py
   ```
4. Open browser to http://localhost:8501

### Interface Overview
- **Sidebar**: Experiment setup and file operations
- **Main Area**: Data input, analysis, visualizations, reports
- **Tabs**: Organized workflow sections

## Data Input

### Step 1: Configure Experiment
In the sidebar, enter:
- **Additive A Name**: First additive (e.g., LiPF6)
- **Additive B Name**: Second additive (e.g., VC)
- **Concentration Unit**: M, mM, vol%, wt%, etc.
- **Effect Parameter**: What you're measuring

### Step 2: Add Data Points
Required data points (minimum):
1. **Base Electrolyte** - Control without additives
2. **Additive A Only** - Single additive effect
3. **Additive B Only** - Single additive effect
4. **Combination(s)** - Both additives together

### Data Entry Format
Enter replicate values separated by commas:
```
95.2, 94.8, 95.5, 96.1
```

### Tips for Data Quality
- Use at least 3 replicates per condition
- Ensure consistent measurement conditions
- Check for outliers before input
- Document experimental conditions

## Running Analysis

### Basic Analysis
1. Navigate to "Analysis" tab
2. Click "Run Analysis" button
3. Wait for calculations (typically < 5 seconds)
4. Review results in expandable sections

### What's Calculated
- **Synergy Metrics**: CI, enhancement, Bliss deviation
- **Statistics**: ANOVA, t-tests, confidence intervals
- **Models**: Response surface (if enough data)
- **Classifications**: Synergy type determination

## Interpreting Results

### Combination Index (CI)
The primary synergy metric:
- **CI < 1**: Synergistic (better than expected)
- **CI = 1**: Additive (as expected)
- **CI > 1**: Antagonistic (worse than expected)

### Enhancement Percentage
Shows how much better/worse than expected:
- **Positive**: Performance gain
- **Negative**: Performance loss
- **Magnitude**: Effect size

### Statistical Significance
P-values indicate confidence:
- **p < 0.05**: Significant (95% confidence)
- **p < 0.01**: Highly significant (99% confidence)
- **p ≥ 0.05**: Not significant

### Visual Indicators
- 🟢 Green: Synergistic effects
- 🔴 Red: Antagonistic effects
- 🟡 Yellow: Additive/neutral effects

## Advanced Features

### Multiple Combinations
Test various concentration ratios:
1. Add multiple combination data points
2. Compare CI values across ratios
3. Identify optimal formulation

### Response Surface Analysis
With 5+ data points:
- Generates 2D concentration map
- Predicts untested combinations
- Shows R² model quality

### Data Import/Export

#### Saving Results
1. Complete analysis
2. Click "Download Results" in sidebar
3. Choose JSON format
4. Save for future reference

#### Loading Previous Data
1. Click "Load Previous Results"
2. Select JSON file
3. Data automatically populates
4. Continue analysis or modify

### Report Generation
1. Navigate to "Report" tab
2. Review auto-generated summary
3. Download as Markdown
4. Convert to PDF if needed

## Troubleshooting

### Common Issues

#### "Need at least 4 data points"
**Solution**: Add base, both single additives, and one combination minimum

#### Invalid values error
**Solution**: Check comma separation and decimal points

#### Analysis won't run
**Solution**: Verify all required fields filled in sidebar

#### Graphs not showing
**Solution**: Run analysis first, check browser compatibility

### Data Quality Checks
- **High standard deviation**: Check for outliers
- **Unexpected CI values**: Verify data entry
- **Non-significant results**: May need more replicates

### Performance Tips
- Close other browser tabs
- Use Chrome or Firefox
- Limit to 50 data points per analysis
- Clear cache if interface lags

## Best Practices

### Experimental Design
1. **Randomize** measurement order
2. **Replicate** at least 3 times
3. **Control** temperature and conditions
4. **Document** all parameters

### Data Analysis
1. **Check assumptions** before ANOVA
2. **Verify normality** of residuals
3. **Consider outliers** carefully
4. **Report confidence** intervals

### Reporting Results
1. **Include** all raw data
2. **State** statistical methods
3. **Show** error bars
4. **Discuss** practical significance

## Examples

### Example 1: Simple Synergy Test
```
Base: 85.0, 84.5, 85.2
Additive A (1M): 90.0, 89.8, 90.3
Additive B (0.5M): 88.0, 87.5, 88.2
Combination (1M + 0.5M): 95.0, 94.8, 95.5
Result: CI = 0.85 (Moderate Synergy)
```

### Example 2: Dose-Response Study
```
Test multiple combinations:
- 0.5M + 0.25M
- 1.0M + 0.5M
- 1.5M + 0.75M
- 2.0M + 1.0M
Identify optimal ratio from CI values
```

## Glossary

- **CI**: Combination Index
- **ANOVA**: Analysis of Variance
- **HSD**: Honestly Significant Difference
- **Effect Size**: Practical significance measure
- **Replicate**: Repeated measurement
- **Additive Effect**: Sum of individual effects
- **Synergy**: Greater than additive effect
- **Antagonism**: Less than additive effect