# Fuelio Fuel Consumption Analysis

A Python-based data analysis project for analyzing fuel consumption data exported from the Fuelio mobile app using a Jupyter notebook.

## Overview

This project provides tools to analyze:
- Fuel consumption data exported from the Fuelio app
- Statistical analysis and visualizations of fuel economy and driving patterns

## Files

- **CarAnalysis.ipynb**: Comprehensive Fuelio fuel consumption analysis, including:
  - Time-series analysis of odometer readings
  - Monthly distance metrics with average km/refill trend analysis
  - Fuel consumption and pricing trend visualizations
  - Multiple statistical plots (histograms, boxplots, violin plots)
  - Automatically executed via GitHub Actions CI with plot generation
- **Fuelio_sample.csv**: Sample Fuelio fuel consumption data for testing and CI execution
- **requirements.txt**: Python dependencies required to run the notebook
- **CarAnalysis_database/**: Git submodule containing the CarAnalysis database (from [CarAnalysis_database](https://github.com/marcorimo88/CarAnalysis_database) repository)

## Requirements

- Python 3.x
- Jupyter Notebook or JupyterLab
- Required Python packages:
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - dataframe_image
  - scipy

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

2. Open the notebook:
   - `CarAnalysis.ipynb` - For Fuelio fuel consumption analysis

3. Run the cells to see the analysis and visualizations

## Data Format

### Fuelio Data
The notebook expects CSV data exported from the Fuelio app. The CSV has 4 header rows and a footer section (marked by `CostCategories`) that are skipped during loading. The relevant columns are:
- `Date`: Date of fuel entry
- `Odo (km)`: Odometer reading in kilometers
- `Fuel (L)`: Fuel volume in liters
- `Price`: Fuel cost for the transaction
- `Full`: Flag indicating a full tank refill (1 = full tank)

## Features

- Calculate statistical summaries (mean, median, std deviation)
- Visualize data distributions using matplotlib and seaborn
- Analyze fuel consumption patterns
- Track monthly fuel cost and distance metrics
- Time-series analysis of odometer readings
- Price vs. fuel efficiency correlation analysis (Pearson coefficient)
- Full-tank vs. partial-fill analysis

## Continuous Integration (CI)

This repository includes a GitHub Actions workflow that automatically:
1. Executes the CarAnalysis.ipynb notebook on every push to main/master branches
2. Generates all visualization plots (odometer trends, monthly averages, price distributions, etc.)
3. Saves the generated plots to a separate `plots` branch
4. Maintains a history of plot updates over time

### Generated Plots

The CI workflow generates the following plots in the `plots` branch:
- `odometer_vs_date.png` - Odometer reading over time
- `avg_km_per_month.png` - Average km/refill with min/max range
- `monthly_distance_histogram.png` - Stacked histogram of monthly distances by year
- `monthly_cost_histogram.png` - Stacked distribution of Cost/month by year
- `km_l_histogram.png` - Stacked histogram of fuel consumption (km/L) by year
- `fuel_violin_plot.png` - Violin plot of km/l for full-tank refills by year
- `monthly_km_violin_plot.png` - Distribution of monthly km by year
- `eur_km_violin_plot.png` - Violin plot of cost per km (EUR/km) by year
- `avg_km_boxplot.png` - Boxplot of average km/month by year
- `price_boxplot.png` - Boxplot of fuel prices by year
- `avg_price_violin_plot.png` - Violin plot of fuel price distribution by year
- `monthly_km_diff_table.png` - Table of monthly distance totals by year
- `monthly_price_table.png` - Table of monthly fuel costs by year
- `fuel_price_km_plot.png` - Regression plot of Price vs km/l with Pearson correlation
- `avg_km_violin_plot_{year}.png` - Individual monthly km/refill trend plots per year

To view the latest plots, check out the `plots` branch or view them on GitHub.

### Using Custom Data

To use your own Fuelio data:
1. Export your data from the Fuelio app
2. Set the environment variable `FUELIO_CSV_PATH` to point to your CSV file
3. Run the notebook: `jupyter notebook CarAnalysis.ipynb`

The notebook determines the data file using the following priority:
1. `FUELIO_CSV_PATH` environment variable (if set)
2. Latest CSV starting with `Fuelio` from the `CarAnalysis_database` submodule
3. `Fuelio_sample.csv` fallback for demonstration purposes

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.