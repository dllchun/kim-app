"""
Setup script for synergy_app package
"""
from setuptools import setup, find_packages

setup(
    name="synergy_app",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0", 
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0"
    ]
)