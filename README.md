# CarAnalysis

A Python-based data analysis project for analyzing car data using Jupyter notebooks. This repository contains multiple notebooks for analyzing different aspects of car and fuel consumption data.

## Overview

This project provides tools to analyze:
- Car sales data (make, model, year, price, mileage, fuel type)
- Fuel consumption data from CarAnalysis app
- Statistical analysis and visualizations of car-related datasets

## Files

- **CarAnalysis.ipynb**: Comprehensive fuel consumption analysis from CarAnalysis app data, including:
  - Time-series analysis of odometer readings
  - Monthly distance metrics with 5-month rolling averages for trend analysis
  - Fuel consumption and pricing trend visualizations
  - Multiple statistical plots (histograms, boxplots, violin plots)
  - Automatically executed via GitHub Actions CI with plot generation
- **CarAnalysis_sample.csv**: Sample CarAnalysis fuel consumption data for testing and CI execution
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
   - `CarAnalysis.ipynb` - For fuel consumption analysis

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

### CarAnalysis Data
The CarAnalysis notebook expects CSV data with:
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
1. Executes the CarAnalysis.ipynb notebook on every push to main/master branches
2. Generates all visualization plots (odometer trends, monthly averages, price distributions, etc.)
3. Saves the generated plots to a separate `plots` branch
4. Maintains a history of plot updates over time

### Generated Plots

The CI workflow generates the following plots in the `plots` branch:
- `odometer_vs_date.png` - Odometer reading over time
- `avg_km_per_month.png` - Average kilometers per month with min/max range
- `monthly_distance_histogram.png` - Histogram of monthly distances by year
- `km_l_histogram.png` - Histogram of fuel consumption (km/L)
- `fuel_violin_plot.png` - Violin plot of fuel consumption distribution
- `avg_km_violin_plot.png` - Violin plot of average km/month distribution by year
- `avg_km_violin_plot_{year}.png` - Individual violin plots for each year (2017-2025)
- `eur_km_violin_plot.png` - Violin plot of cost per km (EUR/km) by year
- `avg_km_boxplot.png` - Boxplot of average km/month by year
- `price_boxplot.png` - Boxplot of fuel prices by year
- `avg_price_violin_plot.png` - Violin plot of average fuel prices
- `monthly_km_diff_table.png` - Table of monthly distance differences
- `monthly_price_table.png` - Table of monthly fuel prices

To view the latest plots, check out the `plots` branch or view them on GitHub.

### Using Custom Data

To use your own CarAnalysis data:
1. Export your data from the CarAnalysis app
2. Set the environment variable `CarAnalysis_CSV_PATH` to point to your CSV file
3. Run the notebook: `jupyter notebook CarAnalysis.ipynb`

The notebook will automatically use `CarAnalysis_sample.csv` if no custom path is provided.

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.