"""
Multi-parameter data input view
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any

from ..models import SynergyAnalyzer
from ..config.settings import EFFECT_PARAMETERS, CONCENTRATION_UNITS


class MultiParameterInputView:
    """Handle multi-parameter data input"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
    
    def render(self):
        """Render multi-parameter input interface"""
        st.header("📊 Multi-Parameter Data Input")
        
        if not self.analyzer.additive_a_name:
            st.warning("⚠️ Please set experiment information in the sidebar first")
            return
        
        # Parameter management
        self._render_parameter_setup()
        
        # Multi-parameter data input
        self._render_multi_input_form()
        
        # Current data display
        self._render_multi_parameter_table()
    
    def _render_parameter_setup(self):
        """Setup multiple parameters to measure"""
        st.subheader("🎯 Parameter Configuration")
        
        # Initialize session state for parameters
        if 'active_parameters' not in st.session_state:
            st.session_state.active_parameters = [
                {'name': self.analyzer.effect_parameter, 'unit': '', 'enabled': True}
            ]
        
        # Add parameter interface
        with st.expander("➕ Add More Parameters", expanded=False):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                param_options = list(EFFECT_PARAMETERS.keys()) + ["Custom"]
                new_param = st.selectbox(
                    "Select Parameter",
                    param_options,
                    key="new_param_select"
                )
                
                if new_param == "Custom":
                    new_param = st.text_input("Enter custom parameter name", key="custom_param")
            
            with col2:
                if new_param in EFFECT_PARAMETERS:
                    default_unit = EFFECT_PARAMETERS[new_param]['unit']
                else:
                    default_unit = ""
                
                new_unit = st.text_input("Unit", value=default_unit, key="new_param_unit")
            
            with col3:
                if st.button("➕ Add"):
                    if new_param and new_param not in [p['name'] for p in st.session_state.active_parameters]:
                        st.session_state.active_parameters.append({
                            'name': new_param,
                            'unit': new_unit,
                            'enabled': True
                        })
                        st.rerun()
        
        # Active parameters display
        st.write("**Active Parameters:**")
        
        for i, param in enumerate(st.session_state.active_parameters):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.write(f"**{param['name']}**")
            with col2:
                st.write(f"Unit: {param['unit']}")
            with col3:
                enabled = st.checkbox("", value=param['enabled'], key=f"param_enabled_{i}")
                st.session_state.active_parameters[i]['enabled'] = enabled
            with col4:
                if len(st.session_state.active_parameters) > 1:
                    if st.button("🗑️", key=f"del_param_{i}"):
                        st.session_state.active_parameters.pop(i)
                        st.rerun()
    
    def _render_multi_input_form(self):
        """Render form for multi-parameter input"""
        st.subheader("📝 Add Multi-Parameter Data")
        
        # Condition setup (outside form for dynamic updates)
        condition_type = st.selectbox(
            "Condition Type",
            ["Base Electrolyte", "Additive A Only", "Additive B Only", "Combination"],
            key="multi_condition_type"
        )
        
        # Amount inputs
        amount_a, amount_b = self._get_amounts(condition_type)
        
        # Multi-parameter input form
        with st.form("multi_param_form"):
            st.write("**Enter values for each parameter:**")
            
            # Create input fields for each active parameter
            param_values = {}
            active_params = [p for p in st.session_state.active_parameters if p['enabled']]
            
            # Use columns for better layout
            if len(active_params) <= 2:
                cols = st.columns(len(active_params))
            else:
                cols = st.columns(2)
            
            for i, param in enumerate(active_params):
                col_idx = i % len(cols)
                
                with cols[col_idx]:
                    st.write(f"**{param['name']}** ({param['unit']})")
                    values_input = st.text_area(
                        f"Values",
                        placeholder="95.2\n94.8\n95.5",
                        height=80,
                        key=f"values_{param['name']}_{i}"
                    )
                    param_values[param['name']] = {
                        'values_input': values_input,
                        'unit': param['unit']
                    }
            
            # Submit button
            if st.form_submit_button("➕ Add Multi-Parameter Data", type="primary"):
                self._process_multi_parameter_input(condition_type, amount_a, amount_b, param_values)
    
    def _get_amounts(self, condition_type: str) -> tuple:
        """Get amount inputs (same as single parameter version)"""
        amount_a = 0.0
        amount_b = 0.0
        
        if condition_type == "Base Electrolyte":
            st.info("🧪 Base electrolyte: Both amounts = 0")
            
        elif condition_type == "Additive A Only":
            amount_a = st.number_input(
                f"🅰️ {self.analyzer.additive_a_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                value=1.0,
                key="multi_amount_a_only"
            )
            
        elif condition_type == "Additive B Only":
            amount_b = st.number_input(
                f"🅱️ {self.analyzer.additive_b_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                value=1.0,
                key="multi_amount_b_only"
            )
            
        elif condition_type == "Combination":
            col1, col2 = st.columns(2)
            with col1:
                amount_a = st.number_input(
                    f"🅰️ {self.analyzer.additive_a_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    value=1.0,
                    key="multi_amount_a_comb"
                )
            with col2:
                amount_b = st.number_input(
                    f"🅱️ {self.analyzer.additive_b_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    value=1.0,
                    key="multi_amount_b_comb"
                )
        
        return amount_a, amount_b
    
    def _process_multi_parameter_input(self, condition_type: str, amount_a: float, 
                                      amount_b: float, param_values: Dict[str, Dict[str, Any]]):
        """Process multi-parameter input"""
        try:
            # Determine condition name
            condition_name = self._get_condition_name(condition_type)
            
            # Parse and validate all parameters
            valid_params = {}
            for param_name, param_info in param_values.items():
                values_input = param_info['values_input'].strip()
                
                if not values_input:
                    st.warning(f"⚠️ No values entered for {param_name}")
                    continue
                
                # Parse values
                values = self._parse_values(values_input)
                if values:
                    valid_params[param_name] = {
                        'values': values,
                        'unit': param_info['unit']
                    }
            
            if not valid_params:
                st.error("❌ No valid parameter data entered")
                return
            
            # Add multi-parameter data point
            self.analyzer.add_multi_parameter_data(condition_name, amount_a, amount_b, valid_params)
            
            param_names = list(valid_params.keys())
            st.success(f"✅ Added {condition_type} data for {len(param_names)} parameters: {', '.join(param_names)}")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error adding data: {str(e)}")
    
    def _parse_values(self, values_input: str) -> List[float]:
        """Parse input values from string"""
        if not values_input.strip():
            return []
        
        # Handle both comma-separated and newline-separated
        if ',' in values_input:
            parts = values_input.split(',')
        else:
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
    
    def _render_multi_parameter_table(self):
        """Render table showing multi-parameter data"""
        st.subheader("📋 Multi-Parameter Data Overview")
        
        if not self.analyzer.data:
            st.info("No data points added yet")
            return
        
        # Get all parameters across all conditions
        all_params = set()
        for data in self.analyzer.data.values():
            all_params.update(data.get_parameter_names())
        
        if not all_params:
            st.info("No parameter data available")
            return
        
        # Create expandable view for each condition
        for condition_name, data in self.analyzer.data.items():
            with st.expander(f"📊 {condition_name.replace('_', ' ').title()} - {data.amount_a} + {data.amount_b} {self.analyzer.unit}"):
                
                if not data.parameters:
                    st.warning("No parameter data")
                    continue
                
                # Create table for this condition
                param_rows = []
                for param_name, param_data in data.parameters.items():
                    ci_text = f"[{param_data.ci_lower:.3f}, {param_data.ci_upper:.3f}]" if param_data.ci_lower else "N/A"
                    
                    param_rows.append({
                        'Parameter': param_data.parameter_name,
                        'Unit': param_data.unit,
                        'Values': ', '.join(f'{v:.2f}' for v in param_data.values),
                        'Mean': f"{param_data.mean:.3f}",
                        'Std Dev': f"{param_data.std:.3f}",
                        'N': param_data.n,
                        'CI (95%)': ci_text
                    })
                
                param_df = pd.DataFrame(param_rows)
                st.dataframe(param_df, use_container_width=True, hide_index=True)
                
                # Action buttons for this condition
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit {condition_name}", key=f"edit_{condition_name}"):
                        st.session_state[f'editing_multi_{condition_name}'] = True
                        st.rerun()
                
                with col2:
                    if st.button(f"🗑️ Delete {condition_name}", key=f"del_{condition_name}"):
                        del self.analyzer.data[condition_name]
                        st.success(f"✅ Deleted {condition_name}")
                        st.rerun()
        
        # Summary statistics
        self._render_parameter_summary(all_params)
    
    def _render_parameter_summary(self, all_params: set):
        """Render summary of all parameters"""
        if not all_params:
            return
        
        st.subheader("📈 Parameter Summary")
        
        # Count data points per parameter
        param_counts = {}
        for param in all_params:
            count = sum(1 for data in self.analyzer.data.values() 
                       if param in data.parameters)
            param_counts[param] = count
        
        # Display summary
        summary_data = []
        for param, count in param_counts.items():
            summary_data.append({
                'Parameter': param,
                'Data Points': count,
                'Coverage': f"{count}/{len(self.analyzer.data)} conditions"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Multi-Parameter Template"):
                template_csv = """condition_type,amount_a,amount_b,cycle_life,capacity_retention,coulombic_efficiency
Base Electrolyte,0,0,500,16.5,98.5
Additive A Only,10,0,450,12.8,97.2
Additive B Only,0,2,600,85,99.1
Combination,8,2,750,91,99.8
Combination,7,3,720,89,99.6"""
                
                st.download_button(
                    label="📋 Download CSV Template",
                    data=template_csv,
                    file_name="multi_parameter_template.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🔄 Sync Parameters"):
                # Ensure all conditions have all parameters
                st.info("Feature coming soon: Auto-sync missing parameters")
        
        with col3:
            if st.button("📊 Export Multi-Parameter Data"):
                if self.analyzer.data:
                    self._export_multi_parameter_data()
    
    def _export_multi_parameter_data(self):
        """Export multi-parameter data as CSV"""
        export_rows = []
        
        # Get all unique parameters
        all_params = set()
        for data in self.analyzer.data.values():
            all_params.update(data.get_parameter_names())
        
        for condition_name, data in self.analyzer.data.items():
            row = {
                'condition_type': condition_name.replace('_', ' ').title(),
                'amount_a': data.amount_a,
                'amount_b': data.amount_b
            }
            
            # Add parameter values
            for param in sorted(all_params):
                if param in data.parameters:
                    param_data = data.parameters[param]
                    row[f'{param}_values'] = ', '.join(map(str, param_data.values))
                    row[f'{param}_mean'] = param_data.mean
                    row[f'{param}_unit'] = param_data.unit
                else:
                    row[f'{param}_values'] = ""
                    row[f'{param}_mean'] = ""
                    row[f'{param}_unit'] = ""
            
            export_rows.append(row)
        
        export_df = pd.DataFrame(export_rows)
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Multi-Parameter CSV",
            data=csv_data,
            file_name=f"multi_parameter_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )