"""
Equity Analysis Module
Analyzes geographic, demographic, and economic equity in allocations
"""

import pandas as pd
import numpy as np
import yaml
from scipy import stats
from typing import Dict, List, Tuple
import logging

class EquityAnalyzer:
    """Analyzes equity across multiple dimensions"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self._load_config(config_path)
        self.equity_targets = self.config.get('equity', {})
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path):
        """Load system configuration"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def comprehensive_equity_analysis(self, 
                                    master_df: pd.DataFrame) -> Dict:
        """
        Comprehensive equity analysis across multiple dimensions
        
        Args:
            allocation_df: Allocation results
            master_df: Master demographic data
            
        Returns:
            Dictionary with equity analysis results
        """
        
        # Merge allocation and demographic data
        merged_df = master_df.copy() #allocation_df.merge(master_df, on='region_name', how='inner')
        
        analysis = {
            'geographic_equity': self._analyze_geographic_equity(merged_df),
            'demographic_equity': self._analyze_demographic_equity(merged_df),
            'economic_equity': self._analyze_economic_equity(merged_df),
            'performance_equity': self._analyze_performance_equity(merged_df),
            'horizontal_equity': self._analyze_horizontal_equity(merged_df),
            'vertical_equity': self._analyze_vertical_equity(merged_df),
            'equity_indices': self._calculate_equity_indices(merged_df),
            'equity_targets': self._assess_against_targets(merged_df)
        }
        
        return analysis
    
    def _analyze_geographic_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze geographic equity (urban vs rural, regional disparities)"""
        
        # Classify regions as urban/rural (simplified)
        urban_regions = ['Jefferson County', 'Madison County', 'Mobile County', 'Montgomery County']
        df['area_type'] = df['region_name'].apply(lambda x: 'Urban' if x in urban_regions else 'Rural')
        
        # Calculate per-capita allocations
        df['allocation_per_capita'] = df['final_allocation'] / df['total_population']
        
        # Urban vs Rural analysis
        urban_data = df[df['area_type'] == 'Urban']
        rural_data = df[df['area_type'] == 'Rural']
        
        urban_avg = urban_data['allocation_per_capita'].mean()
        rural_avg = rural_data['allocation_per_capita'].mean()
        urban_rural_ratio = urban_avg / rural_avg if rural_avg > 0 else 1
        
        # Regional disparity analysis
        regional_stats = df.groupby('region_name', observed=True)['allocation_per_capita'].agg(['mean', 'std', 'count'])
        coefficient_variation = regional_stats['mean'].std() / regional_stats['mean'].mean()
        
        # Geographic distribution fairness
        population_shares = df['total_population'] / df['total_population'].sum()
        allocation_shares = df['final_allocation'] / df['final_allocation'].sum()
        geographic_correlation = np.corrcoef(population_shares, allocation_shares)[0, 1]
        
        return {
            'urban_rural_analysis': {
                'urban_avg_per_capita': urban_avg,
                'rural_avg_per_capita': rural_avg,
                'urban_rural_ratio': urban_rural_ratio,
                'urban_count': len(urban_data),
                'rural_count': len(rural_data)
            },
            'regional_disparity': {
                'coefficient_variation': coefficient_variation,
                'min_allocation': regional_stats['mean'].min(),
                'max_allocation': regional_stats['mean'].max(),
                'range_ratio': regional_stats['mean'].max() / regional_stats['mean'].min()
            },
            'geographic_fairness': {
                'population_allocation_correlation': geographic_correlation,
                'spatial_autocorrelation': self._calculate_morans_i(df)
            }
        }
    
    def _analyze_demographic_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze demographic equity (age, disability, vulnerable populations)"""
        
        # Vulnerable population analysis
        df['vulnerable_pct'] = (df['seniors_65_plus'] + df['disabled_population'] + df['children_under_18']) / df['total_population']
        
        # Correlation between vulnerable population percentage and allocation
        vulnerable_correlation = np.corrcoef(df['vulnerable_pct'], df['final_allocation'] / df['total_population'])[0, 1]
        
        # Senior population equity
        df['senior_pct'] = df['seniors_65_plus'] / df['total_population']
        senior_correlation = np.corrcoef(df['senior_pct'], df['allocation_per_capita'])[0, 1]
        
        # Disability equity
        df['disability_pct'] = df['disabled_population'] / df['total_population']
        disability_correlation = np.corrcoef(df['disability_pct'], df['allocation_per_capita'])[0, 1]
        
        # Create demographic quintiles
        df['vulnerable_quintile'] = pd.qcut(df['vulnerable_pct'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
        
        quintile_analysis = df.groupby('vulnerable_quintile', observed=True).agg({
            'allocation_per_capita': 'mean',
            'final_allocation': 'sum',
            'vulnerable_pct': 'mean'
        }).reset_index()
        
        # Progressivity analysis
        progressivity_index = self._calculate_progressivity_index(df)
        
        return {
            'vulnerable_population_equity': {
                'vulnerable_allocation_correlation': vulnerable_correlation,
                'progressivity_index': progressivity_index,
                'quintile_analysis': quintile_analysis.to_dict('records')
            },
            'senior_equity': {
                'senior_allocation_correlation': senior_correlation,
                'senior_benefit_ratio': df[df['senior_pct'] > df['senior_pct'].median()]['allocation_per_capita'].mean() / 
                                       df[df['senior_pct'] <= df['senior_pct'].median()]['allocation_per_capita'].mean()
            },
            'disability_equity': {
                'disability_allocation_correlation': disability_correlation,
                'disability_benefit_ratio': df[df['disability_pct'] > df['disability_pct'].median()]['allocation_per_capita'].mean() / 
                                           df[df['disability_pct'] <= df['disability_pct'].median()]['allocation_per_capita'].mean()
            }
        }
    
    def _analyze_economic_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze economic equity (income, poverty, energy burden)"""
        
        # Income-based equity analysis
        income_correlation = np.corrcoef(-df['median_income'], df['allocation_per_capita'])[0, 1]  # Negative because lower income should get more
        
        # Create income quintiles
        df['income_quintile'] = pd.qcut(df['median_income'], 5, labels=['Q1-Low', 'Q2', 'Q3', 'Q4', 'Q5-High'])
        
        income_quintile_analysis = df.groupby('income_quintile', observed=True).agg({
            'allocation_per_capita': 'mean',
            'median_income': 'mean',
            'energy_burden_pct': 'mean'
        }).reset_index()
        
        # Poverty-based equity
        poverty_correlation = np.corrcoef(df['poverty_rate'], df['allocation_per_capita'])[0, 1]
        
        # Energy burden equity
        energy_burden_correlation = np.corrcoef(df['energy_burden_pct'], df['allocation_per_capita'])[0, 1]
        
        # Targeting efficiency - how well allocations target those most in need
        targeting_efficiency = self._calculate_targeting_efficiency(df)
        
        return {
            'income_equity': {
                'income_allocation_correlation': income_correlation,
                'income_quintile_analysis': income_quintile_analysis.to_dict('records'),
                'low_income_advantage': df[df['income_quintile'] == 'Q1-Low']['allocation_per_capita'].mean() / 
                                       df[df['income_quintile'] == 'Q5-High']['allocation_per_capita'].mean()
            },
            'poverty_equity': {
                'poverty_allocation_correlation': poverty_correlation,
                'high_poverty_advantage': df[df['poverty_rate'] > df['poverty_rate'].median()]['allocation_per_capita'].mean() / 
                                         df[df['poverty_rate'] <= df['poverty_rate'].median()]['allocation_per_capita'].mean()
            },
            'energy_burden_equity': {
                'energy_burden_correlation': energy_burden_correlation,
                'high_burden_advantage': df[df['energy_burden_pct'] > df['energy_burden_pct'].median()]['allocation_per_capita'].mean() / 
                                        df[df['energy_burden_pct'] <= df['energy_burden_pct'].median()]['allocation_per_capita'].mean()
            },
            'targeting_efficiency': targeting_efficiency
        }
    
    def _analyze_performance_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze equity in performance-based allocations"""
        
        # Performance score equity
        performance_correlation = np.corrcoef(df['compliance_score'], df['final_allocation'])[0, 1]
        utilization_correlation = np.corrcoef(df['utilization_rate'], df['final_allocation'])[0, 1]
        
        # High vs low performers
        high_performers = df[df['compliance_score'] > df['compliance_score'].median()]
        low_performers = df[df['compliance_score'] <= df['compliance_score'].median()]
        
        performance_ratio = high_performers['final_allocation'].mean() / low_performers['final_allocation'].mean()
        
        return {
            'compliance_equity': {
                'compliance_allocation_correlation': performance_correlation,
                'high_performer_advantage': performance_ratio
            },
            'utilization_equity': {
                'utilization_allocation_correlation': utilization_correlation,
                'high_utilization_advantage': df[df['utilization_rate'] > df['utilization_rate'].median()]['final_allocation'].mean() / 
                                             df[df['utilization_rate'] <= df['utilization_rate'].median()]['final_allocation'].mean()
            }
        }
    
    def _analyze_horizontal_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze horizontal equity (equal treatment of equals)"""
        
        # Group regions by similar characteristics
        df['similar_group'] = pd.cut(df['median_income'], bins=3, labels=['Low_Income', 'Medium_Income', 'High_Income'])
        
        # Calculate within-group variation
        horizontal_equity_metrics = {}
        
        for group in df['similar_group'].unique():
            if pd.notna(group):
                group_data = df[df['similar_group'] == group]
                if len(group_data) > 1:
                    cv = group_data['allocation_per_capita'].std() / group_data['allocation_per_capita'].mean()
                    horizontal_equity_metrics[group] = {
                        'coefficient_variation': cv,
                        'min_allocation': group_data['allocation_per_capita'].min(),
                        'max_allocation': group_data['allocation_per_capita'].max(),
                        'range_ratio': group_data['allocation_per_capita'].max() / group_data['allocation_per_capita'].min()
                    }
        
        # Overall horizontal equity
        overall_horizontal_cv = df.groupby('similar_group', observed=True)['allocation_per_capita'].mean().std() / df.groupby('similar_group')['allocation_per_capita'].mean().mean()
        
        return {
            'within_group_variation': horizontal_equity_metrics,
            'overall_horizontal_equity': overall_horizontal_cv
        }
    
    def _analyze_vertical_equity(self, df: pd.DataFrame) -> Dict:
        """Analyze vertical equity (appropriate differentiation)"""
        
        # Vertical equity should show appropriate differences based on need
        
        # Income-based vertical equity
        low_income_allocation = df[df['income_quintile'] == 'Q1-Low']['allocation_per_capita'].mean()
        high_income_allocation = df[df['income_quintile'] == 'Q5-High']['allocation_per_capita'].mean()
        income_vertical_equity = low_income_allocation / high_income_allocation if high_income_allocation > 0 else 1
        
        # Need-based vertical equity
        high_need_allocation = df[df['energy_burden_pct'] > df['energy_burden_pct'].quantile(0.8)]['allocation_per_capita'].mean()
        low_need_allocation = df[df['energy_burden_pct'] < df['energy_burden_pct'].quantile(0.2)]['allocation_per_capita'].mean()
        need_vertical_equity = high_need_allocation / low_need_allocation if low_need_allocation > 0 else 1
        
        return {
            'income_vertical_equity': income_vertical_equity,
            'need_vertical_equity': need_vertical_equity,
            'vertical_equity_score': (income_vertical_equity + need_vertical_equity) / 2
        }
    
    def _calculate_equity_indices(self, df: pd.DataFrame) -> Dict:
        """Calculate various equity indices"""
        
        # Gini coefficient
        gini = self._calculate_gini_coefficient(df['final_allocation'])
        
        # Theil index
        theil = self._calculate_theil_index(df['final_allocation'])
        
        # Atkinson index
        atkinson = self._calculate_atkinson_index(df['final_allocation'], epsilon=0.5)
        
        # Hoover index (Robin Hood index)
        hoover = self._calculate_hoover_index(df['final_allocation'])
        
        return {
            'gini_coefficient': gini,
            'theil_index': theil,
            'atkinson_index': atkinson,
            'hoover_index': hoover
        }
    
    def _assess_against_targets(self, df: pd.DataFrame) -> Dict:
        """Assess equity metrics against targets"""
        
        targets = self.equity_targets
        
        # Calculate coefficient of variation
        cv = df['final_allocation'].std() / df['final_allocation'].mean()
        
        # Calculate Gini coefficient
        gini = self._calculate_gini_coefficient(df['final_allocation'])
        
        # Urban/rural ratio
        urban_avg = df[df['area_type'] == 'Urban']['allocation_per_capita'].mean()
        rural_avg = df[df['area_type'] == 'Rural']['allocation_per_capita'].mean()
        urban_rural_ratio = urban_avg / rural_avg if rural_avg > 0 else 1
        
        # Geographic equity (correlation between population and allocation shares)
        population_shares = df['total_population'] / df['total_population'].sum()
        allocation_shares = df['final_allocation'] / df['final_allocation'].sum()
        geographic_correlation = np.corrcoef(population_shares, allocation_shares)[0, 1]
        
        return {
            'coefficient_variation': {
                'current': cv,
                'target': targets.get('coefficient_variation_max', 0.30),
                'meets_target': cv <= targets.get('coefficient_variation_max', 0.30),
                'gap': cv - targets.get('coefficient_variation_max', 0.30)
            },
            'gini_coefficient': {
                'current': gini,
                'target': targets.get('gini_coefficient_max', 0.35),
                'meets_target': gini <= targets.get('gini_coefficient_max', 0.35),
                'gap': gini - targets.get('gini_coefficient_max', 0.35)
            },
            'urban_rural_ratio': {
                'current': urban_rural_ratio,
                'target': targets.get('urban_rural_ratio_max', 2.0),
                'meets_target': urban_rural_ratio <= targets.get('urban_rural_ratio_max', 2.0),
                'gap': max(0, urban_rural_ratio - targets.get('urban_rural_ratio_max', 2.0))
            },
            'geographic_equity': {
                'current': geographic_correlation,
                'target': targets.get('geographic_equity_min', 0.90),
                'meets_target': geographic_correlation >= targets.get('geographic_equity_min', 0.90),
                'gap': targets.get('geographic_equity_min', 0.90) - geographic_correlation
            }
        }
    
    def _calculate_gini_coefficient(self, allocations: pd.Series) -> float:
        """Calculate Gini coefficient"""
        allocations = allocations.sort_values()
        n = len(allocations)
        cumsum = allocations.cumsum()
        return (2 * np.sum((np.arange(1, n+1) * allocations) - cumsum)) / (n * allocations.sum()) if allocations.sum() > 0 else 0
    
    def _calculate_theil_index(self, allocations: pd.Series) -> float:
        """Calculate Theil index"""
        mean_allocation = allocations.mean()
        if mean_allocation <= 0:
            return 0
        
        relative_allocations = allocations / mean_allocation
        theil = np.mean(relative_allocations * np.log(relative_allocations))
        return theil if not np.isnan(theil) else 0
    
    def _calculate_atkinson_index(self, allocations: pd.Series, epsilon: float = 0.5) -> float:
        """Calculate Atkinson index"""
        if allocations.sum() <= 0:
            return 0
        
        mean_allocation = allocations.mean()
        geometric_mean = np.exp(np.mean(np.log(allocations + 1e-10)))  # Add small value to avoid log(0)
        atkinson = 1 - (geometric_mean / mean_allocation) ** epsilon
        return max(0, atkinson)
    
    def _calculate_hoover_index(self, allocations: pd.Series) -> float:
        """Calculate Hoover index (Robin Hood index)"""
        total_allocation = allocations.sum()
        if total_allocation <= 0:
            return 0
        
        population_shares = np.ones(len(allocations)) / len(allocations)  # Equal population shares
        allocation_shares = allocations / total_allocation
        
        hoover = 0.5 * np.sum(np.abs(population_shares - allocation_shares))
        return hoover
    
    def _calculate_morans_i(self, df: pd.DataFrame) -> float:
        """Calculate Moran's I for spatial autocorrelation (simplified)"""
        # Simplified spatial autocorrelation assuming regions are ordered geographically
        allocations = df['allocation_per_capita'].values
        n = len(allocations)
        
        # Create simple adjacency matrix (regions next to each other)
        spatial_lag = np.zeros(n)
        for i in range(n):
            neighbors = []
            if i > 0:
                neighbors.append(allocations[i-1])
            if i < n-1:
                neighbors.append(allocations[i+1])
            spatial_lag[i] = np.mean(neighbors) if neighbors else allocations[i]
        
        # Calculate Moran's I
        mean_allocation = np.mean(allocations)
        numerator = np.sum((allocations - mean_allocation) * (spatial_lag - mean_allocation))
        denominator = np.sum((allocations - mean_allocation) ** 2)
        
        morans_i = numerator / denominator if denominator > 0 else 0
        return morans_i
    
    def _calculate_progressivity_index(self, df: pd.DataFrame) -> float:
        """Calculate progressivity index for vulnerable populations"""
        # Compare allocation share to population share for vulnerable groups
        
        df_sorted = df.sort_values('vulnerable_pct')
        cumulative_population = df_sorted['total_population'].cumsum() / df_sorted['total_population'].sum()
        cumulative_allocation = df_sorted['final_allocation'].cumsum() / df_sorted['final_allocation'].sum()
        
        # Area between Lorenz curve and equality line
        progressivity = 1 - 2 * np.sum(cumulative_allocation) / len(df) + 1/len(df)
        return progressivity
    
    def _calculate_targeting_efficiency(self, df: pd.DataFrame) -> Dict:
        """Calculate targeting efficiency metrics"""
        
        # Define target groups based on need indicators
        high_need_mask = (df['energy_burden_pct'] > df['energy_burden_pct'].median()) | \
                        (df['poverty_rate'] > df['poverty_rate'].median()) | \
                        (df['median_income'] < df['median_income'].median())
        
        target_group = df[high_need_mask]
        non_target_group = df[~high_need_mask]
        
        # Coverage rate
        coverage_rate = len(target_group[target_group['final_allocation'] > 0]) / len(target_group)
        
        # Leakage rate (benefits going to non-target groups)
        leakage_rate = non_target_group['final_allocation'].sum() / df['final_allocation'].sum()
        
        # Benefit incidence
        target_benefit_share = target_group['final_allocation'].sum() / df['final_allocation'].sum()
        target_population_share = len(target_group) / len(df)
        benefit_incidence = target_benefit_share / target_population_share if target_population_share > 0 else 0
        
        return {
            'coverage_rate': coverage_rate,
            'leakage_rate': leakage_rate,
            'benefit_incidence': benefit_incidence,
            'targeting_accuracy': coverage_rate * (1 - leakage_rate)
        }
    
    def generate_equity_report(self, allocation_df: pd.DataFrame, 
                             master_df: pd.DataFrame) -> Dict:
        """Generate comprehensive equity report"""
        
        analysis = self.comprehensive_equity_analysis(allocation_df, master_df)
        
        report = {
            'generated_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'overall_equity_score': self._calculate_overall_equity_score(analysis),
                'equity_strengths': self._identify_equity_strengths(analysis),
                'equity_concerns': self._identify_equity_concerns(analysis),
                'priority_improvements': self._identify_priority_improvements(analysis)
            },
            'detailed_analysis': analysis
        }
        
        return report
    
    def _calculate_overall_equity_score(self, analysis: Dict) -> float:
        """Calculate overall equity score"""
        
        # Weight different equity dimensions
        weights = {
            'geographic': 0.25,
            'demographic': 0.25,
            'economic': 0.30,
            'performance': 0.20
        }
        
        # Calculate component scores (higher is better)
        geographic_score = 1 - min(1, analysis['geographic_equity']['regional_disparity']['coefficient_variation'])
        demographic_score = analysis['demographic_equity']['vulnerable_population_equity']['progressivity_index']
        economic_score = analysis['economic_equity']['income_equity']['low_income_advantage']
        performance_score = 1 - abs(analysis['performance_equity']['compliance_equity']['compliance_allocation_correlation'] - 0.5) * 2
        
        overall_score = (
            geographic_score * weights['geographic'] +
            demographic_score * weights['demographic'] +
            economic_score * weights['economic'] +
            performance_score * weights['performance']
        )
        
        return overall_score
    
    def _identify_equity_strengths(self, analysis: Dict) -> List[str]:
        """Identify equity strengths"""
        
        strengths = []
        
        if analysis['geographic_equity']['urban_rural_analysis']['urban_rural_ratio'] < 1.5:
            strengths.append("Balanced urban-rural allocation")
        
        if analysis['economic_equity']['income_equity']['low_income_advantage'] > 1.2:
            strengths.append("Strong targeting of low-income populations")
        
        if analysis['demographic_equity']['vulnerable_population_equity']['progressivity_index'] > 0.3:
            strengths.append("Progressive allocation to vulnerable populations")
        
        return strengths
    
    def _identify_equity_concerns(self, analysis: Dict) -> List[str]:
        """Identify equity concerns"""
        
        concerns = []
        
        if analysis['geographic_equity']['regional_disparity']['coefficient_variation'] > 0.30:
            concerns.append("High regional allocation variation")
        
        if analysis['equity_indices']['gini_coefficient'] > 0.35:
            concerns.append("High overall inequality (Gini coefficient)")
        
        if analysis['performance_equity']['compliance_equity']['high_performer_advantage'] > 1.3:
            concerns.append("Over-emphasis on performance may disadvantage high-need areas")
        
        return concerns
    
    def _identify_priority_improvements(self, analysis: Dict) -> List[str]:
        """Identify priority areas for improvement"""
        
        improvements = []
        
        # Find the worst-performing equity dimension
        scores = {
            'Geographic Equity': 1 - min(1, analysis['geographic_equity']['regional_disparity']['coefficient_variation']),
            'Demographic Equity': analysis['demographic_equity']['vulnerable_population_equity']['progressivity_index'],
            'Economic Equity': analysis['economic_equity']['income_equity']['low_income_advantage'],
            'Performance Equity': 1 - abs(analysis['performance_equity']['compliance_equity']['compliance_allocation_correlation'] - 0.5) * 2
        }
        
        min_score_dimension = min(scores, key=scores.get)
        improvements.append(f"Improve {min_score_dimension}")
        
        return improvements
