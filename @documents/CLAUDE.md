# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This repository contains a Python-based Advanced Synergy Analyzer for battery electrolyte research. The tool analyzes synergistic effects between additives in electrolyte formulations using various statistical and mathematical models.

## Code Structure
- `refernece.txt` - Contains the main `AdvancedSynergyAnalyzer` class implementation with methods for:
  - Data input and collection from experimental tests
  - Statistical analysis (ANOVA, confidence intervals, t-tests)
  - Synergy modeling (Loewe Additivity, Bliss Independence)
  - Response surface fitting
  - Report generation

## Development Commands
Since this is a standalone Python script without package.json or requirements.txt:
- Run the analyzer: `python refernece.txt` (Note: file should be renamed to .py extension)
- Install required dependencies: `pip install pandas numpy matplotlib seaborn scipy scikit-learn reportlab`

## Key Technical Details
- The analyzer uses various synergy models including Combination Index (CI), Loewe Additivity, and Bliss Independence
- Statistical significance is determined through ANOVA, t-tests, and Tukey HSD post-hoc analysis
- Effect sizes are calculated using Cohen's d
- Response surface modeling uses polynomial regression for multiple combination analysis
- PDF report generation capability via reportlab (optional dependency)

## Important Notes
- The code in `refernece.txt` appears to be incomplete - it ends mid-function at line 635
- Methods are defined outside the class and then manually added to the class using assignment
- The file extension should be `.py` instead of `.txt` for proper Python execution