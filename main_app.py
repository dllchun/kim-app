"""
Main Streamlit application entry point
"""
import streamlit as st
import sys
from pathlib import Path

# Add the synergy_app package to path
sys.path.append(str(Path(__file__).parent))

from synergy_app.models import SynergyAnalyzer
from synergy_app.views import DataInputView, AnalysisView, VisualizationView, ReportView
from synergy_app.components import SidebarComponent
from synergy_app.config.settings import APP_CONFIG


def setup_page():
    """Configure Streamlit page"""
    st.set_page_config(**APP_CONFIG)
    
    # Custom CSS
    st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .synergy-positive {
            color: #28a745;
            font-weight: bold;
        }
        .synergy-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .synergy-neutral {
            color: #6c757d;
            font-weight: bold;
        }
        .stTab {
            font-size: 16px;
        }
        .main-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SynergyAnalyzer()
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    
    if 'auto_backup' not in st.session_state:
        st.session_state.auto_backup = False


def main():
    """Main application function"""
    setup_page()
    initialize_session_state()
    
    # App header
    st.markdown("""
    <div class="main-header">
        <h1>🔋 Battery Electrolyte Synergy Analyzer</h1>
        <p><em>Advanced Analysis Tool for Additive Interactions</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    analyzer = st.session_state.analyzer
    
    # Sidebar
    with st.sidebar:
        sidebar = SidebarComponent(analyzer)
        sidebar.render()
    
    # Main content tabs
    tab_names = ["📊 Data Input", "📈 Analysis", "📉 Visualizations", "📋 Report"]
    tabs = st.tabs(tab_names)
    
    # Data Input Tab
    with tabs[0]:
        data_input_view = DataInputView(analyzer)
        data_input_view.render()
    
    # Analysis Tab
    with tabs[1]:
        analysis_view = AnalysisView(analyzer)
        analysis_view.render()
    
    # Visualizations Tab
    with tabs[2]:
        viz_view = VisualizationView(analyzer)
        viz_view.render()
    
    # Report Tab
    with tabs[3]:
        report_view = ReportView(analyzer)
        report_view.render()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        Battery Electrolyte Synergy Analyzer | 
        <a href="https://github.com/your-repo" target="_blank">Documentation</a> | 
        Version 1.0.0
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()