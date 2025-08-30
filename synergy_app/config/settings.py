"""
Application configuration settings
"""
from typing import Dict, List

# App Configuration
APP_CONFIG = {
    "page_title": "Battery Synergy Analyzer",
    "page_icon": "🔋",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "confidence_level": 0.95,
    "significance_threshold": 0.05,
    "min_replicates": 1,
    "max_replicates": 50,
    "max_data_points": 100,
    "polynomial_degree": 2
}

# Concentration Units
CONCENTRATION_UNITS = [
    "M", "mM", "μM", "nM",
    "vol%", "wt%", "mol%",
    "g/L", "mg/mL", "μg/mL",
    "Custom"
]

# Common Effect Parameters
EFFECT_PARAMETERS = {
    "Cycle Life": {"unit": "cycles", "category": "Performance"},
    "Coulombic Efficiency": {"unit": "%", "category": "Efficiency"},
    "Capacity Retention": {"unit": "%", "category": "Performance"},
    "Energy Density": {"unit": "Wh/kg", "category": "Energy"},
    "Power Density": {"unit": "W/kg", "category": "Power"},
    "Specific Capacity": {"unit": "mAh/g", "category": "Capacity"},
    "Voltage Stability": {"unit": "V", "category": "Stability"},
    "Thermal Stability": {"unit": "°C", "category": "Safety"},
    "Ionic Conductivity": {"unit": "S/cm", "category": "Transport"},
    "Viscosity": {"unit": "cP", "category": "Physical"},
    "Impedance": {"unit": "Ω", "category": "Electrical"},
    "SEI Resistance": {"unit": "Ω·cm²", "category": "Interface"}
}

# Synergy Classification Thresholds
SYNERGY_THRESHOLDS = {
    "strong_synergy": 0.5,
    "moderate_synergy": 0.9,
    "additive_upper": 1.1,
    "weak_antagonism": 2.0
}

# Visualization Settings
PLOT_CONFIG = {
    "figure_size": (10, 6),
    "dpi": 100,
    "style": "seaborn-v0_8",
    "color_palette": {
        "base": "#808080",
        "additive_a": "#1f77b4",
        "additive_b": "#2ca02c",
        "combination": "#d62728",
        "synergy": "#28a745",
        "antagonism": "#dc3545",
        "additive": "#ffc107"
    }
}

# Export Settings
EXPORT_CONFIG = {
    "json_indent": 2,
    "csv_separator": ",",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "float_precision": 4
}

# Validation Rules
VALIDATION_RULES = {
    "min_data_points": 4,  # base + 2 additives + 1 combination
    "min_combinations": 1,
    "max_name_length": 50,
    "max_unit_length": 20,
    "value_range": (-1e6, 1e6)
}