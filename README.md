# CarAnalysis

A Python-based data analysis project for analyzing car data using Jupyter notebooks. This repository contains multiple notebooks for analyzing different aspects of car and fuel consumption data.

## Overview

This project provides tools to analyze:
- Car sales data (make, model, year, price, mileage, fuel type)
- Fuel consumption data from Fuelio app
- Statistical analysis and visualizations of car-related datasets

## Files

- **car_analysis.ipynb**: Basic car data analysis notebook that reads and analyzes car information from CSV files
- **Fuelio.ipynb**: Advanced fuel consumption analysis from Fuelio app data, including:
  - Odometer tracking over time
  - Monthly distance metrics calculation
  - Rolling averages (5-month window) for trend analysis
- **Jupiter.ipynb**: Additional data analysis and visualizations (includes birth month distribution analysis)
- **cars.csv**: Sample dataset containing car information (make, model, year, price, mileage, fuel_type)

## Requirements

- Python 3.x
- Jupyter Notebook or JupyterLab
- Required Python packages:
  - pandas
  - numpy
  - matplotlib
  - seaborn

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/marcorimo88/CarAnalysis.git
   cd CarAnalysis
   ```

2. Install required packages:
   ```bash
   pip install pandas numpy matplotlib seaborn jupyter
   ```

## Usage

1. Start Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

2. Open any of the notebooks:
   - `car_analysis.ipynb` - For basic car data analysis
   - `Fuelio.ipynb` - For fuel consumption analysis
   - `Jupiter.ipynb` - For additional analysis

3. Run the cells to see the analysis and visualizations

## Data Format

### cars.csv
Contains car information with the following columns:
- `make`: Car manufacturer
- `model`: Car model name
- `year`: Year of manufacture
- `price`: Price in dollars
- `mileage`: Mileage in miles/km
- `fuel_type`: Type of fuel (Gasoline, Electric, etc.)

### Fuelio Data
The Fuelio notebook expects CSV data with:
- `Date`: Date of fuel entry
- `Odo (km)`: Odometer reading in kilometers
- Additional fuel consumption metrics

## Features

- Load and inspect car datasets
- Calculate statistical summaries (mean, median, std deviation)
- Visualize data distributions using matplotlib and seaborn
- Analyze fuel consumption patterns
- Track monthly distance metrics with rolling averages
- Time-series analysis of odometer readings

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.