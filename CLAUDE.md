# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal fuel consumption analysis tool for a BMW 118i (2017), processing data exported from the Fuelio mobile app. Two parallel implementations: a Jupyter notebook for exploration/export and a Dash web app for interactive use.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Jupyter notebook
jupyter notebook CarAnalysis.ipynb

# Execute notebook non-interactively (as CI does)
jupyter nbconvert --to notebook --execute CarAnalysis.ipynb --output CarAnalysis_executed.ipynb

# Run the Plotly/Dash dashboard (http://localhost:8050)
cd Plotly && python app.py
```

## Architecture

**Two parallel implementations** that share logic but serve different purposes:
- `CarAnalysis.ipynb` — primary analysis notebook; generates PNG plots saved to `/plots`
- `Plotly/app.py` — interactive Dash dashboard; mirrors notebook functionality with UI controls

**Data pipeline:**
1. Load CSV from `CarAnalysis_database/` submodule, `FUELIO_CSV_PATH` env var, or `Fuelio_sample.csv` fallback
2. Skip 4 header rows; stop at footer row containing `"CostCategories"`
3. Sort by odometer, compute derived columns: `km_diff`, `km/l`, `Eur/km`, `Price/L`, monthly aggregates
4. Produce visualizations: time-series, histograms, violin/box plots, heatmaps, regression plots

**Key computed columns:** `km_diff` (distance between refills), `km/l` (fuel efficiency), `Eur/km` (cost efficiency), `Price/L` (fuel price), monthly rollups. All calculations assume `Full == 1` indicates a complete tank refill.

**Git submodule:** `CarAnalysis_database/` holds actual fuel data and must be initialized with `git clone --recurse-submodules` or `git submodule update --init`.

**CI/CD:** GitHub Actions executes the notebook on push to main, commits generated PNG plots to the separate `plots` branch.

## Data Format

Fuelio CSV exports have 4 header rows to skip and a footer section starting with `"CostCategories"`. The main columns used are: `Date`, `Odo (km)`, `Fuel (L)`, `Price` (EUR), `Full` (1 = full tank).
