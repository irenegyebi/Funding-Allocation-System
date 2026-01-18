"""
Predictive Analytics Dashboard
Forecasting and scenario modeling capabilities
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_predictive_analytics(master_df, scenario_manager):
    """Render the predictive analytics dashboard"""
    
    st.title("🔮 Predictive Analytics")
    st.markdown("### Forecasting and Scenario Modeling")
    
    # Forecasting Section
    st.subheader("📈 Demand Forecasting")
    
    # Generate historical data for forecasting
    historical_data = []
    years = list(range(2020, 2026))
    
    for year in years:
        households = int(14500 * (1 + (year - 2020) * 0.05 + np.random.uniform(-0.05, 0.08)))
        funding = 6800000 * (1 + (year - 2020) * 0.03 + np.random.uniform(-0.10, 0.12))
        avg_benefit = funding / households if households > 0 else 0
        
        historical_data.append({
            'year': year,
            'households_served': households,
            'total_funding': funding,
            'avg_benefit': avg_benefit,
            'energy_cost_index': 100 + (year - 2020) * 4 + np.random.uniform(-5, 8),
            'unemployment_rate': 6.5 - (year - 2020) * 0.3 + np.random.uniform(-1, 1)
        })
    
    hist_df = pd.DataFrame(historical_data)
    
    # Forecast future years
    forecast_years = list(range(2026, 2031))
    forecast_data = []
    
    base_households = hist_df['households_served'].iloc[-1]
    base_funding = hist_df['total_funding'].iloc[-1]
    
    for year in forecast_years:
        year_offset = year - 2025
        
        # Different scenarios
        if st.session_state.get('forecast_scenario', 'Base Case') == 'Optimistic':
            households = int(base_households * (1 + year_offset * 0.08))
            funding = base_funding * (1 + year_offset * 0.05)
        elif st.session_state.get('forecast_scenario', 'Base Case') == 'Pessimistic':
            households = int(base_households * (1 + year_offset * 0.02))
            funding = base_funding * (1 + year_offset * 0.01)
        else:  # Base Case
            households = int(base_households * (1 + year_offset * 0.05))
            funding = base_funding * (1 + year_offset * 0.03)
        
        avg_benefit = funding / households if households > 0 else 0
        
        forecast_data.append({
            'year': year,
            'households_served': households,
            'total_funding': funding,
            'avg_benefit': avg_benefit,
            'forecast_type': 'Forecast'
        })
    
    forecast_df = pd.DataFrame(forecast_data)
    
    # Combine historical and forecast
    hist_df['forecast_type'] = 'Historical'
    combined_df = pd.concat([hist_df, forecast_df], ignore_index=True)
    
    # Forecast Controls
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_scenario = st.selectbox(
            "Forecast Scenario:",
            ['Base Case', 'Optimistic', 'Pessimistic'],
            key='forecast_scenario'
        )
    
    with col2:
        forecast_years_slider = st.slider("Forecast Period (Years):", 3, 7, 5)
    
    # Main Forecast Chart
    st.subheader("📊 Households Served Forecast")
    
    fig_forecast = px.line(
        combined_df,
        x='year',
        y='households_served',
        color='forecast_type',
        title=f"Households Served Forecast - {forecast_scenario} Scenario",
        color_discrete_map={'Historical': '#1B2951', 'Forecast': '#3B82F6'}
    )
    
    # Add confidence intervals for forecast
    forecast_years_filtered = list(range(2026, 2026 + forecast_years_slider))
    
    upper_bound = [f * 1.15 for f in forecast_df[forecast_df['year'].isin(forecast_years_filtered)]['households_served']]
    lower_bound = [f * 0.85 for f in forecast_df[forecast_df['year'].isin(forecast_years_filtered)]['households_served']]
    
    fig_forecast.add_trace(go.Scatter(
        x=forecast_years_filtered,
        y=upper_bound,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        name='Upper CI'
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=forecast_years_filtered,
        y=lower_bound,
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(width=0),
        showlegend=False,
        name='Lower CI'
    ))
    
    fig_forecast.update_layout(height=500)
    st.plotly_chart(fig_forecast, width="stretch")
    
    # Scenario Comparison
    st.markdown("---")
    st.subheader("🔍 Scenario Comparison")
    
    # Create scenario comparison data
    scenarios = ['Base Case', 'Optimistic', 'Pessimistic']
    scenario_data = []
    
    for scenario in scenarios:
        if scenario == 'Optimistic':
            multiplier = 1.08
            funding_mult = 1.05
        elif scenario == 'Pessimistic':
            multiplier = 1.02
            funding_mult = 1.01
        else:
            multiplier = 1.05
            funding_mult = 1.03
        
        households_2027 = int(base_households * (multiplier ** 2))
        funding_2027 = base_funding * (funding_mult ** 2)
        avg_benefit_2027 = funding_2027 / households_2027
        
        scenario_data.append({
            'Scenario': scenario,
            'Households 2027': households_2027,
            'Funding 2027': funding_2027,
            'Avg Benefit 2027': avg_benefit_2027,
            'Growth Rate': (multiplier - 1) * 100
        })
    
    scenario_df = pd.DataFrame(scenario_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(
            scenario_df,
            width="stretch",
            hide_index=True
        )
    
    with col2:
        # Scenario visualization
        fig_scenarios = px.bar(
            scenario_df,
            x='Scenario',
            y='Households 2027',
            title="Projected Households Served by Scenario (2027)",
            color='Scenario',
            color_discrete_map={
                'Base Case': '#6B7280',
                'Optimistic': '#059669',
                'Pessimistic': '#DC2626'
            }
        )
        
        fig_scenarios.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_scenarios, width="stretch")
    
    # Economic Indicators Impact
    st.markdown("---")
    st.subheader("📉 Economic Indicators Impact")
    
    # Economic indicators chart
    fig_economic = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Energy Cost Index', 'Unemployment Rate', 'Median Income Trend', 'Poverty Rate'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Energy cost index
    fig_economic.add_trace(
        go.Scatter(x=combined_df['year'], y=combined_df['energy_cost_index'], name='Energy Cost'),
        row=1, col=1
    )
    
    # Unemployment rate (simulated)
    unemployment_data = [6.5 - (year - 2020) * 0.2 + np.random.uniform(-0.5, 0.5) for year in combined_df['year']]
    fig_economic.add_trace(
        go.Scatter(x=combined_df['year'], y=unemployment_data, name='Unemployment'),
        row=1, col=2
    )
    
    # Median income (simulated)
    income_data = [45000 + (year - 2020) * 1200 + np.random.uniform(-2000, 3000) for year in combined_df['year']]
    fig_economic.add_trace(
        go.Scatter(x=combined_df['year'], y=income_data, name='Median Income'),
        row=2, col=1
    )
    
    # Poverty rate (simulated)
    poverty_data = [15.2 - (year - 2020) * 0.3 + np.random.uniform(-0.8, 0.8) for year in combined_df['year']]
    fig_economic.add_trace(
        go.Scatter(x=combined_df['year'], y=poverty_data, name='Poverty Rate'),
        row=2, col=2
    )
    
    fig_economic.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_economic, width="stretch")
    
    # Risk Assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Funding Risks**")
        
        risk_factors = [
            {"Risk Factor": "Federal Budget Cuts", "Probability": "Medium", "Impact": "High", "Mitigation": "Diversify funding sources"},
            {"Risk Factor": "Economic Recession", "Probability": "Low", "Impact": "High", "Mitigation": "Emergency reserve fund"},
            {"Risk Factor": "Energy Price Volatility", "Probability": "High", "Impact": "Medium", "Mitigation": "Dynamic allocation model"},
            {"Risk Factor": "Regulatory Changes", "Probability": "Medium", "Impact": "Medium", "Mitigation": "Compliance monitoring"}
        ]
        
        risk_df = pd.DataFrame(risk_factors)
        st.dataframe(risk_df, width="stretch", hide_index=True)
    
    with col2:
        st.markdown("**Demand Risks**")
        
        demand_risks = [
            {"Risk Factor": "Increased Need", "Probability": "High", "Impact": "High", "Mitigation": "Scenario planning"},
            {"Risk Factor": "Climate Events", "Probability": "Medium", "Impact": "High", "Mitigation": "Emergency response protocols"},
            {"Risk Factor": "Population Changes", "Probability": "Low", "Impact": "Medium", "Mitigation": "Regular demographic updates"},
            {"Risk Factor": "Technology Disruption", "Probability": "Low", "Impact": "Low", "Mitigation": "System modernization"}
        ]
        
        demand_df = pd.DataFrame(demand_risks)
        st.dataframe(demand_df, width="stretch", hide_index=True)
    
    # Monte Carlo Simulation
    st.markdown("---")
    st.subheader("🎲 Monte Carlo Simulation")
    
    if st.button("Run Monte Carlo Simulation (1000 iterations)"):
        with st.spinner("Running simulation..."):
            # Simulate Monte Carlo results
            np.random.seed(42)
            n_simulations = 1000
            
            base_households_2027 = int(base_households * (1.05 ** 2))
            
            # Add uncertainty
            simulation_results = []
            for i in range(n_simulations):
                uncertainty = np.random.normal(1, 0.15)  # 15% standard deviation
                households_sim = int(base_households_2027 * uncertainty)
                simulation_results.append(households_sim)
            
            sim_df = pd.DataFrame({'households': simulation_results})
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Mean Households", f"{sim_df['households'].mean():.0f}")
                st.metric("95% Confidence Interval", f"{sim_df['households'].quantile(0.025):.0f} - {sim_df['households'].quantile(0.975):.0f}")
                st.metric("Probability of Shortfall", f"{(sim_df['households'] < base_households_2027 * 0.9).mean() * 100:.1f}%")
            
            with col2:
                # Histogram of results
                fig_mc = px.histogram(
                    sim_df,
                    x='households',
                    title="Monte Carlo Simulation Results (Households 2027)",
                    nbins=50
                )
                
                # Add confidence interval lines
                ci_lower = sim_df['households'].quantile(0.025)
                ci_upper = sim_df['households'].quantile(0.975)
                mean_val = sim_df['households'].mean()
                
                fig_mc.add_vline(x=ci_lower, line_dash="dash", line_color="red", annotation_text="95% CI Lower")
                fig_mc.add_vline(x=ci_upper, line_dash="dash", line_color="red", annotation_text="95% CI Upper")
                fig_mc.add_vline(x=mean_val, line_color="green", annotation_text="Mean")
                
                fig_mc.update_layout(height=400)
                st.plotly_chart(fig_mc, width="stretch")
    
    # Footer
    st.markdown("---")
    st.caption("Predictive Analytics Dashboard | Forecasts are estimates based on historical trends and assumptions")
