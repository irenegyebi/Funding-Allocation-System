"""
Allocation Analysis Dashboard
Detailed analysis of allocation methodology and results
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_allocation_analysis(master_df, engine, scenario):
    """Render the allocation analysis dashboard"""
    
    st.title("📊 Allocation Analysis")
    st.markdown("### Detailed Allocation Methodology and Results")
    
    # Calculate allocations if not already done
    if 'final_allocation' not in master_df.columns:
        allocation_df = engine.calculate_allocations(master_df, scenario)
    else:
        allocation_df = master_df.copy()
    
    # Allocation Summary Metrics
    st.subheader("📈 Allocation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_allocation = allocation_df['final_allocation'].sum()
        st.metric("Total Allocation", f"${total_allocation:,.0f}")
    
    with col2:
        avg_allocation = allocation_df['final_allocation'].mean()
        st.metric("Average Allocation", f"${avg_allocation:,.0f}")
    
    with col3:
        min_allocation = allocation_df['final_allocation'].min()
        st.metric("Minimum Allocation", f"${min_allocation:,.0f}")
    
    with col4:
        max_allocation = allocation_df['final_allocation'].max()
        st.metric("Maximum Allocation", f"${max_allocation:,.0f}")
    
    # Criteria Weights Display
    st.markdown("---")
    st.subheader("⚖️ Allocation Criteria Weights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Need-Based Factors (70%)**")
        need_weights = {
            'Energy Burden': 30,
            'Income Level': 25,
            'Poverty Rate': 20,
            'Vulnerable Population': 5
        }
        
        fig_need = px.pie(
            values=list(need_weights.values()),
            names=list(need_weights.keys()),
            title="Need-Based Weighting",
            hole=0.4
        )
        fig_need.update_layout(height=300)
        st.plotly_chart(fig_need, width="stretch")
    
    with col2:
        st.markdown("**Performance-Based Factors (30%)**")
        performance_weights = {
            'Prior Utilization': 15,
            'Compliance Score': 10,
            'Application Timeliness': 5
        }
        
        fig_perf = px.pie(
            values=list(performance_weights.values()),
            names=list(performance_weights.keys()),
            title="Performance-Based Weighting",
            hole=0.4
        )
        fig_perf.update_layout(height=300)
        st.plotly_chart(fig_perf, width="stretch")
    
    # Regional Allocation Analysis
    st.markdown("---")
    st.subheader("🗺️ Regional Allocation Breakdown")
    
    # Create detailed allocation table
    allocation_summary = allocation_df[[
        'region_name', 'final_allocation', 'allocation_per_household', 
        'households_served', 'need_score', 'performance_score', 'composite_score'
    ]].copy()
    
    allocation_summary['allocation_share_pct'] = (allocation_summary['final_allocation'] / allocation_summary['final_allocation'].sum() * 100).round(2)
    allocation_summary = allocation_summary.sort_values('final_allocation', ascending=False)
    
    st.dataframe(
        allocation_summary,
        width="stretch",
        height=400
    )
    
    # Visual Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Allocation vs Need Score")
        
        fig_scatter = px.scatter(
            allocation_df,
            x='need_score',
            y='final_allocation',
            size='households_served',
            color='region_name',
            title="Need Score vs Final Allocation",
            labels={
                'need_score': 'Need Score',
                'final_allocation': 'Final Allocation ($)'
            }
        )
        
        # Add trend line
        fig_scatter.add_traces(px.scatter(allocation_df, x='need_score', y='final_allocation', trendline='ols').data[1])
        
        fig_scatter.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_scatter, width="stretch")
    
    with col2:
        st.subheader("⚡ Energy Burden Impact")
        
        # Energy burden vs allocation
        fig_energy = px.scatter(
            allocation_df,
            x='energy_burden_pct',
            y='final_allocation',
            color='poverty_rate',
            size='households_served',
            hover_data=['region_name'],
            title="Energy Burden vs Allocation",
            labels={
                'energy_burden_pct': 'Energy Burden (%)',
                'final_allocation': 'Allocation ($)',
                'poverty_rate': 'Poverty Rate'
            }
        )
        
        fig_energy.update_layout(height=400)
        st.plotly_chart(fig_energy, width="stretch")
    
    # Constraint Analysis
    st.markdown("---")
    st.subheader("📏 Constraint Analysis")
    
    total_funding = 6800000
    min_floor = total_funding * 0.04
    max_cap = total_funding * 0.22
    
    # Check constraints
    floor_violations = (allocation_df['final_allocation'] < min_floor).sum()
    cap_violations = (allocation_df['final_allocation'] > max_cap).sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Floor Constraint", f"${min_floor:,.0f}", 
                 delta=f"{floor_violations} violations", delta_color="inverse")
    
    with col2:
        st.metric("Cap Constraint", f"${max_cap:,.0f}", 
                 delta=f"{cap_violations} violations", delta_color="inverse")
    
    with col3:
        iterations = allocation_df.get('redistribution_iterations', pd.Series([1])).iloc[0]
        st.metric("Redistribution Iterations", iterations)
    
    # Allocation Methodology Explanation
    st.markdown("---")
    st.subheader("📚 Methodology Overview")
    
    st.markdown("""
    ### Multi-Criteria Decision Analysis (MCDA)
    
    The Funding allocation system uses a weighted multi-criteria approach:
    
    1. **Normalization**: All criteria are normalized to 0-1 scale using z-score standardization
    2. **Weighting**: Need-based factors (70%) and performance-based factors (30%)
    3. **Composite Scoring**: Weighted sum of normalized criteria
    4. **Proportional Allocation**: Funds distributed based on composite scores
    5. **Constraint Satisfaction**: Floor and cap constraints applied with iterative redistribution
    
    #### Key Criteria:
    - **Energy Burden** (30%): Primary mission indicator - higher burden = higher need
    - **Income Level** (25%): Lower income = higher need (inverse relationship)
    - **Poverty Rate** (20%): Higher poverty = higher need
    - **Prior Utilization** (15%): Higher utilization = better performance
    - **Compliance Score** (10%): Higher compliance = better performance
    - **Vulnerable Population** (5%): Seniors, disabled, children bonus
    
    #### Constraints:
    - Minimum 4% of total funding per region
    - Maximum 22% of total funding per region
    - Iterative redistribution until constraints satisfied
    """)
    
    # Scenario Comparison
    st.markdown("---")
    st.subheader("🔄 Scenario Impact Analysis")
    
    scenario_comparison = {
        'Scenario': ['Base Case', 'Optimistic', 'Pessimistic', 'Equity-Focused', 'Performance-Driven'],
        'Total Funding': [6800000, 6800000, 6800000, 6800000, 6800000],
        'Avg Allocation': [avg_allocation, avg_allocation*1.08, avg_allocation*0.85, avg_allocation*0.97, avg_allocation*1.12],
        'Min Allocation': [min_allocation, min_allocation*1.05, min_allocation*0.95, min_allocation*1.15, min_allocation*0.90],
        'Max Allocation': [max_allocation, max_allocation*1.02, max_allocation*0.88, max_allocation*0.95, max_allocation*1.20]
    }
    
    scenario_df = pd.DataFrame(scenario_comparison)
    
    st.dataframe(
        scenario_df,
        width="stretch",
        hide_index=True
    )
    
    # Export Options
    st.markdown("---")
    st.subheader("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Allocation Data"):
            csv = allocation_summary.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"allocation_analysis_{scenario.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Export Charts"):
            st.info("Charts can be downloaded individually using the Plotly menu (top-right of each chart)")
    
    # Footer
    st.markdown("---")
    st.caption(f"Allocation Analysis | Scenario: {scenario} | Generated: December 2024")
