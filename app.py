"""
Funding Allocation System - Main Application
Streamlit-based dashboard with 7 interactive views
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from datetime import datetime, timedelta
import json
import os

# Import dashboard modules
from dashboards.executive_overview import render_executive_dashboard
from dashboards.allocation_analyzer import render_allocation_analysis
from dashboards.predictive_forecast import render_predictive_analytics
from dashboards.compliance_tracker import render_compliance_dashboard
from dashboards.equity_dashboard import render_equity_analysis
from dashboards.mobile_view import render_mobile_dashboard
from dashboards.report_generator import render_report_generator

# Import core modules
from src.allocation_engine import AllocationEngine
from src.data_loader import DataLoader
from src.scenarios import ScenarioManager
from src.compliance_monitor import ComplianceMonitor
from src.equity_analyzer import EquityAnalyzer

# Configure Streamlit page
st.set_page_config(
    page_title="Funding Allocation System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1B2951;
        --secondary-color: #6B7280;
        --accent-color: #3B82F6;
        --success-color: #059669;
        --warning-color: #D97706;
        --danger-color: #DC2626;
    }
    
    /* Professional styling */
    .main {
        background-color: #FAFBFC;
    }
    
    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    .kpi-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* Data tables */
    .dataframe {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1B2951;
        font-family: 'Georgia', serif;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1B2951;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #3B82F6;
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1B2951;
    }
    
    /* Mobile optimization */
    @media (max-width: 768px) {
        .kpi-value {
            font-size: 2em;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_system_data():
    """Load all system data with caching"""
    try:
        loader = DataLoader()
        return loader.load_all_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

@st.cache_resource
def initialize_engines():
    """Initialize allocation and scenario engines"""
    try:
        engine = AllocationEngine()
        scenario_manager = ScenarioManager()
        compliance_monitor = ComplianceMonitor()
        equity_analyzer = EquityAnalyzer()
        
        return engine, scenario_manager, compliance_monitor, equity_analyzer
    except Exception as e:
        st.error(f"Error initializing engines: {str(e)}")
        return None, None, None, None

def render_sidebar():
    """Render the navigation sidebar"""
    st.sidebar.title("Funding Allocation System")
    st.sidebar.markdown("### Navigation")
    
    # Dashboard selection
    dashboard_options = {
        "Executive Command Center": "executive",
        "Allocation Analysis": "allocation", 
        "Predictive Analytics": "predictive",
        "Compliance Tracker": "compliance",
        "Equity Analysis": "equity",
        "Mobile Field View": "mobile",
        "Report Generator": "reports"
    }
    
    selected_dashboard = st.sidebar.radio(
        "Select Dashboard:",
        list(dashboard_options.keys()),
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Scenario selector
    st.sidebar.markdown("### Scenario Selector")
    scenario = st.sidebar.selectbox(
        "Choose Scenario:",
        ["Base Case", "Optimistic", "Pessimistic", "Equity-Focused", "Performance-Driven"],
        index=0
    )
    
    # Date range selector
    st.sidebar.markdown("### Date Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2025, 1, 1))
    with col2:
        end_date = st.date_input("End Date", datetime(2025, 12, 31))
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.markdown("### Quick Actions")
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    if st.sidebar.button("📊 Export Current View"):
        st.sidebar.info("Export functionality available in Report Generator")
    
    if st.sidebar.button("📧 Email Report"):
        st.sidebar.info("Email functionality available in Report Generator")
    
    return dashboard_options[selected_dashboard], scenario, start_date, end_date

def render_header():
    """Render the main header"""
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        st.title("🏠 Funding Allocation System")
        st.markdown("**Energy Assistance Program - Enterprise Allocation Dashboard**")
    
    with col2:
        st.metric("Total Funding", "$6.8M", delta="+$200K vs last year")
        st.metric("Households Served", "16,847", delta="+1,234 vs last year")
    
    with col3:
        st.metric("Overall Compliance", "92.4%", delta="+2.1% vs last year")
        st.metric("Avg Benefit", "$403", delta="+$28 vs last year")
    
    st.markdown("---")

def main():
    """Main application entry point"""
    
    # Load data and initialize engines
    master_df, historical_df, compliance_df, energy_df = load_system_data()
    engine, scenario_mgr, compliance_monitor, equity_analyzer = initialize_engines()
    
    if master_df is None or engine is None:
        st.error("System failed to initialize. Please check data files and configuration.")
        return
    
    # --- NEW: Calculate allocations once for downstream dashboards ---
    try:
        allocation_df = engine.calculate_allocations(master_df)
    except Exception as e:
        st.error(f"Error calculating allocations: {e}")
        return


    # Render sidebar
    selected_dashboard, scenario, start_date, end_date = render_sidebar()
    
    # Render header
    render_header()
    
    # Route to appropriate dashboard
    if selected_dashboard == "executive":
        render_executive_dashboard(master_df, compliance_df, scenario)
    elif selected_dashboard == "allocation":
        render_allocation_analysis(master_df, engine, scenario)
    elif selected_dashboard == "predictive":
        render_predictive_analytics(master_df, scenario_mgr)
    elif selected_dashboard == "compliance":
        render_compliance_dashboard(compliance_df, compliance_monitor)
    elif selected_dashboard == "equity":
        render_equity_analysis(master_df, equity_analyzer)
    elif selected_dashboard == "mobile":
        render_mobile_dashboard(master_df, scenario)
    elif selected_dashboard == "reports":
        render_report_generator(master_df, compliance_df, scenario)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.markdown("**Version:** 3.0 Enterprise Edition")
    with col3:
        st.markdown("**Support:** proj-support@agcy.gov")

if __name__ == "__main__":
    main()
