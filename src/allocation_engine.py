"""
Allocation Engine Module
Core allocation algorithm with multi-criteria decision analysis
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from scipy import stats
import logging
from typing import Dict, Tuple, List

class AllocationEngine:
    """Core allocation engine with weighted multi-criteria decision analysis"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self._load_config(config_path)
        self.weights = self.config.get('weights', {})
        self.funding_params = self.config.get('funding', {})
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path):
        """Load system configuration"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def calculate_allocations(self, master_df: pd.DataFrame, 
                            scenario: str = "Base Case") -> pd.DataFrame:
        """
        Main allocation calculation using weighted multi-criteria analysis
        
        Args:
            master_df: Master demographic and program data
            scenario: Scenario name for different weight configurations
            
        Returns:
            DataFrame with allocation results
        """
        df = master_df.copy()
        
        # Step 1: Calculate normalized scores for each criterion
        df = self._calculate_normalized_scores(df)
        
        # Step 2: Apply scenario-specific adjustments
        df = self._apply_scenario_weights(df, scenario)
        
        # Step 3: Calculate composite need scores
        df = self._calculate_composite_scores(df)
        
        # Step 4: Calculate initial allocations
        df = self._calculate_initial_allocations(df)
        
        # Step 5: Apply floor and cap constraints
        df = self._apply_allocation_constraints(df)
        
        # Step 6: Iterative redistribution for constraint satisfaction
        df = self._iterative_redistribution(df)
        
        # Step 7: Calculate final metrics
        df = self._calculate_final_metrics(df)
        
        return df
    
    def _calculate_normalized_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate z-score normalized scores for each criterion"""
        
        # Income Level Score (inverse - lower income = higher score)
        df['income_score'] = 1 - stats.zscore(df['median_income'])
        df['income_score'] = self._normalize_to_01(df['income_score'])
        
        # Energy Burden Score (higher burden = higher score)
        df['energy_burden_score'] = stats.zscore(df['energy_burden_pct'])
        df['energy_burden_score'] = self._normalize_to_01(df['energy_burden_score'])
        
        # Poverty Rate Score (higher poverty = higher score)
        df['poverty_score'] = stats.zscore(df['poverty_rate'])
        df['poverty_score'] = self._normalize_to_01(df['poverty_score'])
        
        # Prior Utilization Score (higher utilization = higher score)
        df['utilization_score'] = stats.zscore(df['utilization_rate'])
        df['utilization_score'] = self._normalize_to_01(df['utilization_score'])
        
        # Compliance Score (already 0-1 scale)
        df['compliance_score_norm'] = df['compliance_score']
        
        # Vulnerable Population Score
        total_vulnerable = (df['seniors_65_plus'] + df['disabled_population'] + df['children_under_18'])
        df['vulnerable_score'] = stats.zscore(total_vulnerable / df['total_population'])
        df['vulnerable_score'] = self._normalize_to_01(df['vulnerable_score'])
        
        return df
    
    def _normalize_to_01(self, series: pd.Series) -> pd.Series:
        """Normalize series to 0-1 scale"""
        min_val, max_val = series.min(), series.max()
        if max_val > min_val:
            return (series - min_val) / (max_val - min_val)
        return pd.Series([0.5] * len(series), index=series.index)
    
    def _apply_scenario_weights(self, df: pd.DataFrame, scenario: str) -> pd.DataFrame:
        """Apply scenario-specific weight adjustments"""
        
        scenario_multipliers = {
            "Base Case": {"income": 1.0, "energy_burden": 1.0, "poverty": 1.0, "performance": 1.0},
            "Optimistic": {"income": 0.9, "energy_burden": 1.1, "poverty": 0.9, "performance": 1.2},
            "Pessimistic": {"income": 1.2, "energy_burden": 1.3, "poverty": 1.1, "performance": 0.8},
            "Equity-Focused": {"income": 1.4, "energy_burden": 1.2, "poverty": 1.3, "performance": 0.7},
            "Performance-Driven": {"income": 0.7, "energy_burden": 0.8, "poverty": 0.6, "performance": 1.5}
        }
        
        multipliers = scenario_multipliers.get(scenario, scenario_multipliers["Base Case"])
        
        # Apply multipliers to weights (will be used in composite calculation)
        df['scenario_income_mult'] = multipliers["income"]
        df['scenario_energy_mult'] = multipliers["energy_burden"]
        df['scenario_poverty_mult'] = multipliers["poverty"]
        df['scenario_performance_mult'] = multipliers["performance"]
        
        return df
    
    def _calculate_composite_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite need and performance scores"""
        
        # Need-based score (70% of total weight)
        df['need_score'] = (
            self.weights.get('income_level', 0.25) * df['income_score'] * df['scenario_income_mult'] +
            self.weights.get('energy_burden', 0.30) * df['energy_burden_score'] * df['scenario_energy_mult'] +
            self.weights.get('poverty_rate', 0.20) * df['poverty_score'] * df['scenario_poverty_mult'] +
            self.weights.get('vulnerable_population', 0.05) * df['vulnerable_score']
        )
        
        # Performance-based score (30% of total weight)
        df['performance_score'] = (
            self.weights.get('prior_utilization', 0.15) * df['utilization_score'] * df['scenario_performance_mult'] +
            self.weights.get('compliance_score', 0.10) * df['compliance_score_norm'] * df['scenario_performance_mult']
        )
        
        # Composite score (weighted average)
        df['composite_score'] = 0.7 * df['need_score'] + 0.3 * df['performance_score']
        
        return df
    
    def _calculate_initial_allocations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate initial allocations based on composite scores"""
        
        total_funding = self.funding_params.get('available_for_allocation', 6460000)
        
        # Calculate total composite score across all regions
        total_composite = df['composite_score'].sum()
        
        if total_composite > 0:
            # Proportional allocation based on composite scores
            df['initial_allocation'] = (df['composite_score'] / total_composite) * total_funding
        else:
            # Equal allocation if no variation in scores
            df['initial_allocation'] = total_funding / len(df)
        
        return df
    
    def _apply_allocation_constraints(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply floor and cap constraints to allocations"""
        
        total_funding = self.funding_params.get('available_for_allocation', 6460000)
        min_floor = self.funding_params.get('minimum_floor', 0.04)
        max_cap = self.funding_params.get('maximum_cap', 0.22)
        
        # Calculate floor and cap amounts
        floor_amount = total_funding * min_floor
        cap_amount = total_funding * max_cap
        
        # Apply constraints
        df['constrained_allocation'] = df['initial_allocation'].clip(lower=floor_amount, upper=cap_amount)
        
        # Calculate constraint violations
        df['floor_violation'] = df['initial_allocation'] < floor_amount
        df['cap_violation'] = df['initial_allocation'] > cap_amount
        
        return df
    
    def _iterative_redistribution(self, df: pd.DataFrame, max_iterations: int = 100) -> pd.DataFrame:
        """Iteratively redistribute funds to satisfy constraints"""
        
        total_funding = self.funding_params.get('available_for_allocation', 6460000)
        min_floor = self.funding_params.get('minimum_floor', 0.04)
        max_cap = self.funding_params.get('maximum_cap', 0.22)
        
        floor_amount = total_funding * min_floor
        cap_amount = total_funding * max_cap
        
        for iteration in range(max_iterations):
            current_total = df['constrained_allocation'].sum()
            
            # Check if we've converged
            if abs(current_total - total_funding) < 100:  # Within $100
                break
            
            # Calculate adjustment factor
            adjustment_factor = total_funding / current_total
            
            # Apply adjustment
            df['constrained_allocation'] = df['constrained_allocation'] * adjustment_factor
            
            # Re-apply constraints
            df['constrained_allocation'] = df['constrained_allocation'].clip(lower=floor_amount, upper=cap_amount)
            
            # Check for convergence
            if iteration == max_iterations - 1:
                self.logger.warning(f"Max iterations reached in redistribution: {iteration + 1}")
        
        df['final_allocation'] = df['constrained_allocation']
        df['redistribution_iterations'] = iteration + 1
        
        return df
    
    def _calculate_final_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate final allocation metrics and KPIs"""
        
        # Per-household metrics
        df['allocation_per_household'] = df['final_allocation'] / df['households_served']
        df['benefit_increase_pct'] = ((df['allocation_per_household'] - df['avg_benefit']) / df['avg_benefit']) * 100
        
        # Population-based metrics
        df['allocation_per_capita'] = df['final_allocation'] / df['total_population']
        df['allocation_per_low_income'] = df['final_allocation'] / df['low_income_population']
        
        # Performance metrics
        df['expected_households_served'] = df['final_allocation'] / df['avg_benefit']
        df['utilization_projection'] = df['expected_households_served'] / df['low_income_population']
        
        # Ranking
        df['allocation_rank'] = df['final_allocation'].rank(ascending=False)
        df['need_rank'] = df['need_score'].rank(ascending=False)
        df['performance_rank'] = df['performance_score'].rank(ascending=False)
        
        # Equity metrics
        df['allocation_share'] = df['final_allocation'] / df['final_allocation'].sum()
        df['population_share'] = df['total_population'] / df['total_population'].sum()
        df['low_income_share'] = df['low_income_population'] / df['low_income_population'].sum()
        
        return df
    
    def run_scenario_analysis(self, master_df: pd.DataFrame, 
                            scenarios: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Run allocation analysis for multiple scenarios"""
        
        if scenarios is None:
            scenarios = ["Base Case", "Optimistic", "Pessimistic", "Equity-Focused", "Performance-Driven"]
        
        results = {}
        
        for scenario in scenarios:
            self.logger.info(f"Running scenario: {scenario}")
            results[scenario] = self.calculate_allocations(master_df, scenario)
        
        return results
    
    def calculate_equity_metrics(self, allocation_df: pd.DataFrame) -> Dict:
        """Calculate equity metrics for allocation"""
        
        # Coefficient of variation
        mean_allocation = allocation_df['final_allocation'].mean()
        std_allocation = allocation_df['final_allocation'].std()
        coefficient_variation = std_allocation / mean_allocation if mean_allocation > 0 else 0
        
        # Gini coefficient (simplified)
        allocations = allocation_df['final_allocation'].sort_values()
        n = len(allocations)
        cumsum = allocations.cumsum()
        gini_coefficient = (2 * np.sum((np.arange(1, n+1) * allocations) - cumsum)) / (n * allocations.sum()) if allocations.sum() > 0 else 0
        
        # Urban vs Rural equity (mock classification)
        urban_regions = allocation_df[allocation_df['region_name'].isin([
            'Jefferson County', 'Madison County', 'Mobile County', 'Montgomery County'
        ])]
        rural_regions = allocation_df[~allocation_df.index.isin(urban_regions.index)]
        
        urban_avg = urban_regions['allocation_per_capita'].mean() if len(urban_regions) > 0 else 0
        rural_avg = rural_regions['allocation_per_capita'].mean() if len(rural_regions) > 0 else 0
        urban_rural_ratio = urban_avg / rural_avg if rural_avg > 0 else 1
        
        return {
            'coefficient_variation': coefficient_variation,
            'gini_coefficient': gini_coefficient,
            'urban_rural_ratio': urban_rural_ratio,
            'urban_avg_per_capita': urban_avg,
            'rural_avg_per_capita': rural_avg
        }
    
    def export_allocation_results(self, allocation_df: pd.DataFrame, 
                                filename: str = None) -> str:
        """Export allocation results to CSV"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"allocation_results_{timestamp}.csv"
        
        output_path = f"reports/{filename}"
        os.makedirs("reports", exist_ok=True)
        
        # Select key columns for export
        export_cols = [
            'region_name', 'final_allocation', 'allocation_per_household',
            'need_score', 'performance_score', 'composite_score',
            'households_served', 'expected_households_served',
            'energy_burden_pct', 'poverty_rate', 'median_income',
            'compliance_score', 'utilization_rate'
        ]
        
        export_df = allocation_df[export_cols].copy()
        export_df.to_csv(output_path, index=False)
        
        self.logger.info(f"Allocation results exported to {output_path}")
        return output_path
