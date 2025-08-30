"""
Analysis view for displaying results
"""
import streamlit as st
import pandas as pd
from typing import Optional

from ..models import SynergyAnalyzer, AnalysisResults
from ..config.settings import ANALYSIS_CONFIG


class AnalysisView:
    """Handle analysis results display"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
    
    def render(self):
        """Render analysis interface"""
        st.header("📈 Statistical Analysis")
        
        # Check if data is ready
        if not self._check_data_ready():
            st.warning("⚠️ Need at least 4 data points (base, A only, B only, and one combination)")
            return
        
        # Analysis controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔬 Run Analysis", type="primary", width='stretch'):
                self._run_analysis()
        
        with col2:
            if st.button("📊 Export Results", width='stretch', 
                        disabled=self.analyzer.results is None):
                self._export_results()
        
        with col3:
            if st.button("🔄 Reset Analysis", width='stretch',
                        disabled=self.analyzer.results is None):
                self.analyzer.results = None
                st.rerun()
        
        # Display results if available
        if self.analyzer.results:
            self._display_results(self.analyzer.results)
    
    def _check_data_ready(self) -> bool:
        """Check if sufficient data for analysis"""
        required = ['base', 'additive_a', 'additive_b']
        has_required = all(key in self.analyzer.data for key in required)
        
        has_combination = any(key.startswith('combination_') 
                             for key in self.analyzer.data.keys())
        
        return has_required and has_combination
    
    def _run_analysis(self):
        """Execute analysis"""
        with st.spinner("Analyzing data..."):
            try:
                results = self.analyzer.analyze()
                st.success("✅ Analysis complete!")
                st.balloons()
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
    
    def _display_results(self, results: AnalysisResults):
        """Display analysis results"""
        # Summary statistics
        self._display_summary(results)
        
        # Synergy results tabs
        tabs = st.tabs(["🔄 Synergy Results", "📊 Statistical Tests", "📈 Models", "📋 Summary"])
        
        with tabs[0]:
            self._display_synergy_results(results)
        
        with tabs[1]:
            self._display_statistical_tests(results)
        
        with tabs[2]:
            self._display_model_results(results)
        
        with tabs[3]:
            self._display_summary_table(results)
    
    def _display_summary(self, results: AnalysisResults):
        """Display summary metrics"""
        st.subheader("📊 Summary Metrics")
        
        summary = results.get_summary_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Combinations", summary['total_combinations'])
        
        with col2:
            st.metric("Synergistic", summary['synergistic'], 
                     delta=f"{summary['synergistic']}/{summary['total_combinations']}")
        
        with col3:
            st.metric("Antagonistic", summary['antagonistic'],
                     delta=f"{summary['antagonistic']}/{summary['total_combinations']}")
        
        with col4:
            st.metric("Additive", summary['additive'])
        
        with col5:
            st.metric("Significant", summary['significant'],
                     help="p < 0.05")
    
    def _display_synergy_results(self, results: AnalysisResults):
        """Display individual synergy results"""
        st.subheader("Combination Analysis")
        
        for comb_id, synergy in results.synergy_results.items():
            with st.expander(
                f"**{synergy.combination_id}**: "
                f"{synergy.amount_a} + {synergy.amount_b} {self.analyzer.unit}"
            ):
                # Create three columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Observed Effect", f"{synergy.observed_effect:.3f}")
                    st.metric("Expected (Additive)", f"{synergy.expected_additive:.3f}")
                    st.metric("Expected (Bliss)", f"{synergy.expected_bliss:.3f}")
                
                with col2:
                    ci_display = f"{synergy.combination_index:.3f}" if synergy.combination_index != float('inf') else "∞"
                    st.metric("Combination Index", ci_display,
                             help="CI < 1: Synergy, CI > 1: Antagonism")
                    st.metric("Enhancement", f"{synergy.enhancement:.3f}")
                    st.metric("Enhancement %", f"{synergy.enhancement_percent:.1f}%")
                
                with col3:
                    # Synergy classification with color
                    if "Synergy" in synergy.synergy_type:
                        st.success(f"**{synergy.synergy_type}**")
                    elif "Antagonism" in synergy.synergy_type:
                        st.error(f"**{synergy.synergy_type}**")
                    else:
                        st.info(f"**{synergy.synergy_type}**")
                    
                    if synergy.p_value is not None:
                        st.metric("P-value", f"{synergy.p_value:.4f}",
                                 help="Statistical significance")
                    
                    if synergy.cohens_d is not None:
                        st.metric("Cohen's d", f"{synergy.cohens_d:.3f}",
                                 help="Effect size")
                
                # Confidence interval
                if synergy.confidence_interval[0] is not None:
                    st.write(f"**95% CI**: [{synergy.confidence_interval[0]:.3f}, "
                            f"{synergy.confidence_interval[1]:.3f}]")
    
    def _display_statistical_tests(self, results: AnalysisResults):
        """Display statistical test results"""
        st.subheader("Statistical Tests")
        
        stats = results.statistical_results
        
        # ANOVA results
        if 'anova' in stats:
            st.write("#### ANOVA Results")
            anova = stats['anova']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("F-statistic", f"{anova['f_statistic']:.4f}")
            with col2:
                st.metric("P-value", f"{anova['p_value']:.4f}")
            with col3:
                if anova['significant']:
                    st.success("✅ Significant")
                else:
                    st.info("❌ Not Significant")
            
            st.write(f"**Groups tested**: {', '.join(anova['groups_tested'])}")
            
            # Tukey HSD if available
            if 'tukey' in stats:
                st.write("#### Post-hoc Analysis (Tukey HSD)")
                if 'error' in stats['tukey']:
                    st.warning(stats['tukey']['error'])
                else:
                    st.write("Pairwise p-values available in detailed export")
        
        # Normality tests
        if 'normality' in stats:
            st.write("#### Normality Tests (Shapiro-Wilk)")
            
            norm_data = []
            for group, result in stats['normality'].items():
                norm_data.append({
                    'Group': group.replace('_', ' ').title(),
                    'Statistic': f"{result['statistic']:.4f}",
                    'P-value': f"{result['p_value']:.4f}",
                    'Normal': '✅' if result['normal'] else '❌'
                })
            
            df = pd.DataFrame(norm_data)
            st.dataframe(df, width='stretch', hide_index=True)
    
    def _display_model_results(self, results: AnalysisResults):
        """Display model fitting results"""
        st.subheader("Model Fitting Results")
        
        models = results.model_results
        
        if not models:
            st.info("No models fitted. Try adding more data points for advanced modeling.")
            return
        
        # Response surface model
        if 'response_surface' in models:
            st.write("#### Response Surface Model")
            surface = models['response_surface']
            
            if 'error' in surface:
                st.error(f"Model fitting failed: {surface['error']}")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Score", f"{surface['r_squared']:.4f}",
                             help="Model fit quality (1.0 = perfect)")
                with col2:
                    st.metric("RMSE", f"{surface['rmse']:.4f}",
                             help="Root Mean Square Error")
                with col3:
                    st.metric("Polynomial Degree", surface['degree'])
                
                # Show equation
                with st.expander("Model Equation"):
                    st.write("**Features**:", ', '.join(surface['feature_names']))
                    st.write("**Intercept**:", f"{surface['intercept']:.4f}")
                    st.write("**Coefficients**:")
                    for feat, coef in zip(surface['feature_names'], surface['coefficients']):
                        st.write(f"  - {feat}: {coef:.4f}")
        
        # Dose-response curves
        if 'dose_response' in models:
            st.write("#### Dose-Response Curves")
            dr = models['dose_response']
            
            for additive, params in dr.items():
                with st.expander(f"{additive.replace('_', ' ').title()} Hill Equation"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Top", f"{params['top']:.3f}")
                        st.metric("Bottom", f"{params['bottom']:.3f}")
                    with col2:
                        st.metric("IC50", f"{params['ic50']:.3f}")
                        st.metric("Hill Slope", f"{params['hill_slope']:.3f}")
                    
                    st.metric("R² Score", f"{params['r_squared']:.4f}")
    
    def _display_summary_table(self, results: AnalysisResults):
        """Display summary table of all results"""
        st.subheader("Summary Table")
        
        # Create summary DataFrame
        summary_data = []
        
        for comb_id, synergy in results.synergy_results.items():
            summary_data.append({
                'Combination': f"{synergy.amount_a}+{synergy.amount_b}",
                'Observed': f"{synergy.observed_effect:.3f}",
                'Expected': f"{synergy.expected_additive:.3f}",
                'CI': f"{synergy.combination_index:.3f}" if synergy.combination_index != float('inf') else "∞",
                'Enhancement %': f"{synergy.enhancement_percent:.1f}",
                'P-value': f"{synergy.p_value:.4f}" if synergy.p_value else "N/A",
                'Type': synergy.synergy_type.replace(" (NS)", ""),
                'Significant': '✅' if synergy.is_significant else '❌'
            })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, width='stretch', hide_index=True)
        
        # Download as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="synergy_summary.csv",
            mime="text/csv"
        )
    
    def _export_results(self):
        """Export results to various formats"""
        # This would be implemented with file export functionality
        st.info("Export functionality available in sidebar")