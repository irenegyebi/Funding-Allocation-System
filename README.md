# Funding Allocation System

## Energy Assistance Program - Enterprise Allocation Dashboard

**Version:** 3.0 Enterprise Edition  
**Last Updated:** December 2024  
**Technology Stack:** Python, Streamlit, Plotly, Pandas

---

## Overview

The Funding Allocation System is a comprehensive, enterprise-grade fund allocation platform designed for the Energy Assistance Program. The system uses advanced multi-criteria decision analysis to distribute $6.8M in federal funding across 12 regions based on need, performance, and equity considerations.

## Features

### 🏠 7 Interactive Dashboards

1. **Executive Command Center** - Strategic overview with KPIs and high-level insights
2. **Allocation Analysis** - Detailed methodology and regional breakdown
3. **Predictive Analytics** - Forecasting and scenario modeling
4. **Compliance Tracker** - Regulatory compliance monitoring
5. **Equity Analysis** - Comprehensive equity assessment
6. **Mobile Field View** - Touch-optimized interface for field workers
7. **Report Generator** - Automated report generation and export

### ⚖️ Advanced Allocation Algorithm

- **Multi-Criteria Decision Analysis** with weighted scoring
- **Need-based factors** (70% weight): Energy burden, income level, poverty rate, vulnerable populations
- **Performance-based factors** (30% weight): Utilization rate, compliance score
- **Constraint satisfaction** with floor (4%) and cap (22%) limits
- **Iterative redistribution** for optimal allocation

### 📊 Key Capabilities

- **Real-time data integration** with Census, EIA, and NOAA APIs
- **Scenario modeling** for different economic conditions
- **Monte Carlo simulation** for uncertainty analysis
- **Equity analysis** with Gini coefficient, coefficient of variation
- **Compliance monitoring** with audit tracking
- **Mobile-responsive design** for field accessibility
- **Automated reporting** with multiple export formats

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd funding_allocation_system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv/Scripts/activate # On MAC: source venv/bin/activate   
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the system:**
   ```bash
   cp config/config.yaml.template config/config.yaml
   # Edit config.yaml with your settings
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Configuration

### System Configuration (config/config.yaml)

Key configuration parameters:

```yaml
# Funding Parameters
funding:
  total_appropriation: 6800000  # $6.8M total funding
  reserve_percentage: 0.05      # 5% reserve
  minimum_floor: 0.04           # 4% minimum allocation
  maximum_cap: 0.22             # 22% maximum allocation

# Criteria Weights
weights:
  income_level: 0.25           # Lower income = higher need
  energy_burden: 0.30          # Primary mission indicator
  poverty_rate: 0.20           # Supplemental income validation
  prior_utilization: 0.15      # Program performance
  compliance_score: 0.10       # Accountability
  vulnerable_population: 0.05  # Seniors, disabled, children bonus
```

### API Configuration

Configure API keys for external data sources:

- **Census API**: demographic data
- **EIA API**: energy cost data
- **NOAA API**: weather data for energy burden calculations

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Navigation

Use the sidebar to navigate between different dashboard views:

- **Executive Command Center**: Strategic overview
- **Allocation Analysis**: Detailed methodology
- **Predictive Analytics**: Forecasting
- **Compliance Tracker**: Regulatory compliance
- **Equity Analysis**: Fairness assessment
- **Mobile Field View**: Mobile-optimized
- **Report Generator**: Export and automation

### Key Interactions

1. **Scenario Selection**: Choose from Base Case, Optimistic, Pessimistic, Equity-Focused, or Performance-Driven scenarios
2. **Date Range Filtering**: Select analysis period
3. **Region Selection**: Filter by specific regions
4. **Export Options**: Download data and reports in multiple formats

## Data Sources

The system integrates with multiple data sources:

1. **Master Demographic Data** (`data/master_input.csv`): Regional population, income, and demographic statistics
2. **Historical Trends** (`data/historical_trends.csv`): Historical allocation and performance data
3. **Compliance Details** (`data/compliance_details.csv`): Audit findings and compliance scores
4. **Energy Costs** (`data/energy_costs.csv`): Monthly energy cost and consumption data

### API Integrations

- **U.S. Census Bureau**: ACS 5-year estimates for demographic data
- **Energy Information Administration**: State energy profiles and costs
- **National Oceanic and Atmospheric Administration**: Degree-day data for energy burden calculations

## Architecture

### Directory Structure

```
funding_allocation_system/
├── app.py                    # Main Streamlit application
├── config/
│   └── config.yaml          # System configuration
├── src/                     # Core engine modules
│   ├── __init__.py
│   ├── allocation_engine.py # Core allocation algorithm
│   ├── data_loader.py       # Data loading and validation
│   ├── scenarios.py         # Scenario management
│   ├── compliance_monitor.py # Compliance tracking
│   └── equity_analyzer.py   # Equity analysis
├── dashboards/              # Dashboard modules
│   ├── __init__.py
│   ├── executive_overview.py
│   ├── allocation_analyzer.py
│   ├── predictive_forecast.py
│   ├── compliance_tracker.py
│   ├── equity_dashboard.py
│   ├── mobile_view.py
│   └── report_generator.py
├── data/                    # Data files
├── logs/                    # Application logs
├── reports/                 # Generated reports
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Core Components

