"""
Visualization view for charts and plots
"""
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Optional

from ..models import SynergyAnalyzer
from ..config.settings import PLOT_CONFIG


class VisualizationView:
    """Handle data visualizations"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
        self._setup_plot_style()
    
    def _setup_plot_style(self):
        """Setup matplotlib style"""
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def render(self):
        """Render visualization interface"""
        st.header("📉 Visualizations")
        
        if not self.analyzer.results:
            st.info("📊 Run analysis first to generate visualizations")
            return
        
        # Visualization tabs
        tabs = st.tabs(["📊 Effects Comparison", "🔄 Synergy Analysis", 
                        "🗺️ Response Surface", "📈 Dose-Response"])
        
        with tabs[0]:
            self._render_effects_comparison()
        
        with tabs[1]:
            self._render_synergy_analysis()
        
        with tabs[2]:
            self._render_response_surface()
        
        with tabs[3]:
            self._render_dose_response()
    
    def _render_effects_comparison(self):
        """Render effects comparison bar chart"""
        st.subheader("Effects Comparison")
        
        fig = self._create_effects_plot()
        st.pyplot(fig)
        
        # Download button
        self._add_download_button(fig, "effects_comparison.png")
    
    def _create_effects_plot(self) -> plt.Figure:
        """Create effects comparison plot"""
        fig, ax = plt.subplots(figsize=PLOT_CONFIG['figure_size'])
        
        conditions = []
        effects = []
        errors = []
        colors = []
        
        # Prepare data
        for key, data in self.analyzer.data.items():
            conditions.append(self._format_condition_name(key))
            effects.append(data.mean)
            errors.append(data.std)
            colors.append(self._get_color_for_condition(key))
        
        # Create bar plot
        bars = ax.bar(conditions, effects, yerr=errors, capsize=5, 
                      color=colors, alpha=0.7, edgecolor='black', linewidth=1)
        
        # Customize plot
        ax.set_ylabel(self.analyzer.effect_parameter, fontsize=12)
        ax.set_title('Effects Comparison Across Conditions', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-labels if needed
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, effects):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def _render_synergy_analysis(self):
        """Render synergy analysis plots"""
        st.subheader("Synergy Analysis")
        
        if not self.analyzer.results.synergy_results:
            st.warning("No combination data available")
            return
        
        fig = self._create_synergy_plot()
        st.pyplot(fig)
        
        self._add_download_button(fig, "synergy_analysis.png")
    
    def _create_synergy_plot(self) -> plt.Figure:
        """Create synergy comparison plot"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Prepare data
        comb_names = []
        observed = []
        expected = []
        ci_values = []
        
        for synergy in self.analyzer.results.synergy_results.values():
            comb_names.append(f"{synergy.amount_a}+{synergy.amount_b}")
            observed.append(synergy.observed_effect)
            expected.append(synergy.expected_additive)
            ci_values.append(synergy.combination_index if synergy.combination_index != float('inf') else 2.5)
        
        x = np.arange(len(comb_names))
        width = 0.35
        
        # Plot 1: Observed vs Expected
        bars1 = ax1.bar(x - width/2, observed, width, label='Observed', 
                       color=PLOT_CONFIG['color_palette']['combination'], alpha=0.7)
        bars2 = ax1.bar(x + width/2, expected, width, label='Expected', 
                       color=PLOT_CONFIG['color_palette']['additive'], alpha=0.7)
        
        ax1.set_xlabel('Combination', fontsize=12)
        ax1.set_ylabel(self.analyzer.effect_parameter, fontsize=12)
        ax1.set_title('Observed vs Expected Effects', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(comb_names, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Combination Index
        bars3 = ax2.bar(x, ci_values, color=[self._get_ci_color(ci) for ci in ci_values], 
                       alpha=0.7, edgecolor='black', linewidth=1)
        
        # Add reference line at CI = 1
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Additive (CI=1)')
        
        ax2.set_xlabel('Combination', fontsize=12)
        ax2.set_ylabel('Combination Index', fontsize=12)
        ax2.set_title('Synergy Classification', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(comb_names, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Add CI value labels
        for bar, ci in zip(bars3, ci_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{ci:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def _render_response_surface(self):
        """Render response surface plot"""
        st.subheader("Response Surface Model")
        
        if 'response_surface' not in self.analyzer.results.model_results:
            st.info("Add more data points (5+) to generate response surface")
            return
        
        fig = self._create_response_surface_plot()
        if fig:
            st.pyplot(fig)
            self._add_download_button(fig, "response_surface.png")
    
    def _create_response_surface_plot(self) -> Optional[plt.Figure]:
        """Create 3D response surface plot"""
        try:
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Get data points
            X_data = []
            Y_data = []
            Z_data = []
            
            for data in self.analyzer.data.values():
                X_data.append(data.amount_a)
                Y_data.append(data.amount_b)
                Z_data.append(data.mean)
            
            # Create mesh grid
            x_range = np.linspace(min(X_data), max(X_data), 20)
            y_range = np.linspace(min(Y_data), max(Y_data), 20)
            X_mesh, Y_mesh = np.meshgrid(x_range, y_range)
            
            # Predict surface (simplified - would need actual model prediction)
            Z_mesh = np.zeros_like(X_mesh)
            for i in range(X_mesh.shape[0]):
                for j in range(X_mesh.shape[1]):
                    # Simple interpolation for visualization
                    Z_mesh[i, j] = np.mean(Z_data)  # Placeholder
            
            # Plot surface
            surf = ax.plot_surface(X_mesh, Y_mesh, Z_mesh, cmap='viridis', 
                                  alpha=0.6, edgecolor='none')
            
            # Plot data points
            ax.scatter(X_data, Y_data, Z_data, c='red', s=50, alpha=1, 
                      edgecolors='black', linewidth=2, label='Data Points')
            
            # Labels and title
            ax.set_xlabel(f'{self.analyzer.additive_a_name} ({self.analyzer.unit})', fontsize=12)
            ax.set_ylabel(f'{self.analyzer.additive_b_name} ({self.analyzer.unit})', fontsize=12)
            ax.set_zlabel(self.analyzer.effect_parameter, fontsize=12)
            ax.set_title('Response Surface Model', fontsize=14, fontweight='bold')
            
            # Color bar
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
            
            ax.legend()
            plt.tight_layout()
            return fig
            
        except ImportError:
            st.error("3D plotting requires matplotlib toolkit")
            return None
    
    def _render_dose_response(self):
        """Render dose-response curves"""
        st.subheader("Dose-Response Curves")
        
        if 'dose_response' not in self.analyzer.results.model_results:
            st.info("Add multiple concentrations of single additives to generate dose-response curves")
            return
        
        fig = self._create_dose_response_plot()
        if fig:
            st.pyplot(fig)
            self._add_download_button(fig, "dose_response.png")
    
    def _create_dose_response_plot(self) -> Optional[plt.Figure]:
        """Create dose-response curves"""
        dr_data = self.analyzer.results.model_results.get('dose_response', {})
        
        if not dr_data:
            return None
        
        fig, axes = plt.subplots(1, len(dr_data), figsize=(6*len(dr_data), 5))
        
        if len(dr_data) == 1:
            axes = [axes]
        
        for idx, (additive, params) in enumerate(dr_data.items()):
            ax = axes[idx]
            
            # Get actual data points
            doses = []
            effects = []
            
            for data in self.analyzer.data.values():
                if additive == 'additive_a' and data.amount_b == 0 and data.amount_a > 0:
                    doses.append(data.amount_a)
                    effects.append(data.mean)
                elif additive == 'additive_b' and data.amount_a == 0 and data.amount_b > 0:
                    doses.append(data.amount_b)
                    effects.append(data.mean)
            
            # Plot data points
            ax.scatter(doses, effects, s=50, alpha=0.7, label='Data')
            
            # Plot fitted curve (if parameters available)
            if doses:
                x_fit = np.linspace(0, max(doses)*1.2, 100)
                # Simplified Hill equation visualization
                y_fit = params['bottom'] + (params['top'] - params['bottom']) / \
                       (1 + (x_fit / params['ic50']) ** params['hill_slope'])
                ax.plot(x_fit, y_fit, 'r-', alpha=0.7, label='Fitted')
            
            # Customize
            name = self.analyzer.additive_a_name if additive == 'additive_a' else self.analyzer.additive_b_name
            ax.set_xlabel(f'{name} ({self.analyzer.unit})', fontsize=12)
            ax.set_ylabel(self.analyzer.effect_parameter, fontsize=12)
            ax.set_title(f'{name} Dose-Response', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add R² annotation
            ax.text(0.05, 0.95, f"R² = {params['r_squared']:.3f}", 
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top')
        
        plt.tight_layout()
        return fig
    
    def _format_condition_name(self, key: str) -> str:
        """Format condition name for display"""
        if key == 'base':
            return 'Base'
        elif key == 'additive_a':
            return self.analyzer.additive_a_name
        elif key == 'additive_b':
            return self.analyzer.additive_b_name
        elif key.startswith('combination_'):
            data = self.analyzer.data[key]
            return f"{data.amount_a}+{data.amount_b}"
        return key.replace('_', ' ').title()
    
    def _get_color_for_condition(self, key: str) -> str:
        """Get color for condition type"""
        colors = PLOT_CONFIG['color_palette']
        
        if key == 'base':
            return colors['base']
        elif key == 'additive_a':
            return colors['additive_a']
        elif key == 'additive_b':
            return colors['additive_b']
        else:
            return colors['combination']
    
    def _get_ci_color(self, ci: float) -> str:
        """Get color based on CI value"""
        colors = PLOT_CONFIG['color_palette']
        
        if ci < 0.9:
            return colors['synergy']
        elif ci > 1.1:
            return colors['antagonism']
        else:
            return colors['additive']
    
    def _add_download_button(self, fig: plt.Figure, filename: str):
        """Add download button for figure"""
        import io
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=PLOT_CONFIG['dpi'], bbox_inches='tight')
        buf.seek(0)
        
        st.download_button(
            label=f"📥 Download {filename}",
            data=buf,
            file_name=filename,
            mime="image/png"
        )