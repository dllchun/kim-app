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
            
            # Always show amount inputs for non-base conditions
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
                submit = st.form_submit_button("➕ Add Data Point", type="primary")
            with col2:
                if st.form_submit_button("📋 Paste from Clipboard"):
                    st.info("Paste data in the text area above")
            
            if submit:
                self._process_data_input(condition_type, amount_a, amount_b, values_input)
    
    def _get_amounts(self, condition_type: str) -> tuple:
        """Get amount inputs based on condition type"""
        amount_a = 0.0
        amount_b = 0.0
        
        if condition_type == "Base Electrolyte":
            st.info("Base electrolyte: Both amounts = 0")
            
        elif condition_type == "Additive A Only":
            st.write("**Concentration Settings:**")
            amount_a = st.number_input(
                f"{self.analyzer.additive_a_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                value=1.0,
                key="amount_a_only"
            )
            st.info(f"{self.analyzer.additive_b_name} = 0 (not present)")
            
        elif condition_type == "Additive B Only":
            st.write("**Concentration Settings:**")
            amount_b = st.number_input(
                f"{self.analyzer.additive_b_name} Amount ({self.analyzer.unit})",
                min_value=0.0,
                step=0.1,
                value=1.0,
                key="amount_b_only"
            )
            st.info(f"{self.analyzer.additive_a_name} = 0 (not present)")
            
        elif condition_type == "Combination":
            st.write("**Concentration Settings:**")
            col1, col2 = st.columns(2)
            with col1:
                amount_a = st.number_input(
                    f"{self.analyzer.additive_a_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    value=1.0,
                    key="amount_a_comb"
                )
            with col2:
                amount_b = st.number_input(
                    f"{self.analyzer.additive_b_name} ({self.analyzer.unit})",
                    min_value=0.0,
                    step=0.1,
                    value=1.0,
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
        """Render current data points table with edit/delete options"""
        st.subheader("Current Data Points")
        
        if not self.analyzer.data:
            st.info("No data points added yet")
            return
        
        # Data management tabs
        tab1, tab2 = st.tabs(["📊 View Data", "📝 Edit Data"])
        
        with tab1:
            # Create DataFrame for display
            data_list = []
            for key, data in self.analyzer.data.items():
                ci_text = f"[{data.ci_lower:.3f}, {data.ci_upper:.3f}]" if data.ci_lower else "N/A"
                data_list.append({
                    'Condition': key.replace('_', ' ').title(),
                    f'{self.analyzer.additive_a_name}': data.amount_a,
                    f'{self.analyzer.additive_b_name}': data.amount_b,
                    'Values': ', '.join(f'{v:.2f}' for v in data.values),
                    'Mean': f"{data.mean:.3f}",
                    'Std Dev': f"{data.std:.3f}",
                    'N': data.n,
                    'CI (95%)': ci_text
                })
            
            df = pd.DataFrame(data_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with tab2:
            # Edit/Delete interface
            if self.analyzer.data:
                condition_to_edit = st.selectbox(
                    "Select condition to edit/delete:",
                    list(self.analyzer.data.keys()),
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                if condition_to_edit:
                    data = self.analyzer.data[condition_to_edit]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current Data:**")
                        st.write(f"Amounts: {data.amount_a} + {data.amount_b}")
                        st.write(f"Values: {', '.join(map(str, data.values))}")
                        st.write(f"Mean: {data.mean:.3f}")
                    
                    with col2:
                        if st.button("🗑️ Delete This Condition", type="secondary"):
                            del self.analyzer.data[condition_to_edit]
                            st.success(f"✅ Deleted {condition_to_edit}")
                            st.rerun()
                        
                        if st.button("✏️ Edit Values"):
                            st.session_state[f'editing_{condition_to_edit}'] = True
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f'editing_{condition_to_edit}', False):
                        st.write("**Edit Values:**")
                        
                        new_values_input = st.text_area(
                            "New values (comma-separated or one per line):",
                            value=', '.join(map(str, data.values)),
                            key=f"edit_values_{condition_to_edit}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Save Changes", type="primary"):
                                try:
                                    new_values = self._parse_values(new_values_input)
                                    if new_values and self._validate_values(new_values):
                                        # Update data point
                                        self.analyzer.add_data_point(
                                            condition_to_edit, 
                                            data.amount_a, 
                                            data.amount_b, 
                                            new_values
                                        )
                                        st.session_state[f'editing_{condition_to_edit}'] = False
                                        st.success(f"✅ Updated {condition_to_edit}")
                                        st.rerun()
                                except ValueError as e:
                                    st.error(f"Invalid input: {str(e)}")
                        
                        with col2:
                            if st.button("❌ Cancel"):
                                st.session_state[f'editing_{condition_to_edit}'] = False
                                st.rerun()
        
        # Action buttons
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Clear All Data"):
                # Confirm deletion
                if st.session_state.get('confirm_clear', False):
                    self.analyzer.data = {}
                    st.session_state['confirm_clear'] = False
                    st.success("✅ All data cleared")
                    st.rerun()
                else:
                    st.session_state['confirm_clear'] = True
                    st.warning("Click again to confirm deletion")
        
        with col2:
            if st.button("📁 Import CSV"):
                st.session_state['show_import'] = True
                st.rerun()
        
        with col3:
            if st.button("📊 Export CSV", disabled=not self.analyzer.data):
                self._export_current_data()
        
        with col4:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Import CSV interface
        if st.session_state.get('show_import', False):
            self._render_csv_import()
        
        # Status
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
    
    def _render_csv_import(self):
        """Render CSV import interface"""
        st.subheader("📁 Import Data from CSV/Excel")
        
        uploaded_file = st.file_uploader(
            "Choose CSV/Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="File should have columns: condition_type, amount_a, amount_b, values"
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Show preview
                st.write("**File Preview:**")
                st.dataframe(df.head(), use_container_width=True)
                
                # Map columns
                st.write("**Column Mapping:**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    condition_col = st.selectbox("Condition Type", df.columns, key="condition_col")
                with col2:
                    amount_a_col = st.selectbox("Amount A", df.columns, key="amount_a_col")
                with col3:
                    amount_b_col = st.selectbox("Amount B", df.columns, key="amount_b_col") 
                with col4:
                    values_col = st.selectbox("Effect Values", df.columns, key="values_col")
                
                if st.button("📥 Import Data", type="primary"):
                    success_count = self._import_from_dataframe(
                        df, condition_col, amount_a_col, amount_b_col, values_col
                    )
                    
                    if success_count > 0:
                        st.success(f"✅ Imported {success_count} data points")
                        st.session_state['show_import'] = False
                        st.rerun()
                    else:
                        st.error("❌ No valid data points found")
                
                if st.button("❌ Cancel Import"):
                    st.session_state['show_import'] = False
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        # Template download
        st.write("**Need a template?**")
        if st.button("📥 Download CSV Template"):
            self._download_template()
    
    def _import_from_dataframe(self, df: pd.DataFrame, condition_col: str, 
                              amount_a_col: str, amount_b_col: str, values_col: str) -> int:
        """Import data from pandas DataFrame"""
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                condition = str(row[condition_col]).lower().strip()
                amount_a = float(row[amount_a_col])
                amount_b = float(row[amount_b_col])
                
                # Handle multiple values in one cell
                values_str = str(row[values_col])
                values = self._parse_values(values_str)
                
                if values and self._validate_values(values):
                    # Map condition name
                    condition_name = self._map_condition_name(condition)
                    self.analyzer.add_data_point(condition_name, amount_a, amount_b, values)
                    success_count += 1
                    
            except (ValueError, KeyError) as e:
                continue  # Skip invalid rows
        
        return success_count
    
    def _map_condition_name(self, condition: str) -> str:
        """Map user condition names to internal format"""
        condition = condition.lower()
        
        if any(word in condition for word in ['base', 'control', 'blank']):
            return 'base'
        elif any(word in condition for word in ['a only', 'additive a', 'a alone']):
            return 'additive_a'
        elif any(word in condition for word in ['b only', 'additive b', 'b alone']):
            return 'additive_b'
        else:
            # Treat as combination
            comb_count = sum(1 for k in self.analyzer.data.keys() if k.startswith('combination_'))
            return f'combination_{comb_count + 1}'
    
    def _export_current_data(self):
        """Export current data as CSV"""
        if not self.analyzer.data:
            return
        
        # Create export DataFrame
        export_data = []
        for key, data in self.analyzer.data.items():
            export_data.append({
                'condition_type': key.replace('_', ' ').title(),
                'amount_a': data.amount_a,
                'amount_b': data.amount_b,
                'values': ', '.join(map(str, data.values)),
                'mean': data.mean,
                'std': data.std,
                'n': data.n
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Current Data",
            data=csv,
            file_name=f"synergy_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def _download_template(self):
        """Download CSV template"""
        template_data = {
            'condition_type': ['Base Electrolyte', 'Additive A Only', 'Additive B Only', 'Combination'],
            'amount_a': [0, 10, 0, 8],
            'amount_b': [0, 0, 2, 2],
            'values': ['16.5', '12.8', '85', '91, 89, 92']
        }
        
        df = pd.DataFrame(template_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Template",
            data=csv,
            file_name="synergy_data_template.csv",
            mime="text/csv"
        )