1. **AllocationEngine**: Implements the weighted multi-criteria decision analysis
2. **DataLoader**: Handles data loading, validation, and mock data generation
3. **ScenarioManager**: Manages scenario modeling and sensitivity analysis
4. **ComplianceMonitor**: Tracks regulatory compliance and audit findings
5. **EquityAnalyzer**: Analyzes equity across geographic, demographic, and economic dimensions

## Methodology

### Multi-Criteria Decision Analysis

The allocation system uses a sophisticated weighted scoring approach:

1. **Normalization**: All criteria are normalized to 0-1 scale using z-score standardization
2. **Weighting**: Need-based factors (70%) and performance-based factors (30%)
3. **Composite Scoring**: Weighted sum of normalized criteria
4. **Proportional Allocation**: Funds distributed based on composite scores
5. **Constraint Satisfaction**: Floor and cap constraints with iterative redistribution

### Equity Analysis

Multiple equity dimensions are analyzed:

- **Geographic Equity**: Urban vs rural, regional disparities
- **Demographic Equity**: Vulnerable populations, seniors, disabled
- **Economic Equity**: Income-based, poverty-based targeting
- **Performance Equity**: Compliance-based, utilization-based

### Predictive Analytics

The system includes forecasting capabilities:

- **Demand Forecasting**: Linear and exponential smoothing models
- **Scenario Modeling**: Economic, funding, policy, and emergency scenarios
- **Monte Carlo Simulation**: Uncertainty analysis with confidence intervals
- **Risk Assessment**: Probability distributions and sensitivity analysis

## Compliance

### Federal Requirements

The system addresses key federal compliance areas:

- **LIHEAP Program Requirements**: 42 CFR 96.85
- **Equity Standards**: Coefficient of variation ≤ 0.30, Gini coefficient ≤ 0.35
- **Performance Targets**: 90% compliance score, 90% utilization rate
- **Audit Standards**: Documentation, eligibility, calculation, and reporting

### State Requirements

- **Alabama LIHEAP Guidelines**: State-specific allocation formulas
- **Reporting Standards**: Monthly, quarterly, and annual reports
- **Audit Trail**: Complete documentation of allocation decisions

## Security

### Data Protection

- **Encryption**: Data at rest and in transit
- **Access Control**: Role-based authentication and authorization
- **Audit Logging**: Complete activity logging for 7 years
- **Backup**: Daily automated backups with 30-day retention

### Compliance

- **FISMA**: Federal Information Security Management Act compliance
- **NIST**: National Institute of Standards and Technology guidelines
- **PII**: Personally Identifiable Information protection
- **HIPAA**: Health Insurance Portability and Accountability Act (where applicable)

## Performance

### Optimization Features

- **Caching**: Streamlit caching for data loading and calculations
- **Lazy Loading**: On-demand data loading for large datasets
- **Responsive Design**: Mobile-optimized interfaces
- **Progressive Enhancement**: Graceful degradation for older browsers

### Scalability

- **Horizontal Scaling**: Multi-instance deployment support
- **Load Balancing**: Traffic distribution across instances
- **Database Optimization**: Indexed queries and efficient data structures
- **Memory Management**: Optimized data structures and garbage collection

## Testing

### Test Coverage

- **Unit Tests**: Core algorithm testing with 80% coverage target
- **Integration Tests**: API and data integration testing
- **End-to-End Tests**: Full user workflow testing
- **Performance Tests**: Load and stress testing

### Quality Assurance

- **Code Review**: Peer review process for all changes
- **Static Analysis**: Linting and code quality tools
- **Security Scanning**: Vulnerability assessment
- **User Acceptance Testing**: Stakeholder validation

## Deployment

### Production Deployment

1. **Container Deployment**: Docker containers for consistency
2. **Cloud Hosting**: AWS, Azure, or Google Cloud Platform
3. **CI/CD Pipeline**: Automated deployment with testing
4. **Monitoring**: Application performance monitoring
5. **Disaster Recovery**: Backup and recovery procedures

### Development Environment

1. **Local Development**: Streamlit development server
2. **Staging Environment**: Pre-production testing
3. **Version Control**: Git with feature branch workflow
4. **Documentation**: Inline code documentation and user guides

## Support

### Documentation

- **User Guide**: Comprehensive user documentation
<!-- - **API Reference**: Technical API documentation
- **FAQ**: Frequently asked questions
- **Video Tutorials**: Step-by-step video guides -->

### Contact Information

- **Technical Support**: support@agcy.gov
- **Program Questions**: program@agcy.gov
- **Emergency Contact**: 1-770-HELP

### Version History

- **v3.0** (December 2024): Complete Python/Streamlit rewrite
- **v2.0** (June 2023): Enhanced equity analysis
- **v1.5** (January 2022): Mobile dashboard addition
- **v1.0** (October 2020): Initial system launch

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Commit changes**: `git commit -am 'Add new feature'`
4. **Push to branch**: `git push origin feature/new-feature`
5. **Submit pull request**

### Code Standards

- **PEP 8**: Python style guide compliance
- **Type Hints**: Function parameter and return type annotations
- **Documentation**: Docstrings for all public functions
- **Testing**: Unit tests for all new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **U.S. Department of Health and Human Services**: LIHEAP program guidance
- **Alabama Department of Economic and Community Affairs**: State program administration
- **Energy Information Administration**: Energy cost data
- **U.S. Census Bureau**: Demographic data

---

**Disclaimer**: This system is designed for the Alabama Low Income Energy Assistance Program. Other jurisdictions should adapt the configuration and methodology to meet their specific requirements and regulatory environment.
