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
  - Automatically executed via GitHub Actions CI
- **Jupiter.ipynb**: Additional data analysis and visualizations (includes birth month distribution analysis)
- **cars.csv**: Sample dataset containing car information (make, model, year, price, mileage, fuel_type)
- **Fuelio_sample.csv**: Sample Fuelio fuel consumption data for testing and CI execution
- **requirements.txt**: Python dependencies required to run the notebooks
- **CarAnalysis_database/**: Git submodule containing the CarAnalysis database (from [CarAnalysis_database](https://github.com/marcorimo88/CarAnalysis_database) repository)

## Requirements

- Python 3.x
- Jupyter Notebook or JupyterLab
- Required Python packages:
  - pandas
  - numpy
  - matplotlib
  - seaborn

## Installation

1. Clone this repository with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/marcorimo88/CarAnalysis.git
   cd CarAnalysis
   ```
   
   If you've already cloned without submodules, initialize them:
   ```bash
   git submodule update --init --recursive
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
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

## Continuous Integration (CI)

This repository includes a GitHub Actions workflow that automatically:
1. Executes the Fuelio.ipynb notebook on every push to main/master branches
2. Generates all visualization plots (odometer trends, monthly averages, price distributions, etc.)
3. Saves the generated plots to a separate `plots` branch
4. Maintains a history of plot updates over time

### Generated Plots

The CI workflow generates the following plots in the `plots` branch:
- `odometer_vs_date.png` - Odometer reading over time
- `avg_km_per_month.png` - Average kilometers per month with min/max range
- `monthly_distance_histogram.png` - Histogram of monthly distances by year
- `avg_km_violin_plot.png` - Violin plot of average km/month distribution by year
- `avg_km_boxplot.png` - Boxplot of average km/month by year
- `price_boxplot.png` - Boxplot of fuel prices by year

To view the latest plots, check out the `plots` branch or view them on GitHub.

### Using Custom Data

To use your own Fuelio data:
1. Export your data from the Fuelio app
2. Set the environment variable `FUELIO_CSV_PATH` to point to your CSV file
3. Run the notebook: `jupyter notebook Fuelio.ipynb`

The notebook will automatically use `Fuelio_sample.csv` if no custom path is provided.

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.