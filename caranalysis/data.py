"""
Shared data loading and transformation for CarAnalysis.

Used by both CarAnalysis.ipynb and Plotly/app.py.
"""

import os
import calendar

import numpy as np
import pandas as pd


def load_data() -> pd.DataFrame:
    """
    Locate and load the Fuelio CSV export.

    Resolution order:
    1. FUELIO_CSV_PATH environment variable
    2. Most-recent Fuelio*.csv in the CarAnalysis_database/ submodule
    3. Fuelio_sample.csv in the current working directory

    Skips the 4-row header and the footer section starting with
    'CostCategories'. Sorts by odometer and imputes zero km/l values
    with the yearly mean.
    """
    csv_path = os.getenv("FUELIO_CSV_PATH")
    if not csv_path:
        # Resolve relative to this file so imports work from any CWD
        pkg_dir = os.path.dirname(__file__)
        db_dir = os.path.join(pkg_dir, "..", "CarAnalysis_database")
        db_dir = os.path.normpath(db_dir)
        if os.path.exists(db_dir):
            csv_files = [
                f for f in os.listdir(db_dir)
                if f.startswith("Fuelio") and f.endswith(".csv")
            ]
            if csv_files:
                csv_path = os.path.join(db_dir, sorted(csv_files)[-1])

    if not csv_path:
        csv_path = "Fuelio_sample.csv"

    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    footer_count = 1
    for line in reversed(lines):
        if "CostCategories" not in line.strip():
            footer_count += 1
        else:
            break

    df = pd.read_csv(
        csv_path,
        skiprows=[0, 1, 2, 3],
        skipfooter=footer_count,
        engine="python",
    )
    df.sort_values(by="Odo (km)", inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])

    yearly_mean = (
        df[df["km/l"] > 0]
        .groupby(df["Date"].dt.year)["km/l"]
        .mean()
    )
    mask = df["km/l"] == 0
    df.loc[mask, "km/l"] = df.loc[mask, "Date"].dt.year.map(yearly_mean)

    return df


def calculate_avg_km_per_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich a raw Fuelio DataFrame with monthly aggregates and derived columns.

    Added columns
    -------------
    Year-Month, Year, Month, MonthName, Year_name, Month_name
    km_diff         — distance between consecutive refills
    monthly_km      — total km driven in that calendar month
    monthly_cost    — total fuel spend in that calendar month
    monthly_mean_km — mean km per refill in that calendar month
    monthly_km_size — number of refills in that calendar month
    Avgkm/refill    — monthly_km / monthly_km_size
    Avgkm/liter     — monthly_km / monthly litres consumed
    Maxkm/month     — largest single refill interval in that month
    Minkm/month     — smallest single refill interval in that month
    Eur/km          — cost per km for each refill
    Price/L         — fuel price per litre for each refill
    cumulative_cost — running total of fuel spend
    """
    df = df.copy()

    df["Year-Month"] = df["Date"].dt.to_period("M")
    df["Year"]       = df["Date"].dt.to_period("Y")
    df["Month"]      = df["Date"].dt.month
    df["MonthName"]  = df["Month"].apply(lambda x: calendar.month_name[x])
    df["Year_name"]  = df["Date"].dt.year
    df["Month_name"] = df["Date"].dt.month_name()
    df["km_diff"]    = df["Odo (km)"].diff()

    monthly_km      = df.groupby("Year-Month")["km_diff"].sum()
    monthly_cost    = df.groupby("Year-Month")["Price"].sum()
    monthly_mean_km = df.groupby("Year-Month")["km_diff"].mean()
    max_km          = df.groupby("Year-Month")["km_diff"].max()
    min_km          = df.groupby("Year-Month")["km_diff"].min()
    liter           = df.groupby("Year-Month")["Fuel (L)"].sum()
    size_km         = df.groupby("Year-Month").size()

    df["monthly_km"]      = df["Year-Month"].map(monthly_km).astype(float)
    df["monthly_cost"]    = df["Year-Month"].map(monthly_cost).astype(float)
    df["monthly_mean_km"] = df["Year-Month"].map(monthly_mean_km).astype(float)
    df["monthly_km_size"] = df["Year-Month"].map(size_km).astype(float)
    df["Avgkm/refill"]    = (df["monthly_km"] / df["monthly_km_size"]).astype(float)
    df["Avgkm/liter"]     = df["monthly_km"] / df["Year-Month"].map(liter).astype(float)
    df["Maxkm/month"]     = df["Year-Month"].map(max_km).astype(float)
    df["Minkm/month"]     = df["Year-Month"].map(min_km).astype(float)
    df["Eur/km"]          = (df["Price"] / df["km_diff"].replace(0, np.nan)).astype(float)
    df["Price/L"]         = df["Price"] / df["Fuel (L)"]
    df["cumulative_cost"] = df["Price"].cumsum()

    return df


def build_fuel_data() -> pd.DataFrame:
    """Convenience function: load raw data and apply all enrichments."""
    return calculate_avg_km_per_month(load_data())
