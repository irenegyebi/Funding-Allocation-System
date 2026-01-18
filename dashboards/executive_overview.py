"""
Executive Overview Dashboard
High-level KPIs and strategic insights for leadership
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

def render_executive_dashboard(master_df, compliance_df, scenario):
    """Render the executive overview dashboard"""
    
    st.title("🏠 Executive Command Center")
    st.markdown("### Strategic Overview - Energy Assistance Program")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_funding = 6800000
        total_households = master_df['households_served'].sum()
        st.metric(
            "Total FY2025 Funding",
            f"${total_funding:,.0f}",
            delta="+$200K vs FY2024",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Households Served",
            f"{total_households:,}",
            delta="+1,234 vs last year",
            delta_color="normal"
        )
    
    with col3:
        avg_compliance = compliance_df['overall_score'].mean() * 100
        st.metric(
            "Compliance Rate",
            f"{avg_compliance:.1f}%",
            delta="+2.1% vs last year",
            delta_color="normal"
        )
    
    with col4:
        avg_benefit = master_df['avg_benefit'].mean()
        st.metric(
            "Average Benefit",
            f"${avg_benefit:.0f}",
            delta="+$28 vs last year",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Regional Allocation Distribution")
        
        # Create allocation chart
        fig_allocation = px.bar(
            master_df.sort_values('final_allocation', ascending=True),
            x='final_allocation',
            y='region_name',
            orientation='h',
            title="Allocation by Region",
            labels={'final_allocation': 'Allocation Amount ($)', 'region_name': 'Region'}
        )
        
        fig_allocation.update_layout(
            height=400,
            showlegend=False,
            margin=dict(l=150, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig_allocation, width="stretch")
    
    with col2:
        st.subheader("🎯 Performance vs Need Analysis")
        
        # Create scatter plot
        fig_scatter = px.scatter(
            master_df,
            x='energy_burden_pct',
            y='final_allocation',
            size='households_served',
            color='compliance_score',
            hover_data=['region_name'],
            title="Energy Burden vs Allocation",
            labels={
                'energy_burden_pct': 'Energy Burden (%)',
                'final_allocation': 'Allocation ($)',
                'compliance_score': 'Compliance Score'
            }
        )
        
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, width="stretch")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Compliance Trends")
        
        # Monthly compliance trend (simulated)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        compliance_trend = [88.2, 89.1, 90.3, 91.2, 90.8, 91.5, 92.1, 91.9, 92.4, 92.8, 92.6, 92.4]
        
        fig_compliance = px.line(
            x=months,
            y=compliance_trend,
            title="Monthly Compliance Rate Trend",
            labels={'x': 'Month', 'y': 'Compliance Rate (%)'}
        )
        
        fig_compliance.add_hline(
            y=90, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Target (90%)"
        )
        
        fig_compliance.update_layout(height=350)
        st.plotly_chart(fig_compliance, width="stretch")
    
    with col2:
        st.subheader("⚖️ Equity Metrics")
        
        # Equity indicators
        equity_data = {
            'Metric': ['Coefficient of Variation', 'Gini Coefficient', 'Urban-Rural Ratio'],
            'Current': [0.28, 0.32, 1.4],
            'Target': [0.30, 0.35, 2.0],
            'Status': ['✅ On Track', '✅ On Track', '✅ On Track']
        }
        
        equity_df = pd.DataFrame(equity_data)
        
        st.dataframe(
            equity_df,
            width="stretch",
            hide_index=True
        )
        
        # Equity score gauge
        equity_score = 88.5
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=equity_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Equity Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#1B2951"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_gauge.update_layout(height=250)
        st.plotly_chart(fig_gauge, width="stretch")
    
    # Key Insights Section
    st.markdown("---")
    st.subheader("🔍 Key Strategic Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📈 Performance Highlights**
        - 92.4% compliance rate exceeds 90% target
        - Average benefit increased by $28
        - 16,847 households served (+8% growth)
        """)
    
    with col2:
        st.warning("""
        **⚠️ Areas of Concern**
        - 3 regions below minimum allocation floor
        - Energy burden increasing in rural areas
        - Compliance variance across regions
        """)
    
    with col3:
        st.success("""
        **🎯 Opportunities**
        - Performance bonus pool available
        - Emergency funding for crisis response
        - Technology improvements for efficiency
        """)
    
    # Scenario Impact Summary
    st.markdown("---")
    st.subheader(f"📋 {scenario} Scenario Impact")
    
    scenario_impacts = {
        'Base Case': {'funding_change': 0, 'households_impact': 0, 'description': 'Standard allocation model'},
        'Optimistic': {'funding_change': 8, 'households_impact': 12, 'description': 'Economic growth scenario with increased performance focus'},
        'Pessimistic': {'funding_change': -15, 'households_impact': -8, 'description': 'Economic downturn with increased need focus'},
        'Equity-Focused': {'funding_change': -3, 'households_impact': 15, 'description': 'Prioritizes vulnerable populations'},
        'Performance-Driven': {'funding_change': 12, 'households_impact': 5, 'description': 'Rewards high-performing regions'}
    }
    
    impact = scenario_impacts.get(scenario, scenario_impacts['Base Case'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Funding Change", f"{impact['funding_change']:+d}%", 
                 delta_color="normal" if impact['funding_change'] >= 0 else "inverse")
    
    with col2:
        st.metric("Households Impact", f"{impact['households_impact']:+d}%",
                 delta_color="normal" if impact['households_impact'] >= 0 else "inverse")
    
    with col3:
        st.caption(impact['description'])
    
    # Footer
    st.markdown("---")
    st.caption("Executive Dashboard | Last Updated: December 2024 | Next Review: January 2025")
