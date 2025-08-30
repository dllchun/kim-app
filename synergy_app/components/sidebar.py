"""
Sidebar component for app navigation and controls
"""
import streamlit as st
import json
from datetime import datetime

from ..models import SynergyAnalyzer
from ..utils import FileHandler, DataValidator
from ..config.settings import CONCENTRATION_UNITS, EFFECT_PARAMETERS


class SidebarComponent:
    """Handle sidebar functionality"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
    
    def render(self):
        """Render complete sidebar"""
        st.header("⚙️ Experiment Setup")
        
        # Experiment configuration
        self._render_experiment_setup()
        
        st.divider()
        
        # File operations
        self._render_file_operations()
        
        st.divider()
        
        # Data validation
        self._render_data_validation()
    
    def _render_experiment_setup(self):
        """Render experiment setup form"""
        with st.form("experiment_setup"):
            st.subheader("1. Basic Information")
            
            additive_a = st.text_input(
                "Additive A Name",
                value=self.analyzer.additive_a_name,
                placeholder="e.g., LiPF6, LiTFSI"
            )
            
            additive_b = st.text_input(
                "Additive B Name", 
                value=self.analyzer.additive_b_name,
                placeholder="e.g., VC, FEC"
            )
            
            # Unit selection with common options
            unit_index = 0
            if self.analyzer.unit in CONCENTRATION_UNITS:
                unit_index = CONCENTRATION_UNITS.index(self.analyzer.unit)
            
            unit = st.selectbox(
                "Concentration Unit",
                CONCENTRATION_UNITS,
                index=unit_index
            )
            
            if unit == "Custom":
                unit = st.text_input("Enter custom unit", value=self.analyzer.unit)
            
            # Effect parameter selection
            effect_options = list(EFFECT_PARAMETERS.keys()) + ["Custom"]
            effect_index = 0
            
            if self.analyzer.effect_parameter in EFFECT_PARAMETERS:
                effect_index = list(EFFECT_PARAMETERS.keys()).index(self.analyzer.effect_parameter)
            elif self.analyzer.effect_parameter:
                effect_options.insert(-1, self.analyzer.effect_parameter)
                effect_index = len(effect_options) - 2
            
            effect_parameter = st.selectbox(
                "Effect Parameter",
                effect_options,
                index=effect_index
            )
            
            if effect_parameter == "Custom":
                effect_parameter = st.text_input(
                    "Enter custom effect parameter",
                    value=self.analyzer.effect_parameter
                )
            
            # Submit button
            if st.form_submit_button("💾 Save Setup", type="primary"):
                # Validate inputs
                valid, error_msg = DataValidator.validate_experiment_info(
                    additive_a, additive_b, unit, effect_parameter
                )
                
                if valid:
                    self.analyzer.set_experiment_info(
                        additive_a, additive_b, unit, effect_parameter
                    )
                    st.success("✅ Experiment setup saved!")
                    st.rerun()
                else:
                    st.error(f"❌ {error_msg}")
        
        # Display current setup
        if self.analyzer.additive_a_name:
            st.success("✅ Experiment configured")
            with st.expander("Current Setup"):
                st.write(f"**A**: {self.analyzer.additive_a_name}")
                st.write(f"**B**: {self.analyzer.additive_b_name}")
                st.write(f"**Unit**: {self.analyzer.unit}")
                st.write(f"**Effect**: {self.analyzer.effect_parameter}")
    
    def _render_file_operations(self):
        """Render file load/save operations"""
        st.subheader("📁 File Operations")
        
        # Load previous results
        uploaded_file = st.file_uploader(
            "Load Previous Analysis",
            type=['json'],
            help="Upload a previously saved analysis file"
        )
        
        if uploaded_file:
            try:
                # Save uploaded file temporarily
                temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.read())
                
                # Load into analyzer
                if FileHandler.load_results(self.analyzer, temp_path):
                    st.success("✅ Analysis loaded successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to load file")
                
                # Clean up temp file
                import os
                os.remove(temp_path)
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
        
        # Save current results
        if self.analyzer.results:
            st.write("#### Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save JSON", use_container_width=True):
                    self._download_json()
            
            with col2:
                if st.button("📊 Save CSV", use_container_width=True):
                    self._download_csv()
        
        # Auto-backup option
        auto_backup = st.checkbox(
            "Auto-backup on analysis",
            help="Automatically save backup after each analysis"
        )
        
        if auto_backup and hasattr(st.session_state, 'auto_backup'):
            st.session_state.auto_backup = True
    
    def _render_data_validation(self):
        """Render data validation section"""
        st.subheader("🔍 Data Validation")
        
        if not self.analyzer.data:
            st.info("No data to validate")
            return
        
        # Check data completeness
        valid, error_msg = DataValidator.validate_data_completeness(
            {k: v.__dict__ for k, v in self.analyzer.data.items()}
        )
        
        if valid:
            st.success("✅ Data requirements met")
        else:
            st.warning(f"⚠️ {error_msg}")
        
        # Data quality suggestions
        suggestions = DataValidator.suggest_data_improvements(
            {k: v.__dict__ for k, v in self.analyzer.data.items()}
        )
        
        if suggestions:
            st.write("#### Suggestions for Improvement")
            for suggestion in suggestions:
                st.info(suggestion)
        
        # Quick stats
        if self.analyzer.data:
            with st.expander("Data Summary"):
                total_points = len(self.analyzer.data)
                total_measurements = sum(len(data.values) for data in self.analyzer.data.values())
                combinations = sum(1 for k in self.analyzer.data.keys() if k.startswith('combination_'))
                
                st.write(f"**Total Conditions**: {total_points}")
                st.write(f"**Total Measurements**: {total_measurements}")
                st.write(f"**Combinations**: {combinations}")
    
    def _download_json(self):
        """Generate JSON download"""
        if not self.analyzer.results:
            st.error("No results to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"synergy_analysis_{timestamp}.json"
        
        json_data = json.dumps(
            self.analyzer.results.to_dict(), 
            indent=EXPORT_CONFIG['json_indent']
        )
        
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=filename,
            mime="application/json"
        )
    
    def _download_csv(self):
        """Generate CSV download"""
        if not self.analyzer.results:
            st.error("No results to save")
            return
        
        # This would use the FileHandler.export_csv method
        st.info("CSV export functionality - implement with FileHandler.export_csv")