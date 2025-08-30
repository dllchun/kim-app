"""
Data input view for Streamlit app
"""
import streamlit as st
import pandas as pd
from typing import List, Optional

from ..models import SynergyAnalyzer
from ..config.settings import VALIDATION_RULES


class DataInputView:
    """Handle data input interface"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
    
    def render(self):
        """Render data input interface"""
        st.header("📊 Data Input")
        
        if not self.analyzer.additive_a_name:
            st.warning("⚠️ Please set experiment information in the sidebar first")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_input_form()
        
        with col2:
            self._render_data_table()
    
    def _render_input_form(self):
        """Render data input form"""
        st.subheader("Add Data Points")
        
        with st.form("data_input_form", clear_on_submit=True):
            condition_type = st.selectbox(
                "Condition Type",
                ["Base Electrolyte", "Additive A Only", "Additive B Only", "Combination"],
                key="condition_type"
            )
            
            amount_a, amount_b = self._get_amounts(condition_type)
            
            # Replicate values input
            st.write("Enter replicate values:")
            values_input = st.text_area(
                f"{self.analyzer.effect_parameter} values",
                placeholder="Enter one value per line or comma-separated:\n95.2\n94.8\n95.5",
                height=100,
                key="values_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("➕ Add Data Point", type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button("📋 Paste from Clipboard", use_container_width=True):
                    st.info("Paste data in the text area above")
            
            if submit:
                self._process_data_input(condition_type, amount_a, amount_b, values_input)
    
    def _get_amounts(self, condition_type: str) -> tuple:
        """Get amount inputs based on condition type"""
        amount_a = 0.0
        amount_b = 0.0
        
        if condition_type == "Additive A Only":
            amount_a = st.number_input(
                f"{self.analyzer.additive_a_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                key="amount_a_only"
            )
        elif condition_type == "Additive B Only":
            amount_b = st.number_input(
                f"{self.analyzer.additive_b_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                key="amount_b_only"
            )
        elif condition_type == "Combination":
            col1, col2 = st.columns(2)
            with col1:
                amount_a = st.number_input(
                    f"{self.analyzer.additive_a_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    key="amount_a_comb"
                )
            with col2:
                amount_b = st.number_input(
                    f"{self.analyzer.additive_b_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    key="amount_b_comb"
                )
        
        return amount_a, amount_b
    
    def _process_data_input(self, condition_type: str, amount_a: float, 
                           amount_b: float, values_input: str):
        """Process and validate data input"""
        try:
            # Parse values (handle both comma-separated and newline-separated)
            values = self._parse_values(values_input)
            
            if not values:
                st.error("Please enter at least one value")
                return
            
            # Validate values
            if not self._validate_values(values):
                return
            
            # Determine condition name
            condition_name = self._get_condition_name(condition_type)
            
            # Add data point
            self.analyzer.add_data_point(condition_name, amount_a, amount_b, values)
            
            st.success(f"✅ Added {condition_type} data with {len(values)} replicates")
            st.rerun()
            
        except ValueError as e:
            st.error(f"Invalid input: {str(e)}")
    
    def _parse_values(self, values_input: str) -> List[float]:
        """Parse input values from string"""
        if not values_input.strip():
            return []
        
        # Try to parse as comma-separated first
        if ',' in values_input:
            parts = values_input.split(',')
        else:
            # Parse as newline-separated
            parts = values_input.split('\n')
        
        values = []
        for part in parts:
            part = part.strip()
            if part:
                try:
                    value = float(part)
                    values.append(value)
                except ValueError:
                    raise ValueError(f"'{part}' is not a valid number")
        
        return values
    
    def _validate_values(self, values: List[float]) -> bool:
        """Validate input values"""
        min_val, max_val = VALIDATION_RULES['value_range']
        
        for value in values:
            if not min_val <= value <= max_val:
                st.error(f"Value {value} is outside valid range [{min_val}, {max_val}]")
                return False
        
        if len(values) > VALIDATION_RULES.get('max_replicates', 50):
            st.error(f"Too many replicates (max: {VALIDATION_RULES.get('max_replicates', 50)})")
            return False
        
        return True
    
    def _get_condition_name(self, condition_type: str) -> str:
        """Generate appropriate condition name"""
        if condition_type == "Base Electrolyte":
            return "base"
        elif condition_type == "Additive A Only":
            return "additive_a"
        elif condition_type == "Additive B Only":
            return "additive_b"
        else:
            # Count existing combinations
            comb_count = sum(1 for k in self.analyzer.data.keys() 
                           if k.startswith('combination_'))
            return f"combination_{comb_count + 1}"
    
    def _render_data_table(self):
        """Render current data points table"""
        st.subheader("Current Data Points")
        
        if not self.analyzer.data:
            st.info("No data points added yet")
            return
        
        # Create DataFrame
        data_list = []
        for key, data in self.analyzer.data.items():
            data_list.append({
                'Condition': key.replace('_', ' ').title(),
                f'{self.analyzer.additive_a_name}': data.amount_a,
                f'{self.analyzer.additive_b_name}': data.amount_b,
                'Mean': f"{data.mean:.3f}",
                'Std Dev': f"{data.std:.3f}",
                'N': data.n,
                'CI': f"[{data.ci_lower:.3f}, {data.ci_upper:.3f}]" if data.ci_lower else "N/A"
            })
        
        df = pd.DataFrame(data_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear All Data", use_container_width=True):
                self.analyzer.data = {}
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh Statistics", use_container_width=True):
                st.rerun()
        
        with col3:
            # Check if minimum requirements met
            if self._check_minimum_data():
                st.success("✅ Ready to analyze")
            else:
                missing = self._get_missing_conditions()
                st.warning(f"⚠️ Need: {', '.join(missing)}")
    
    def _check_minimum_data(self) -> bool:
        """Check if minimum data requirements are met"""
        required = ['base', 'additive_a', 'additive_b']
        has_required = all(key in self.analyzer.data for key in required)
        
        has_combination = any(key.startswith('combination_') 
                             for key in self.analyzer.data.keys())
        
        return has_required and has_combination
    
    def _get_missing_conditions(self) -> List[str]:
        """Get list of missing required conditions"""
        missing = []
        
        if 'base' not in self.analyzer.data:
            missing.append("Base")
        if 'additive_a' not in self.analyzer.data:
            missing.append(f"{self.analyzer.additive_a_name} only")
        if 'additive_b' not in self.analyzer.data:
            missing.append(f"{self.analyzer.additive_b_name} only")
        
        has_combination = any(key.startswith('combination_') 
                             for key in self.analyzer.data.keys())
        if not has_combination:
            missing.append("At least 1 combination")
        
        return missing