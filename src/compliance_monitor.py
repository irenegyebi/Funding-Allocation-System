"""
Compliance Monitoring Module
Tracks regulatory compliance, audit findings, and performance metrics
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging


class ComplianceMonitor:
    """Monitors compliance with federal and state regulations"""
    
    def __init__(self, config_path="config/config.yaml"):
        self.config = self._load_config(config_path)
        self.performance_targets = self.config.get('performance', {})
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
    
    def assess_compliance_status(self, compliance_df: pd.DataFrame, 
                               allocation_df: pd.DataFrame = None) -> Dict:
        """
        Comprehensive compliance assessment
        
        Args:
            compliance_df: Compliance and audit data
            allocation_df: Allocation results (optional)
            
        Returns:
            Dictionary with compliance status and metrics
        """
        
        assessment = {
            'overall_compliance_score': self._calculate_overall_compliance(compliance_df),
            'regional_compliance': self._assess_regional_compliance(compliance_df),
            'performance_metrics': self._assess_performance_metrics(compliance_df),
            'audit_findings': self._analyze_audit_findings(compliance_df),
            'corrective_actions': self._track_corrective_actions(compliance_df),
            'risk_assessment': self._assess_compliance_risks(compliance_df),
            'trends': self._analyze_compliance_trends(compliance_df)
        }
        
        if allocation_df is not None:
            assessment['equity_compliance'] = self._assess_equity_compliance(allocation_df)
        
        return assessment
    
    def _calculate_overall_compliance(self, compliance_df: pd.DataFrame) -> Dict:
        """Calculate overall compliance score"""
        
        # Weight different compliance components
        weights = {
            'documentation': 0.25,
            'eligibility': 0.30,
            'calculation': 0.25,
            'reporting': 0.20
        }
        
        # Calculate weighted average
        overall_score = (
            compliance_df['documentation_score'].mean() * weights['documentation'] +
            compliance_df['eligibility_score'].mean() * weights['eligibility'] +
            compliance_df['calculation_score'].mean() * weights['calculation']
        )
        
        # Assume reporting score based on overall trends
        reporting_score = min(1.0, overall_score * 1.1)
        overall_score = overall_score + reporting_score * weights['reporting']
        
        return {
            'overall_score': overall_score,
            'compliance_status': 'Compliant' if overall_score >= 0.90 else 'Needs Improvement',
            'documentation_score': compliance_df['documentation_score'].mean(),
            'eligibility_score': compliance_df['eligibility_score'].mean(),
            'calculation_score': compliance_df['calculation_score'].mean(),
            'reporting_score': reporting_score
        }
    
    def _assess_regional_compliance(self, compliance_df: pd.DataFrame) -> pd.DataFrame:
        """Assess compliance by region"""
        
        regional_compliance = compliance_df.groupby('region_name').agg({
            'overall_score': 'mean',
            'documentation_score': 'mean',
            'eligibility_score': 'mean',
            'calculation_score': 'mean',
            'num_findings': 'sum',
            'corrective_actions_due': 'sum'
        }).reset_index()
        
        # Add compliance status
        regional_compliance['compliance_status'] = regional_compliance['overall_score'].apply(
            lambda x: 'Compliant' if x >= 0.90 else 'Needs Improvement' if x >= 0.80 else 'At Risk'
        )
        
        # Add risk level
        regional_compliance['risk_level'] = regional_compliance.apply(
            lambda row: self._assess_regional_risk(row), axis=1
        )
        
        return regional_compliance
    
    def _assess_regional_risk(self, row: pd.Series) -> str:
        """Assess risk level for a region"""
        score = row['overall_score']
        findings = row['num_findings']
        
        if score >= 0.95 and findings == 0:
            return 'Low'
        elif score >= 0.90 and findings <= 2:
            return 'Medium'
        elif score >= 0.80 and findings <= 5:
            return 'High'
        else:
            return 'Critical'
    
    def _assess_performance_metrics(self, compliance_df: pd.DataFrame) -> Dict:
        """Assess performance against targets"""
        
        # Calculate current performance metrics
        current_metrics = {
            'compliance_target': compliance_df['overall_score'].mean(),
            'utilization_target': compliance_df.get('utilization_rate', pd.Series([0.9] * len(compliance_df))).mean(),
            'error_rate': 1 - compliance_df['calculation_score'].mean(),  # Proxy for error rate
            'audit_score': compliance_df['overall_score'].mean() * 100
        }
        
        # Compare against targets
        targets = self.performance_targets
        
        performance_assessment = {}
        
        for metric, current_value in current_metrics.items():
            target_key = f"{metric}_target" if metric != 'compliance_target' else 'compliance_target'
            target_value = targets.get(target_key, 0.90)
            
            if metric == 'error_rate':
                # Lower is better for error rate
                meets_target = current_value <= target_value
                variance = (current_value - target_value) / target_value if target_value > 0 else 0
            else:
                # Higher is better for other metrics
                meets_target = current_value >= target_value
                variance = (current_value - target_value) / target_value if target_value > 0 else 0
            
            performance_assessment[metric] = {
                'current_value': current_value,
                'target_value': target_value,
                'meets_target': meets_target,
                'variance_pct': variance * 100,
                'status': 'Meets Target' if meets_target else 'Below Target'
            }
        
        return performance_assessment
    
    def _analyze_audit_findings(self, compliance_df: pd.DataFrame) -> Dict:
        """Analyze audit findings and patterns"""
        
        # Total findings
        total_findings = compliance_df['num_findings'].sum()
        
        # Findings by category
        all_findings = []
        for findings in compliance_df['findings']:
            if pd.notna(findings) and str(findings).strip() != '':
                all_findings.extend([f.strip() for f in str(findings).split('; ') if f.strip()!=''])
        
        findings_by_category = {}
        for finding in all_findings:
            if ':' in finding:
                category, priority = finding.split(':')
                category = category.strip()
                priority = priority.strip()
                
                if category not in findings_by_category:
                    findings_by_category[category] = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
                
                if priority in findings_by_category[category]:
                    findings_by_category[category][priority] += 1
        
        # Findings by severity
        severity_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for finding in all_findings:
            if ':' in finding:
                _, priority = finding.split(':', 1)
                priority = priority.strip()
                if priority in severity_counts:
                    severity_counts[priority] += 1
        
        return {
            'total_findings': total_findings,
            'findings_by_category': findings_by_category,
            'findings_by_severity': severity_counts,
            'avg_findings_per_audit': total_findings / len(compliance_df) if len(compliance_df) > 0 else 0,
            'regions_with_findings': (compliance_df['num_findings'] > 0).sum()
        }
    
    def _track_corrective_actions(self, compliance_df: pd.DataFrame) -> Dict:
        """Track status of corrective actions"""
        
        total_due = compliance_df['corrective_actions_due'].sum()
        
        # Simulate some completion tracking
        completed_actions = int(total_due * np.random.uniform(0.6, 0.9))
        overdue_actions = max(0, total_due - completed_actions)
        
        return {
            'total_actions_due': total_due,
            'completed_actions': completed_actions,
            'overdue_actions': overdue_actions,
            'completion_rate': completed_actions / total_due if total_due > 0 else 1.0,
            'avg_days_to_complete': np.random.uniform(25, 45)
        }
    
    def _assess_compliance_risks(self, compliance_df: pd.DataFrame) -> Dict:
        """Assess compliance risks and vulnerabilities"""
        
        # Risk factors
        low_scoring_regions = (compliance_df['overall_score'] < 0.85).sum()
        high_findings_regions = (compliance_df['num_findings'] > 3).sum()
        overdue_actions = compliance_df['corrective_actions_due'].sum()
        
        # Calculate risk score
        risk_score = (
            (low_scoring_regions / len(compliance_df)) * 0.4 +
            (high_findings_regions / len(compliance_df)) * 0.3 +
            min(overdue_actions / 20, 1.0) * 0.3
        )
        
        # Risk categories
        risk_categories = {
            'Documentation Risk': {
                'score': 1 - compliance_df['documentation_score'].mean(),
                'description': 'Risk related to record-keeping and documentation'
            },
            'Eligibility Risk': {
                'score': 1 - compliance_df['eligibility_score'].mean(),
                'description': 'Risk related to eligibility determinations'
            },
            'Calculation Risk': {
                'score': 1 - compliance_df['calculation_score'].mean(),
                'description': 'Risk related to benefit calculations'
            },
            'Reporting Risk': {
                'score': np.random.uniform(0.05, 0.25),  # Simulated
                'description': 'Risk related to timely and accurate reporting'
            }
        }
        
        return {
            'overall_risk_score': risk_score,
            'risk_level': 'High' if risk_score > 0.3 else 'Medium' if risk_score > 0.15 else 'Low',
            'risk_categories': risk_categories,
            'priority_areas': self._identify_priority_areas(compliance_df)
        }
    
    def _identify_priority_areas(self, compliance_df: pd.DataFrame) -> List[str]:
        """Identify priority areas for improvement"""
        
        priority_areas = []
        
        # Analyze which areas need most attention
        scores = {
            'Documentation': compliance_df['documentation_score'].mean(),
            'Eligibility': compliance_df['eligibility_score'].mean(),
            'Calculation': compliance_df['calculation_score'].mean()
        }
        
        # Find lowest scoring areas
        min_score = min(scores.values())
        for area, score in scores.items():
            if score < 0.90 or score == min_score:
                priority_areas.append(area)
        
        return priority_areas
    
    def _analyze_compliance_trends(self, compliance_df: pd.DataFrame) -> Dict:
        """Analyze compliance trends over time"""
        
        # Convert audit_date to datetime
        compliance_df['audit_date'] = pd.to_datetime(compliance_df['audit_date'])
        compliance_df['year_month'] = compliance_df['audit_date'].dt.to_period('M')
        
        # Monthly trends
        monthly_trends = compliance_df.groupby('year_month').agg({
            'overall_score': 'mean',
            'documentation_score': 'mean',
            'eligibility_score': 'mean',
            'calculation_score': 'mean',
            'num_findings': 'sum'
        }).reset_index()
        
        # Calculate trend direction
        recent_scores = monthly_trends['overall_score'].tail(3).mean()
        older_scores = monthly_trends['overall_score'].head(3).mean()
        
        trend_direction = 'Improving' if recent_scores > older_scores else 'Declining' if recent_scores < older_scores else 'Stable'
        
        return {
            'monthly_trends': monthly_trends,
            'trend_direction': trend_direction,
            'improvement_rate': (recent_scores - older_scores) / older_scores if older_scores > 0 else 0,
            'volatility': monthly_trends['overall_score'].std()
        }
    
    def _assess_equity_compliance(self, allocation_df: pd.DataFrame) -> Dict:
        """Assess compliance with equity requirements"""
        
        # Calculate equity metrics
        coefficient_variation = allocation_df['final_allocation'].std() / allocation_df['final_allocation'].mean()
        
        # Gini coefficient (simplified)
        allocations = allocation_df['final_allocation'].sort_values()
        n = len(allocations)
        cumsum = allocations.cumsum()
        gini_coefficient = (2 * np.sum((np.arange(1, n+1) * allocations) - cumsum)) / (n * allocations.sum()) if allocations.sum() > 0 else 0
        
        # Compare against targets
        targets = self.equity_targets
        
        equity_assessment = {
            'coefficient_variation': {
                'current': coefficient_variation,
                'target': targets.get('coefficient_variation_max', 0.30),
                'meets_target': coefficient_variation <= targets.get('coefficient_variation_max', 0.30)
            },
            'gini_coefficient': {
                'current': gini_coefficient,
                'target': targets.get('gini_coefficient_max', 0.35),
                'meets_target': gini_coefficient <= targets.get('gini_coefficient_max', 0.35)
            }
        }
        
        return equity_assessment
    
    def generate_compliance_report(self, compliance_df: pd.DataFrame,
                                 allocation_df: pd.DataFrame = None) -> Dict:
        """Generate comprehensive compliance report"""
        
        assessment = self.assess_compliance_status(compliance_df, allocation_df)
        
        report = {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'report_period': f"{compliance_df['audit_date'].min()} to {compliance_df['audit_date'].max()}",
            'summary': {
                'overall_compliance_score': assessment['overall_compliance_score']['overall_score'],
                'compliance_status': assessment['overall_compliance_score']['compliance_status'],
                'total_regions': len(compliance_df),
                'total_findings': assessment['audit_findings']['total_findings'],
                'risk_level': assessment['risk_assessment']['risk_level']
            },
            'detailed_assessment': assessment
        }
        
        return report
    
    def track_compliance_improvement(self, compliance_df: pd.DataFrame,
                                   action_plan: Dict) -> Dict:
        """Track progress on compliance improvement plans"""
        
        # Simulate progress tracking
        current_assessment = self.assess_compliance_status(compliance_df)
        
        progress = {
            'target_compliance_score': 0.95,
            'current_compliance_score': current_assessment['overall_compliance_score']['overall_score'],
            'progress_percentage': min(100, (current_assessment['overall_compliance_score']['overall_score'] / 0.95) * 100),
            'actions_completed': np.random.randint(5, 15),
            'actions_pending': np.random.randint(2, 8),
            'estimated_completion_date': (datetime.now() + timedelta(days=np.random.randint(60, 180))).strftime('%Y-%m-%d')
        }
        
        return progress
