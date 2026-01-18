"""
Scenario Management Module
Handles scenario modeling and sensitivity analysis
"""

import pandas as pd
import numpy as np
import yaml
from typing import Dict, List, Tuple
import logging

class ScenarioManager:
    """Manages allocation scenarios and sensitivity analysis"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path):
        """Load system configuration"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def create_scenario_variants(self, base_data: pd.DataFrame, 
                               scenario_type: str = "all") -> Dict[str, pd.DataFrame]:
        """
        Create scenario variants with adjusted parameters
        
        Args:
            base_data: Base master data
            scenario_type: Type of scenarios to create
            
        Returns:
            Dictionary of scenario dataframes
        """
        scenarios = {}
        
        if scenario_type in ["all", "economic"]:
            scenarios.update(self._create_economic_scenarios(base_data))
        
        if scenario_type in ["all", "funding"]:
            scenarios.update(self._create_funding_scenarios(base_data))
        
        if scenario_type in ["all", "policy"]:
            scenarios.update(self._create_policy_scenarios(base_data))
        
        if scenario_type in ["all", "emergency"]:
            scenarios.update(self._create_emergency_scenarios(base_data))
        
        return scenarios
    
    def _create_economic_scenarios(self, base_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create economic condition scenarios"""
        scenarios = {}
        
        # Recession Scenario
        recession_df = base_data.copy()
        recession_df['median_income'] *= 0.85  # 15% income drop
        recession_df['unemployment_rate'] = (recession_df['unemployment_rate'] * 1.8).clip(upper=0.25)
        recession_df['poverty_rate'] = (recession_df['poverty_rate'] * 1.4).clip(upper=0.45)
        recession_df['energy_burden_pct'] = (recession_df['energy_burden_pct'] * 1.25).clip(upper=0.45)
        recession_df['households_served'] = (recession_df['households_served'] * 1.3).astype(int)
        scenarios['Recession'] = recession_df
        
        # Economic Growth Scenario
        growth_df = base_data.copy()
        growth_df['median_income'] *= 1.12  # 12% income increase
        growth_df['unemployment_rate'] *= 0.7
        growth_df['poverty_rate'] *= 0.85
        growth_df['energy_burden_pct'] *= 0.88
        growth_df['households_served'] = (growth_df['households_served'] * 0.92).astype(int)
        scenarios['Economic Growth'] = growth_df
        
        # Energy Crisis Scenario
        energy_crisis_df = base_data.copy()
        energy_crisis_df['avg_monthly_bill'] *= 1.4  # 40% energy cost increase
        energy_crisis_df['energy_burden_pct'] = (energy_crisis_df['energy_burden_pct'] * 1.6).clip(upper=0.50)
        energy_crisis_df['households_served'] = (energy_crisis_df['households_served'] * 1.5).astype(int)
        scenarios['Energy Crisis'] = energy_crisis_df
        
        return scenarios
    
    def _create_funding_scenarios(self, base_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create funding level scenarios"""
        scenarios = {}
        
        # Funding scenarios don't modify base data, but will affect allocations
        scenarios['Base Funding'] = base_data.copy()
        scenarios['Increased Funding (+25%)'] = base_data.copy()
        scenarios['Reduced Funding (-20%)'] = base_data.copy()
        scenarios['Emergency Funding (+50%)'] = base_data.copy()
        
        return scenarios
    
    def _create_policy_scenarios(self, base_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create policy change scenarios"""
        scenarios = {}
        
        # Eligibility Expansion
        eligibility_df = base_data.copy()
        eligibility_df['low_income_population'] = (eligibility_df['low_income_population'] * 1.35).astype(int)
        eligibility_df['households_served'] = (eligibility_df['households_served'] * 1.4).astype(int)
        scenarios['Eligibility Expansion'] = eligibility_df
        
        # Benefit Increase Policy
        benefit_df = base_data.copy()
        benefit_df['avg_benefit'] *= 1.25
        scenarios['Benefit Increase (+25%)'] = benefit_df
        
        # Performance-Focused Policy
        performance_df = base_data.copy()
        performance_df['compliance_score'] = (performance_df['compliance_score'] * 1.1).clip(upper=1.0)
        performance_df['utilization_rate'] = (performance_df['utilization_rate'] * 1.05).clip(upper=1.0)
        scenarios['Performance-Focused'] = performance_df
        
        return scenarios
    
    def _create_emergency_scenarios(self, base_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create emergency/disaster scenarios"""
        scenarios = {}
        
        # Natural Disaster Scenario
        disaster_df = base_data.copy()
        disaster_df['median_income'] *= 0.9  # Economic disruption
        disaster_df['energy_burden_pct'] = (disaster_df['energy_burden_pct'] * 1.8).clip(upper=0.55)
        disaster_df['households_served'] = (disaster_df['households_served'] * 2.2).astype(int)
        scenarios['Natural Disaster'] = disaster_df
        
        # Extreme Weather Scenario
        weather_df = base_data.copy()
        weather_df['avg_monthly_bill'] *= 1.6
        weather_df['energy_burden_pct'] = (weather_df['energy_burden_pct'] * 1.7).clip(upper=0.50)
        scenarios['Extreme Weather'] = weather_df
        
        return scenarios
    
    def run_sensitivity_analysis(self, base_data: pd.DataFrame, 
                               allocation_engine, parameter: str,
                               range_values: List[float]) -> Dict[str, Dict]:
        """
        Run sensitivity analysis on a specific parameter
        
        Args:
            base_data: Base master data
            allocation_engine: AllocationEngine instance
            parameter: Parameter to vary
            range_values: List of values to test
            
        Returns:
            Dictionary with results for each parameter value
        """
        results = {}
        
        for value in range_values:
            # Create modified data
            modified_data = self._modify_parameter(base_data.copy(), parameter, value)
            
            # Run allocation
            allocation_result = allocation_engine.calculate_allocations(modified_data)
            
            # Calculate metrics
            metrics = self._calculate_sensitivity_metrics(allocation_result)
            
            results[f"{parameter}_{value}"] = {
                'parameter_value': value,
                'allocation_result': allocation_result,
                'metrics': metrics
            }
        
        return results
    
    def _modify_parameter(self, df: pd.DataFrame, parameter: str, value: float) -> pd.DataFrame:
        """Modify a specific parameter in the dataframe"""
        
        if parameter == "poverty_weight":
            # This would be handled by the allocation engine
            pass
        elif parameter == "energy_burden_multiplier":
            df['energy_burden_pct'] *= value
        elif parameter == "income_threshold":
            # Adjust income levels relative to threshold
            df['median_income'] *= value
        elif parameter == "compliance_threshold":
            # Adjust compliance scores
            df['compliance_score'] = df['compliance_score'] * value
        elif parameter == "funding_level":
            # Funding level affects allocation, not input data
            pass
        
        return df
    
    def _calculate_sensitivity_metrics(self, allocation_result: pd.DataFrame) -> Dict:
        """Calculate metrics for sensitivity analysis"""
        
        return {
            'total_allocation': allocation_result['final_allocation'].sum(),
            'mean_allocation': allocation_result['final_allocation'].mean(),
            'std_allocation': allocation_result['final_allocation'].std(),
            'coefficient_variation': allocation_result['final_allocation'].std() / allocation_result['final_allocation'].mean(),
            'min_allocation': allocation_result['final_allocation'].min(),
            'max_allocation': allocation_result['final_allocation'].max(),
            'range_allocation': allocation_result['final_allocation'].max() - allocation_result['final_allocation'].min(),
            'households_served_total': allocation_result['expected_households_served'].sum(),
            'avg_benefit_per_household': allocation_result['allocation_per_household'].mean()
        }
    
    def monte_carlo_simulation(self, base_data: pd.DataFrame, 
                             allocation_engine, n_simulations: int = 1000,
                             uncertainty_factors: Dict = None) -> Dict:
        """
        Run Monte Carlo simulation for uncertainty analysis
        
        Args:
            base_data: Base master data
            allocation_engine: AllocationEngine instance
            n_simulations: Number of simulations to run
            uncertainty_factors: Dictionary of parameter uncertainties
            
        Returns:
            Dictionary with simulation results and statistics
        """
        
        if uncertainty_factors is None:
            uncertainty_factors = {
                'poverty_rate': {'std': 0.05, 'distribution': 'normal'},
                'energy_burden_pct': {'std': 0.08, 'distribution': 'normal'},
                'median_income': {'std': 5000, 'distribution': 'normal'},
                'compliance_score': {'std': 0.08, 'distribution': 'normal'},
                'households_served': {'std': 200, 'distribution': 'normal'}
            }
        
        simulation_results = []
        
        for i in range(n_simulations):
            # Create perturbed data
            perturbed_data = self._perturb_data(base_data.copy(), uncertainty_factors)
            
            # Run allocation
            allocation_result = allocation_engine.calculate_allocations(perturbed_data)
            
            # Store key results
            simulation_results.append({
                'simulation_id': i,
                'total_allocation': allocation_result['final_allocation'].sum(),
                'mean_allocation': allocation_result['final_allocation'].mean(),
                'coefficient_variation': allocation_result['final_allocation'].std() / allocation_result['final_allocation'].mean(),
                'min_allocation': allocation_result['final_allocation'].min(),
                'max_allocation': allocation_result['final_allocation'].max(),
                'households_served': allocation_result['expected_households_served'].sum()
            })
        
        # Convert to DataFrame for analysis
        results_df = pd.DataFrame(simulation_results)
        
        # Calculate statistics
        statistics = {
            'mean_total_allocation': results_df['total_allocation'].mean(),
            'std_total_allocation': results_df['total_allocation'].std(),
            'ci_95_lower_total': results_df['total_allocation'].quantile(0.025),
            'ci_95_upper_total': results_df['total_allocation'].quantile(0.975),
            'mean_households_served': results_df['households_served'].mean(),
            'std_households_served': results_df['households_served'].std(),
            'probability_shortfall': (results_df['total_allocation'] < 6000000).mean(),
            'probability_surplus': (results_df['total_allocation'] > 7000000).mean()
        }
        
        return {
            'simulation_results': results_df,
            'statistics': statistics,
            'n_simulations': n_simulations
        }
    
    def _perturb_data(self, df: pd.DataFrame, uncertainty_factors: Dict) -> pd.DataFrame:
        """Perturb data according to uncertainty factors"""
        
        for parameter, config in uncertainty_factors.items():
            if parameter in df.columns:
                std = config.get('std', 0.1)
                distribution = config.get('distribution', 'normal')
                
                if distribution == 'normal':
                    noise = np.random.normal(0, std, len(df))
                elif distribution == 'uniform':
                    noise = np.random.uniform(-std, std, len(df))
                else:
                    noise = np.random.normal(0, std, len(df))
                
                # Apply noise
                df[parameter] = df[parameter] + noise
                
                # Ensure values stay within reasonable bounds
                if parameter == 'poverty_rate':
                    df[parameter] = df[parameter].clip(lower=0.02, upper=0.50)
                elif parameter == 'energy_burden_pct':
                    df[parameter] = df[parameter].clip(lower=0.02, upper=0.60)
                elif parameter == 'compliance_score':
                    df[parameter] = df[parameter].clip(lower=0.5, upper=1.0)
                elif parameter == 'households_served':
                    df[parameter] = df[parameter].clip(lower=100)
        
        return df
    
    def forecast_demand(self, historical_df: pd.DataFrame, 
                       periods: int = 12, method: str = "linear") -> pd.DataFrame:
        """
        Forecast future energy assistance demand
        
        Args:
            historical_df: Historical trends data
            periods: Number of periods to forecast
            method: Forecasting method
            
        Returns:
            DataFrame with forecasted values
        """
        
        # Aggregate historical data by year
        annual_data = historical_df.groupby('year').agg({
            'households_served': 'sum',
            'allocation_amount': 'sum',
            'avg_benefit': 'mean'
        }).reset_index()
        
        if method == "linear":
            # Simple linear trend
            from sklearn.linear_model import LinearRegression
            
            X = annual_data['year'].values.reshape(-1, 1)
            
            # Forecast households served
            y_households = annual_data['households_served'].values
            model_households = LinearRegression().fit(X, y_households)
            
            # Forecast allocation amount
            y_allocation = annual_data['allocation_amount'].values
            model_allocation = LinearRegression().fit(X, y_allocation)
            
        elif method == "exponential_smoothing":
            # Exponential smoothing (simplified)
            alpha = 0.3  # smoothing parameter
            
            households_smoothed = [annual_data['households_served'].iloc[0]]
            allocation_smoothed = [annual_data['allocation_amount'].iloc[0]]
            
            for i in range(1, len(annual_data)):
                households_smoothed.append(alpha * annual_data['households_served'].iloc[i] + 
                                         (1 - alpha) * households_smoothed[-1])
                allocation_smoothed.append(alpha * annual_data['allocation_amount'].iloc[i] + 
                                         (1 - alpha) * allocation_smoothed[-1])
            
            # Simple trend extrapolation
            households_trend = (households_smoothed[-1] - households_smoothed[-3]) / 2
            allocation_trend = (allocation_smoothed[-1] - allocation_smoothed[-3]) / 2
            
        # Generate future periods
        last_year = annual_data['year'].max()
        future_years = list(range(last_year + 1, last_year + periods + 1))
        
        forecasts = []
        
        for year in future_years:
            if method == "linear":
                pred_households = model_households.predict([[year]])[0]
                pred_allocation = model_allocation.predict([[year]])[0]
            else:  # exponential_smoothing
                pred_households = households_smoothed[-1] + households_trend * (year - last_year)
                pred_allocation = allocation_smoothed[-1] + allocation_trend * (year - last_year)
            
            forecasts.append({
                'year': year,
                'forecasted_households': max(0, int(pred_households)),
                'forecasted_allocation': max(0, pred_allocation),
                'forecasted_avg_benefit': pred_allocation / pred_households if pred_households > 0 else 0,
                'confidence_interval_lower': pred_households * 0.85,
                'confidence_interval_upper': pred_households * 1.15
            })
        
        return pd.DataFrame(forecasts)
