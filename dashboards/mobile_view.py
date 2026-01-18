"""
Mobile Field Dashboard
Optimized for mobile devices and field workers
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_mobile_dashboard(master_df, scenario):
    """Render the mobile-optimized field dashboard"""
    
    st.title("📱 Field Dashboard")
    st.markdown(f"### Mobile View - {scenario}")
    
    # Mobile-optimized metrics
    col1, col2 = st.columns(2)
    
    with col1:
        total_households = master_df['households_served'].sum()
        st.metric("Total Served", f"{total_households:,}")
    
    with col2:
        avg_benefit = master_df['avg_benefit'].mean()
        st.metric("Avg Benefit", f"${avg_benefit:.0f}")
    
    # Quick Region Lookup
    st.markdown("---")
    st.subheader("🔍 Quick Region Lookup")
    
    region_name = st.selectbox("Select Region:", master_df['region_name'].tolist())
    
    if region_name:
        region_data = master_df[master_df['region_name'] == region_name].iloc[0]
        
        st.markdown(f"**{region_name}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Allocation", f"${region_data['final_allocation']:,.0f}")
            st.metric("Households", f"{region_data['households_served']:,}")
            st.metric("Energy Burden", f"{region_data['energy_burden_pct']:.1%}")
        
        with col2:
            st.metric("Compliance", f"{region_data['compliance_score']:.1%}")
            st.metric("Poverty Rate", f"{region_data['poverty_rate']:.1%}")
            st.metric("Median Income", f"${region_data['median_income']:,.0f}")
    
    # Top Priority Regions
    st.markdown("---")
    st.subheader("🚨 Priority Regions")
    
    # Sort by need indicators
    priority_df = master_df.nlargest(5, 'energy_burden_pct')[['region_name', 'energy_burden_pct', 'final_allocation']]
    
    st.dataframe(
        priority_df,
        width="stretch",
        hide_index=True
    )
    
    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Emergency Contact"):
            st.info("Emergency Hotline: 1-770-HELP")
        
        if st.button("📍 Find Office"):
            st.info("Use GPS navigation to nearest office")
    
    with col2:
        if st.button("📋 Report Issue"):
            st.info("Issue reporting form available in full dashboard")
        
        if st.button("📊 View Map"):
            st.info("Interactive map available in full dashboard")
    
    # Offline Capability Note
    st.markdown("---")
    st.info("💡 **Mobile Features**\n\n- Touch-optimized interface\n- Offline data caching\n- GPS integration ready\n- Simplified workflows")
    
    # Footer
    st.markdown("---")
    st.caption("Mobile Field Dashboard | Touch-Optimized | v3.0")
