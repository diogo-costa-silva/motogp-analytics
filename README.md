# MotoGP Analytics Project

Data analytics project using MotoGP datasets from 1949-2022.

## Setup

This project uses UV for Python environment management.

### Prerequisites
- Python 3.11+
- UV (install from https://docs.astral.sh/uv/)

### Environment Setup

1. **Activate UV environment:**
   ```bash
   uv sync
   ```

2. **Start Jupyter:**
   ```bash
   uv run jupyter notebook
   ```
   or
   ```bash
   uv run jupyter lab
   ```

## Usage

1. **Data Download:** Run `notebooks/00_data_download.ipynb` to download datasets from GitHub
2. **Data Preview:** Run `notebooks/01_data_preview.ipynb` to explore and understand all datasets
3. **Data Understanding:** Individual analysis notebooks in `notebooks/02_data_understanding/` (coming soon)
4. **Data Location:** Downloaded files are saved to `data/raw/`

## Features

- **Separation of Concerns:** Clear separation between download, preview, and analysis phases
- **Dynamic URL Loading:** The download notebook reads URLs from `docs/data.txt`, making it easy to add new datasets
- **Interactive Preview:** Comprehensive data overview with statistics and sample data
- **Environment Isolation:** Uses UV for clean dependency management
- **Error Handling:** Basic error handling for network issues and file problems

## Adding New Datasets

Simply add new URLs to `docs/data.txt` (one per line) and re-run the download notebook.

## Project Structure

```
notebooks/
├── 00_data_download.ipynb     # Download datasets from GitHub
├── 01_data_preview.ipynb      # Interactive preview of all datasets
└── 02_data_understanding/     # Detailed analysis per dataset (future)
```