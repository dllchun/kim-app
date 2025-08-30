#!/usr/bin/env python3
"""Test import script to debug package issues"""
import sys
from pathlib import Path

# Add the synergy_app package to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing synergy_app package import...")
    import synergy_app
    print("✅ synergy_app package imported successfully")
    
    print("Testing models import...")
    from synergy_app.models import SynergyAnalyzer
    print("✅ SynergyAnalyzer imported successfully")
    
    print("Testing views import...")
    from synergy_app.views import DataInputView, AnalysisView, VisualizationView, ReportView
    print("✅ Views imported successfully")
    
    print("Testing multi-parameter view import...")
    from synergy_app.views.multi_parameter_input import MultiParameterInputView
    print("✅ MultiParameterInputView imported successfully")
    
    print("Testing components import...")
    from synergy_app.components import SidebarComponent
    print("✅ SidebarComponent imported successfully")
    
    print("Testing config import...")
    from synergy_app.config.settings import APP_CONFIG
    print("✅ APP_CONFIG imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()