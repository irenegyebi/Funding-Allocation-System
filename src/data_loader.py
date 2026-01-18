"""
Data Loader Module
Handles loading and validation of all data sources
"""

import pandas as pd
import numpy as np
import yaml
import os
from datetime import datetime
import logging

class DataLoader:
    """Loads and manages all system data sources"""
    
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
    
    def load_all_data(self):
        """Load all data sources"""
        try:
            master_df = self.load_master_data()
            historical_df = self.load_historical_data()
            compliance_df = self.load_compliance_data()
            energy_df = self.load_energy_data()
            
            return master_df, historical_df, compliance_df, energy_df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return self._load_mock_data()
    
    def load_master_data(self):
        """Load master demographic and program data"""
        data_path = self.config.get('sources', {}).get('demographics', 'data/master_input.csv')
        
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        else:
            return self._generate_mock_master_data()
    
    def load_historical_data(self):
        """Load historical allocation and performance data"""
        data_path = self.config.get('sources', {}).get('historical', 'data/historical_trends.csv')
        
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        else:
            return self._generate_mock_historical_data()
    
    def load_compliance_data(self):
        """Load compliance and audit data"""
        data_path = self.config.get('sources', {}).get('compliance', 'data/compliance_details.csv')
        
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        else:
            return self._generate_mock_compliance_data()
    
    def load_energy_data(self):
        """Load energy cost and burden data"""
        data_path = self.config.get('sources', {}).get('energy_costs', 'data/energy_costs.csv')
        
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        else:
            return self._generate_mock_energy_data()
    
    def _load_mock_data(self):
        """Generate all mock data when files don't exist"""
        return (
            self._generate_mock_master_data(),
            self._generate_mock_historical_data(),
            self._generate_mock_compliance_data(),
            self._generate_mock_energy_data()
        )
    
    def _generate_mock_master_data(self):
        """Generate realistic mock master data for 12 regions"""
        regions = [
            'Jefferson County', 'Madison County', 'Marshall County', 'Mobile County',
            'Montgomery County', 'Morgan County', 'Shelby County', 'Talladega County',
            'Tuscaloosa County', 'Baldwin County', 'Etowah County', 'Calhoun County'
        ]
        
        data = []
        for i, region in enumerate(regions):
            # Generate realistic demographic data
            total_population = np.random.randint(45000, 680000)
            low_income_population = int(total_population * np.random.uniform(0.12, 0.28))
            poverty_rate = np.random.uniform(0.08, 0.35)
            median_income = np.random.randint(28000, 55000)
            unemployment_rate = np.random.uniform(0.04, 0.18)
            
            # Energy burden data
            avg_monthly_bill = np.random.uniform(95, 185)
            energy_burden_pct = np.random.uniform(0.08, 0.32)
            
            # Vulnerable populations
            seniors_65_plus = int(total_population * np.random.uniform(0.12, 0.22))
            disabled_population = int(total_population * np.random.uniform(0.08, 0.15))
            children_under_18 = int(total_population * np.random.uniform(0.18, 0.28))
            
            # Program data
            households_served = np.random.randint(850, 4200)
            avg_benefit = np.random.uniform(285, 485)
            total_benefits = households_served * avg_benefit
            
            # Performance metrics
            compliance_score = np.random.uniform(0.82, 0.98)
            utilization_rate = np.random.uniform(0.75, 0.96)
            application_timeliness = np.random.uniform(0.88, 0.97)
            
            data.append({
                'region_id': f'REG_{i+1:03d}',
                'region_name': region,
                'total_population': total_population,
                'low_income_population': low_income_population,
                'poverty_rate': poverty_rate,
                'median_income': median_income,
                'unemployment_rate': unemployment_rate,
                'avg_monthly_bill': avg_monthly_bill,
                'energy_burden_pct': energy_burden_pct,
                'seniors_65_plus': seniors_65_plus,
                'disabled_population': disabled_population,
                'children_under_18': children_under_18,
                'households_served': households_served,
                'avg_benefit': avg_benefit,
                'total_benefits': total_benefits,
                'compliance_score': compliance_score,
                'utilization_rate': utilization_rate,
                'application_timeliness': application_timeliness
            })
        
        return pd.DataFrame(data)
    
    def _generate_mock_historical_data(self):
        """Generate historical trend data"""
        regions = [
            'Jefferson County', 'Madison County', 'Marshall County', 'Mobile County',
            'Montgomery County', 'Morgan County', 'Shelby County', 'Talladega County',
            'Tuscaloosa County', 'Baldwin County', 'Etowah County', 'Calhoun County'
        ]
        
        years = list(range(2020, 2026))
        data = []
        
        for region in regions:
            base_allocation = np.random.uniform(280000, 850000)
            base_households = np.random.randint(750, 3800)
            
            for year in years:
                # Add realistic year-over-year variation
                allocation_variation = np.random.uniform(0.92, 1.12)
                households_variation = np.random.uniform(0.94, 1.08)
                
                allocation = base_allocation * allocation_variation * (1 + (year - 2020) * 0.03)
                households_served = int(base_households * households_variation * (1 + (year - 2020) * 0.05))
                
                data.append({
                    'year': year,
                    'region_name': region,
                    'allocation_amount': allocation,
                    'households_served': households_served,
                    'avg_benefit': allocation / households_served if households_served > 0 else 0,
                    'funding_utilization': np.random.uniform(0.78, 0.98),
                    'compliance_score': np.random.uniform(0.80, 0.97)
                })
        
        return pd.DataFrame(data)
    
    def _generate_mock_compliance_data(self):
        """Generate compliance and audit data"""
        regions = [
            'Jefferson County', 'Madison County', 'Marshall County', 'Mobile County',
            'Montgomery County', 'Morgan County', 'Shelby County', 'Talladega County',
            'Tuscaloosa County', 'Baldwin County', 'Etowah County', 'Calhoun County'
        ]
        
        audit_types = ['Program', 'Financial', 'Compliance', 'Quality Control']
        findings_categories = ['Documentation', 'Eligibility', 'Benefit Calculation', 'Reporting', 'Timeliness']
        
        data = []
        for region in regions:
            # Generate multiple audit records per region
            num_audits = np.random.randint(2, 6)
            
            for _ in range(num_audits):
                audit_date = datetime(2024, np.random.randint(1, 13), np.random.randint(1, 29))
                audit_type = np.random.choice(audit_types)
                
                # Generate compliance scores
                overall_score = np.random.uniform(0.80, 0.98)
                documentation_score = np.random.uniform(0.75, 1.00)
                eligibility_score = np.random.uniform(0.82, 1.00)
                calculation_score = np.random.uniform(0.78, 1.00)
                
                # Generate findings
                num_findings = np.random.randint(0, 4)
                findings = []
                
                for _ in range(num_findings):
                    category = np.random.choice(findings_categories)
                    severity = np.random.choice(['Low', 'Medium', 'High', 'Critical'])
                    findings.append(f"{category}: {severity} priority")
                
                data.append({
                    'region_name': region,
                    'audit_date': audit_date.strftime('%Y-%m-%d'),
                    'audit_type': audit_type,
                    'overall_score': overall_score,
                    'documentation_score': documentation_score,
                    'eligibility_score': eligibility_score,
                    'calculation_score': calculation_score,
                    'num_findings': num_findings,
                    'findings': '; '.join(findings) if findings else 'None',
                    'corrective_actions_due': np.random.randint(0, 6) if findings else 0,
                    'status': np.random.choice(['Pass', 'Pass with Conditions', 'Fail'])
                })
        
        return pd.DataFrame(data)
    
    def _generate_mock_energy_data(self):
        """Generate energy cost and consumption data"""
        regions = [
            'Jefferson County', 'Madison County', 'Marshall County', 'Mobile County',
            'Montgomery County', 'Morgan County', 'Shelby County', 'Talladega County',
            'Tuscaloosa County', 'Baldwin County', 'Etowah County', 'Calhoun County'
        ]
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = []
        
        for region in regions:
            base_elec_cost = np.random.uniform(0.10, 0.16)  # $/kWh
            base_gas_cost = np.random.uniform(0.85, 1.25)   # $/therm
            
            for month in months:
                # Seasonal variations
                if month in ['Dec', 'Jan', 'Feb']:
                    elec_multiplier = 1.3
                    gas_multiplier = 1.8
                    consumption_mult = 1.4
                elif month in ['Jun', 'Jul', 'Aug']:
                    elec_multiplier = 1.6
                    gas_multiplier = 0.4
                    consumption_mult = 1.3
                else:
                    elec_multiplier = 1.0
                    gas_multiplier = 1.0
                    consumption_mult = 1.0
                
                elec_cost = base_elec_cost * elec_multiplier
                gas_cost = base_gas_cost * gas_multiplier
                avg_consumption = np.random.uniform(850, 1450) * consumption_mult
                
                data.append({
                    'region_name': region,
                    'month': month,
                    'electricity_rate': elec_cost,
                    'gas_rate': gas_cost,
                    'avg_monthly_consumption_kwh': avg_consumption,
                    'avg_monthly_bill': avg_consumption * elec_cost,
                    'heating_degree_days': np.random.randint(200, 800) if month in ['Dec', 'Jan', 'Feb'] else np.random.randint(50, 300),
                    'cooling_degree_days': np.random.randint(300, 600) if month in ['Jun', 'Jul', 'Aug'] else np.random.randint(50, 200)
                })
        
        return pd.DataFrame(data)
    
    def validate_data_quality(self, df, source_name):
        """Validate data quality and log issues"""
        issues = []
        
        # Check for missing values
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 5:
            issues.append(f"High missing data: {missing_pct:.1f}%")
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate records: {duplicates}")
        
        # Check for outliers in key metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.1:  # More than 10% outliers
                issues.append(f"Outliers in {col}: {outliers} records")
        
        if issues:
            self.logger.warning(f"Data quality issues in {source_name}: {', '.join(issues)}")
        
        return len(issues) == 0
    
    def save_data_to_csv(self, master_df, historical_df, compliance_df, energy_df):
        """Save all data to CSV files for persistence"""
        data_dir = self.config.get('paths', {}).get('data', 'data/')
        os.makedirs(data_dir, exist_ok=True)
        
        master_df.to_csv(f"{data_dir}master_input.csv", index=False)
        historical_df.to_csv(f"{data_dir}historical_trends.csv", index=False)
        compliance_df.to_csv(f"{data_dir}compliance_details.csv", index=False)
        energy_df.to_csv(f"{data_dir}energy_costs.csv", index=False)
        
        self.logger.info(f"Data saved to {data_dir}")
