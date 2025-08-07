# MotoGP Analytics Project

A comprehensive data analysis project exploring MotoGP World Championship data from 1949 to 2022. This project provides insights into racing performance, constructor championships, rider statistics, and historical trends in motorcycle racing.

## Data Source

Data sourced from [Kaggle MotoGP World Championship Dataset](https://www.kaggle.com/datasets/alrizacelk/moto-gp-world-championship19492022)

## Features

- 📊 Constructor championship analysis
- 🏁 Race winner statistics and trends
- 👥 Rider performance and career analysis
- 🌍 National representation in podium finishes
- 📈 Historical data visualization and insights

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

## Usage

Explore the analysis through Jupyter notebooks:

```bash
# Start Jupyter notebook server
jupyter notebook

# Navigate to notebooks directory and open:
# - 00_data_download.ipynb - Data acquisition and preprocessing
# - 01_constructure_world_championship.ipynb - Constructor analysis
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
├── data/raw/           # Raw CSV data files
├── notebooks/          # Jupyter analysis notebooks
├── README.md          # Project documentation
├── requirements.txt   # Python dependencies
└── pyproject.toml    # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

