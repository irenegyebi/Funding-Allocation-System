"""
Compliance Tracker Dashboard
Monitors regulatory compliance and audit findings
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_compliance_dashboard(compliance_df, compliance_monitor):
    """Render the compliance tracker dashboard with parsed findings"""
    
    st.title("✅ Compliance Tracker")
    st.markdown("### Regulatory Compliance Monitoring")
    
    # Get compliance assessment
    assessment = compliance_monitor.assess_compliance_status(compliance_df)
    
    # Overall Compliance Score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_score = assessment['overall_compliance_score']['overall_score'] * 100
        st.metric("Overall Compliance", f"{overall_score:.1f}%", 
                 delta="+2.1% vs last quarter", delta_color="normal")
    
    with col2:
        total_findings = assessment['audit_findings']['total_findings']
        st.metric("Total Findings", total_findings, delta="-3 vs last quarter", delta_color="normal")
    
    with col3:
        risk_level = assessment['risk_assessment']['risk_level']
        color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
        st.metric("Risk Level", risk_level, delta_color="off")
    
    with col4:
        completion_rate = assessment['corrective_actions']['completion_rate'] * 100
        st.metric("Action Completion", f"{completion_rate:.1f}%", delta_color="off")
    
    # Compliance Trends Chart
    st.markdown("---")
    st.subheader("📈 Compliance Trends")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    compliance_trend = [88.2, 89.1, 90.3, 91.2, 90.8, 91.5, 92.1, 91.9, 92.4, 92.8, 92.6, 92.4]
    findings_trend = [15, 12, 18, 14, 16, 13, 11, 14, 12, 10, 13, 12]
    
    fig_trends = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Compliance Score Trend', 'Monthly Findings'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig_trends.add_trace(
        go.Scatter(x=months, y=compliance_trend, mode='lines+markers', name='Compliance %'),
        row=1, col=1
    )
    
    fig_trends.add_trace(
        go.Bar(x=months, y=findings_trend, name='Findings', marker_color='red'),
        row=1, col=2
    )
    
    fig_trends.add_hline(y=90, line_dash="dash", line_color="green", row=1, col=1)
    
    fig_trends.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_trends, width="stretch")
    
    # Regional Compliance Analysis
    st.markdown("---")
    st.subheader("🗺️ Regional Compliance Analysis")
    
    regional_compliance = assessment['regional_compliance']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_regional = px.bar(
            regional_compliance.sort_values('overall_score'),
            x='overall_score',
            y='region_name',
            orientation='h',
            title="Compliance Score by Region",
            labels={'overall_score': 'Compliance Score', 'region_name': 'Region'}
        )
        
        fig_regional.add_vline(x=0.90, line_dash="dash", line_color="red", annotation_text="Target")
        fig_regional.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_regional, width="stretch")
    
    with col2:
        st.dataframe(
            regional_compliance[['region_name', 'overall_score', 'num_findings', 'risk_level']],
            width="stretch",
            height=500
        )
    
    # --- Audit Findings Analysis ---
    st.markdown("---")
    st.subheader("🔍 Audit Findings Breakdown")
    
    # Parse free-text findings from compliance_df
    from collections import Counter
    
    category_counter = Counter()
    severity_counter = Counter()
    severities = ["Low", "Medium", "High", "Critical"]
    
    for row in compliance_df['findings']:
        if pd.isna(row) or str(row).lower() == "none":
            continue
        items = str(row).split(";")
        for item in items:
            if ":" not in item:
                continue
            category, severity = item.split(":", 1)
            category = category.strip()
            severity = severity.strip().replace(" priority", "")
            category_counter[category] += 1
            if severity in severities:
                severity_counter[severity] += 1
    
    category_counts = dict(category_counter)
    severity_counts = dict(severity_counter)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_findings = px.pie(
            values=list(category_counts.values()),
            names=list(category_counts.keys()),
            title="Findings by Category",
            hole=0.4
        )
        fig_findings.update_layout(height=400)
        st.plotly_chart(fig_findings, width="stretch")
    
    with col2:
        fig_severity = px.bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            title="Findings by Severity",
            color=list(severity_counts.keys()),
            color_discrete_map={
                'Low': '#10B981',
                'Medium': '#F59E0B',
                'High': '#EF4444',
                'Critical': '#7C2D12'
            }
        )
        fig_severity.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_severity, width="stretch")
    
    # Corrective Actions Tracking
    st.markdown("---")
    st.subheader("🛠️ Corrective Actions Tracking")
    
    actions = assessment['corrective_actions']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Actions Due", actions['total_actions_due'])
    
    with col2:
        st.metric("Completed", actions['completed_actions'], 
                 delta=f"{actions['completion_rate']*100:.1f}%")
    
    with col3:
        st.metric("Overdue", actions['overdue_actions'], delta_color="inverse")
    
    # Risk Assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")
    
    risks = assessment['risk_assessment']
    
    st.markdown(f"**Overall Risk Level: {risks['risk_level']}**")
    
    # Risk categories
    risk_categories = risks['risk_categories']
    
    for category, details in risk_categories.items():
        risk_score = details['score']
        color = "red" if risk_score > 0.3 else "orange" if risk_score > 0.15 else "green"
        st.markdown(f"""
        **{category}**
        - Risk Score: {risk_score:.2f} 
        - Description: {details['description']}
        """)
    
    # Priority Areas
    st.markdown("---")
    st.subheader("🎯 Priority Improvement Areas")
    
    priority_areas = risks['priority_areas']
    
    for i, area in enumerate(priority_areas, 1):
        st.markdown(f"{i}. **{area}** - Requires immediate attention")
    
    # Compliance Report Generation
    st.markdown("---")
    st.subheader("📋 Compliance Report")
    
    if st.button("Generate Comprehensive Compliance Report"):
        report = compliance_monitor.generate_compliance_report(compliance_df)
        
        st.json(report)
        
        # Export option
        csv_data = regional_compliance.to_csv(index=False)
        st.download_button(
            label="Download Regional Compliance Data",
            data=csv_data,
            file_name="regional_compliance_report.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.caption("Compliance Tracker Dashboard | Last Audit: December 2024 | Next Review: January 2025")
