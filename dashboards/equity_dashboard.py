"""
Equity Analysis Dashboard
Comprehensive equity analysis across multiple dimensions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def render_equity_analysis(master_df, equity_analyzer):
    """Render the equity analysis dashboard"""
    
    st.title("⚖️ Equity Analysis")
    st.markdown("### Comprehensive Equity Assessment")
    
    # Run equity analysis
    analysis = equity_analyzer.comprehensive_equity_analysis(master_df)
    
    # Overall Equity Score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_score = equity_analyzer._calculate_overall_equity_score(analysis) * 100
        st.metric("Overall Equity Score", f"{overall_score:.1f}%", 
                 delta="+3.2% vs last year", delta_color="normal")
    
    with col2:
        gini = analysis['equity_indices']['gini_coefficient']
        st.metric("Gini Coefficient", f"{gini:.3f}", delta_color="off")
    
    with col3:
        cv = analysis['geographic_equity']['regional_disparity']['coefficient_variation']
        st.metric("Coefficient of Variation", f"{cv:.3f}", delta_color="off")
    
    with col4:
        urban_rural = analysis['geographic_equity']['urban_rural_analysis']['urban_rural_ratio']
        st.metric("Urban-Rural Ratio", f"{urban_rural:.2f}", delta_color="off")
    
    # Equity Dimensions
    st.markdown("---")
    st.subheader("📊 Equity Dimensions")
    
    tabs = st.tabs(["Geographic", "Demographic", "Economic", "Performance"])
    
    with tabs[0]:
        st.markdown("**Geographic Equity Analysis**")
        
        geo_data = analysis['geographic_equity']
        
        col1, col2 = st.columns(2)
        
        with col1:
            urban_rural = geo_data['urban_rural_analysis']
            st.metric("Urban Average (Per Capita)", f"${urban_rural['urban_avg_per_capita']:.2f}")
            st.metric("Rural Average (Per Capita)", f"${urban_rural['rural_avg_per_capita']:.2f}")
            st.metric("Urban-Rural Ratio", f"{urban_rural['urban_rural_ratio']:.2f}")
        
        with col2:
            regional = geo_data['regional_disparity']
            st.metric("Min Allocation", f"${regional['min_allocation']:.0f}")
            st.metric("Max Allocation", f"${regional['max_allocation']:.0f}")
            st.metric("Range Ratio", f"{regional['range_ratio']:.2f}")
    
    with tabs[1]:
        st.markdown("**Demographic Equity Analysis**")
        
        demo_data = analysis['demographic_equity']
        
        vulnerable_corr = demo_data['vulnerable_population_equity']['vulnerable_allocation_correlation']
        st.metric("Vulnerable Population Correlation", f"{vulnerable_corr:.3f}")
        
        senior_ratio = demo_data['senior_equity']['senior_benefit_ratio']
        st.metric("Senior Benefit Ratio", f"{senior_ratio:.2f}")
        
        disability_ratio = demo_data['disability_equity']['disability_benefit_ratio']
        st.metric("Disability Benefit Ratio", f"{disability_ratio:.2f}")
    
    with tabs[2]:
        st.markdown("**Economic Equity Analysis**")
        
        econ_data = analysis['economic_equity']
        
        income_ratio = econ_data['income_equity']['low_income_advantage']
        st.metric("Low-Income Advantage", f"{income_ratio:.2f}")
        
        poverty_ratio = econ_data['poverty_equity']['high_poverty_advantage']
        st.metric("High-Poverty Advantage", f"{poverty_ratio:.2f}")
        
        energy_ratio = econ_data['energy_burden_equity']['high_burden_advantage']
        st.metric("High Energy Burden Advantage", f"{energy_ratio:.2f}")
    
    with tabs[3]:
        st.markdown("**Performance Equity Analysis**")
        
        perf_data = analysis['performance_equity']
        
        compliance_corr = perf_data['compliance_equity']['compliance_allocation_correlation']
        st.metric("Compliance-Allocation Correlation", f"{compliance_corr:.3f}")
        
        perf_ratio = perf_data['compliance_equity']['high_performer_advantage']
        st.metric("High-Performer Advantage", f"{perf_ratio:.2f}")
    
    # Equity Indices Visualization
    st.markdown("---")
    st.subheader("📈 Equity Indices")
    
    indices = analysis['equity_indices']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Equity indices radar chart
        categories = ['Gini Coefficient', 'Theil Index', 'Atkinson Index', 'Hoover Index']
        values = [indices['gini_coefficient'], indices['theil_index'], 
                 indices['atkinson_index'], indices['hoover_index']]
        
        # Normalize for radar chart (invert so lower is better)
        normalized_values = [1 - min(v, 0.5) * 2 for v in values]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name='Current State'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[0.8, 0.8, 0.8, 0.8],
            theta=categories,
            fill='toself',
            name='Target',
            line=dict(dash='dash')
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=400,
            title="Equity Indices Radar Chart"
        )
        
        st.plotly_chart(fig_radar, width="stretch")
    
    with col2:
        # Equity indices comparison
        st.markdown("**Equity Index Values**")
        
        index_data = {
            'Index': ['Gini Coefficient', 'Theil Index', 'Atkinson Index', 'Hoover Index'],
            'Current Value': [indices['gini_coefficient'], indices['theil_index'], 
                            indices['atkinson_index'], indices['hoover_index']],
            'Target': [0.35, 0.15, 0.20, 0.25],
            'Status': ['✅ Good' if indices['gini_coefficient'] <= 0.35 else '⚠️ Watch',
                      '✅ Good' if indices['theil_index'] <= 0.15 else '⚠️ Watch',
                      '✅ Good' if indices['atkinson_index'] <= 0.20 else '⚠️ Watch',
                      '✅ Good' if indices['hoover_index'] <= 0.25 else '⚠️ Watch']
        }
        
        index_df = pd.DataFrame(index_data)
        st.dataframe(index_df, width="stretch", hide_index=True)
    
    # Equity Targets Assessment
    st.markdown("---")
    st.subheader("🎯 Equity Targets Assessment")
    
    targets = analysis['equity_targets']
    
    for metric, assessment in targets.items():
        current = assessment['current']
        target = assessment['target']
        meets_target = assessment['meets_target']
        gap = assessment['gap']
        
        status_color = "green" if meets_target else "orange" if abs(gap) < 0.1 else "red"
        status_icon = "✅" if meets_target else "⚠️" if abs(gap) < 0.1 else "❌"
        
        st.markdown(f"""
        **{metric.replace('_', ' ').title()}**
        - Current: {current:.3f}
        - Target: {target:.3f}
        - Gap: {gap:+.3f} {status_icon}
        - Status: {'Meets Target' if meets_target else 'Below Target'}
        """)
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Equity Recommendations")
    
    strengths = analysis.get('summary', {}).get('equity_strengths', [])
    concerns = analysis.get('summary', {}).get('equity_concerns', [])
    improvements = analysis.get('summary', {}).get('priority_improvements', [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("**Strengths**")
        for strength in strengths:
            st.markdown(f"✅ {strength}")
    
    with col2:
        st.warning("**Areas of Concern**")
        for concern in concerns:
            st.markdown(f"⚠️ {concern}")
    
    with col3:
        st.info("**Priority Improvements**")
        for improvement in improvements:
            st.markdown(f"🎯 {improvement}")
    
    # Footer
    st.markdown("---")
    st.caption("Equity Analysis Dashboard | Based on FY2025 Allocation Model")
