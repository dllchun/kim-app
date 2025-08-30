"""
Report generation view
"""
import streamlit as st
from datetime import datetime
import json
from typing import Dict, Any

from ..models import SynergyAnalyzer
from ..config.settings import EXPORT_CONFIG


class ReportView:
    """Handle report generation and export"""
    
    def __init__(self, analyzer: SynergyAnalyzer):
        self.analyzer = analyzer
    
    def render(self):
        """Render report interface"""
        st.header("📋 Analysis Report")
        
        if not self.analyzer.results:
            st.info("📊 Run analysis first to generate report")
            return
        
        # Report options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_format = st.selectbox(
                "Report Format",
                ["Markdown", "JSON", "Summary"]
            )
        
        with col2:
            include_raw_data = st.checkbox("Include Raw Data", value=True)
        
        with col3:
            include_plots = st.checkbox("Include Plot References", value=True)
        
        # Generate report
        if report_format == "Markdown":
            report_content = self._generate_markdown_report(include_raw_data, include_plots)
            st.markdown("### Report Preview")
            st.markdown(report_content)
            
            st.download_button(
                label="📥 Download Markdown Report",
                data=report_content,
                file_name=f"synergy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        elif report_format == "JSON":
            json_content = self._generate_json_report()
            st.json(json_content)
            
            st.download_button(
                label="📥 Download JSON Report",
                data=json.dumps(json_content, indent=EXPORT_CONFIG['json_indent']),
                file_name=f"synergy_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        else:  # Summary
            summary = self._generate_summary_report()
            st.markdown(summary)
            
            st.download_button(
                label="📥 Download Summary",
                data=summary,
                file_name=f"synergy_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    def _generate_markdown_report(self, include_raw_data: bool, include_plots: bool) -> str:
        """Generate comprehensive markdown report"""
        results = self.analyzer.results
        timestamp = datetime.now().strftime(EXPORT_CONFIG['datetime_format'])
        
        report = f"""# Synergy Analysis Report

**Generated**: {timestamp}  
**Analysis Tool**: Battery Electrolyte Synergy Analyzer

## Experiment Details

- **Additive A**: {self.analyzer.additive_a_name}
- **Additive B**: {self.analyzer.additive_b_name}
- **Concentration Unit**: {self.analyzer.unit}
- **Effect Parameter**: {self.analyzer.effect_parameter}

## Summary Statistics

"""
        
        # Add summary stats
        summary_stats = results.get_summary_stats()
        report += f"""- **Total Combinations Tested**: {summary_stats['total_combinations']}
- **Synergistic Effects**: {summary_stats['synergistic']}
- **Antagonistic Effects**: {summary_stats['antagonistic']}
- **Additive Effects**: {summary_stats['additive']}
- **Statistically Significant**: {summary_stats['significant']}

## Key Findings

"""
        
        # Add combination results
        for comb_id, synergy in results.synergy_results.items():
            report += f"""### Combination: {synergy.amount_a} + {synergy.amount_b} {self.analyzer.unit}

- **Synergy Type**: {synergy.synergy_type}
- **Combination Index**: {synergy.combination_index:.3f}
- **Enhancement**: {synergy.enhancement_percent:.1f}%
- **Statistical Significance**: {'Yes (p < 0.05)' if synergy.is_significant else 'No'}
- **Observed Effect**: {synergy.observed_effect:.3f}
- **Expected Additive**: {synergy.expected_additive:.3f}

"""
        
        # Statistical results
        if results.statistical_results.get('anova'):
            anova = results.statistical_results['anova']
            report += f"""## Statistical Analysis

### ANOVA Results
- **F-statistic**: {anova['f_statistic']:.4f}
- **P-value**: {anova['p_value']:.4f}
- **Result**: {'Significant difference between groups' if anova['significant'] else 'No significant difference'}

"""
        
        # Model results
        if results.model_results:
            report += "## Model Results\n\n"
            
            if 'response_surface' in results.model_results:
                surface = results.model_results['response_surface']
                report += f"""### Response Surface Model
- **R² Score**: {surface['r_squared']:.4f}
- **RMSE**: {surface['rmse']:.4f}
- **Model Type**: Polynomial (degree {surface['degree']})

"""
        
        # Raw data section
        if include_raw_data:
            report += "## Raw Data\n\n"
            
            for key, data in results.raw_data.items():
                report += f"""### {key.replace('_', ' ').title()}
- **Composition**: {data.amount_a} + {data.amount_b} {self.analyzer.unit}
- **Values**: {', '.join(f'{v:.3f}' for v in data.values)}
- **Mean ± SD**: {data.mean:.3f} ± {data.std:.3f}
- **95% CI**: [{data.ci_lower:.3f}, {data.ci_upper:.3f}] (if available)

"""
        
        report += f"""## Methodology

This analysis used standard synergy assessment methods:

1. **Combination Index (CI)** - Compares observed effect to expected additive effect
2. **Bliss Independence** - Probabilistic model for independent action
3. **Statistical Testing** - ANOVA and t-tests for significance
4. **Effect Size** - Cohen's d for practical significance

### Interpretation Guidelines
- CI < 1: Synergistic (better than expected)
- CI = 1: Additive (as expected)  
- CI > 1: Antagonistic (worse than expected)

---
*Report generated by Battery Electrolyte Synergy Analyzer*
"""
        
        return report
    
    def _generate_json_report(self) -> Dict[str, Any]:
        """Generate structured JSON report"""
        return self.analyzer.results.to_dict()
    
    def _generate_summary_report(self) -> str:
        """Generate concise summary report"""
        results = self.analyzer.results
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        summary_stats = results.get_summary_stats()
        
        report = f"""SYNERGY ANALYSIS SUMMARY
Generated: {timestamp}

Experiment: {self.analyzer.additive_a_name} + {self.analyzer.additive_b_name}
Effect: {self.analyzer.effect_parameter}

RESULTS OVERVIEW:
- Total combinations: {summary_stats['total_combinations']}
- Synergistic: {summary_stats['synergistic']}
- Antagonistic: {summary_stats['antagonistic']}
- Additive: {summary_stats['additive']}
- Significant: {summary_stats['significant']}

COMBINATION DETAILS:
"""
        
        for synergy in results.synergy_results.values():
            significance = "***" if synergy.is_significant else ""
            report += f"• {synergy.amount_a}+{synergy.amount_b}: CI={synergy.combination_index:.3f} "
            report += f"({synergy.synergy_type.split('(')[0].strip()}) {significance}\n"
        
        if results.statistical_results.get('anova'):
            anova = results.statistical_results['anova']
            report += f"\nANOVA: F={anova['f_statistic']:.3f}, p={anova['p_value']:.4f}"
        
        return report