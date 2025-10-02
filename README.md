# Movie Database Analytics Project

## Description
Analysis of a movie database with visualizations and interactive reports.

## Structure
- `datasets/` — source CSV files
- `analytics.py` — 6 Plotly charts with Excel export
- `charts/` — saved charts
- `exports/` — Excel reports

## How to Run
1. Create database: `python db_create.py`
2. Create tables: `python tables_create.py`
3. Load data: `python data_import.py`
4. Run analysis: `python analytics.py`

## Requirements
Python 3.8+, PostgreSQL, libraries from `requirements.txt`