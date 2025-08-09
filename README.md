# MotoGP Analytics Project

A comprehensive data analysis project exploring MotoGP World Championship data from 1949 to 2022. This project provides insights into racing performance, constructor championships, rider statistics, and historical trends in motorcycle racing.

## 🚀 Key Components

- **📊 Analytics Notebooks**: 27 CRISP-DM structured notebooks for comprehensive analysis
- **🏗️ Database Infrastructure**: PostgreSQL schema with 13 tables and materialized views
- **🔌 REST API**: FastAPI application with comprehensive endpoints
- **📱 Interactive Demo**: Streamlit application for data visualization
- **💼 Business Intelligence**: Strategic recommendations and KPIs

## Data Source

Data sourced from [Kaggle MotoGP World Championship Dataset](https://www.kaggle.com/datasets/alrizacelk/moto-gp-world-championship19492022)

## Features

- 📊 Constructor championship analysis and dominance patterns
- 🏁 Race winner statistics and predictive modeling
- 👥 Rider performance analytics and career trajectory analysis
- 🌍 Geographic analysis and market expansion insights
- 🏁 Circuit intelligence and home advantage analysis
- 📈 Executive dashboards and strategic recommendations

## Dataset Overview

The project includes comprehensive MotoGP data with the following files:
- `constructure_world_championship.csv` - Constructor championship data
- `grand_prix_events_held.csv` - Grand Prix event information  
- `grand_prix_race_winners.csv` - Race winner records
- `riders_finishing_positions.csv` - Detailed finishing positions
- `riders_info.csv` - Rider biographical information
- `same_nation_podium_lockouts.csv` - National podium domination records

## Installation

### Using uv (recommended)
```bash
uv sync
```

### Using pip
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Analytics Notebooks
Explore comprehensive CRISP-DM analysis:
```bash
# Start Jupyter notebook server
uv run jupyter notebook

# Explore notebooks in structured phases:
# - 00_business_understanding/
# - 01_data_understanding/
# - 02_data_preparation/ 
# - 03_modeling/
# - 04_evaluation/
# - 05_deployment/
```

### 2. Interactive Demo App
Launch the Streamlit demonstration:
```bash
# Run interactive demo
uv run python apps/streamlit_demo/run_app.py

# Access at: http://localhost:8501
```

### 3. Database & API Setup
Set up the complete database infrastructure:
```bash
# Install dependencies and setup database
cd database/
python setup_database.py --sample-data

# Launch API server
uv run python api/main.py

# Access API docs at: http://localhost:8000/docs
```

## Requirements

- Python 3.11+
- pandas
- matplotlib
- seaborn
- numpy
- requests

## Project Structure

```
motogp-analytics/
├── apps/                   # Applications
│   └── streamlit_demo/     # Interactive Streamlit demo
├── data/                   # Data pipeline (follows industry standards)
│   ├── raw/               # Original CSV datasets (immutable)
│   ├── interim/           # Processed data from Phase 02 (CRISP-DM)
│   ├── processed/         # Final analysis-ready datasets
│   └── external/          # External data sources (future)
├── database/              # Database infrastructure
│   ├── api/               # FastAPI REST API
│   ├── etl/               # Data import scripts
│   ├── schema/            # PostgreSQL schema
│   └── setup_database.py  # Database setup
├── notebooks/             # CRISP-DM analysis (27 notebooks)
│   ├── 00_business_understanding/
│   ├── 01_data_understanding/
│   ├── 02_data_preparation/
│   ├── 03_modeling/
│   ├── 04_evaluation/
│   └── 05_deployment/
├── pyproject.toml         # UV project configuration
└── README.md             # This documentation
```

## Technology Stack

- **Data Analysis**: Python, Pandas, NumPy, Matplotlib, Seaborn
- **Database**: PostgreSQL with materialized views
- **API**: FastAPI with Pydantic models
- **Frontend**: Streamlit with Plotly visualizations  
- **Package Management**: UV (modern Python packaging)
- **Methodology**: CRISP-DM for systematic analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

