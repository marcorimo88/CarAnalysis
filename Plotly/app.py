"""
Fuelio Fuel Consumption Analysis — Plotly Dash App
Replicates all analyses from CarAnalysis.ipynb as interactive charts.
"""

import sys
import os
import calendar

import numpy as np
import pandas as pd
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, dash_table, Input, Output

# Allow running from the Plotly/ subdirectory or the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from caranalysis import build_fuel_data

# ─── Data Loading ─────────────────────────────────────────────────────────────

# Load once at startup
fuel_data = build_fuel_data()
all_months_df = pd.DataFrame({
    "Month": range(1, 13),
    "MonthName": [calendar.month_name[i] for i in range(1, 13)],
})
years = sorted(fuel_data["Year_name"].unique().tolist())

# ─── Chart Builders ───────────────────────────────────────────────────────────

def fig_odometer():
    fig = px.line(
        fuel_data, x="Date", y="Odo (km)",
        title="Odometer Reading vs Date",
        markers=True,
    )
    fig.update_traces(marker_size=4)
    fig.update_layout(xaxis_title="Date", yaxis_title="Odometer (km)")
    return fig


def fig_avg_km_refill():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fuel_data["Date"], y=fuel_data["Avgkm/refill"],
        mode="lines+markers", name="Avg km/refill",
        marker_size=4,
    ))
    fig.add_trace(go.Scatter(
        x=pd.concat([fuel_data["Date"], fuel_data["Date"].iloc[::-1]]),
        y=pd.concat([fuel_data["Maxkm/month"], fuel_data["Minkm/month"].iloc[::-1]]),
        fill="toself", fillcolor="rgba(128,128,128,0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Min–Max Range",
    ))
    fig.update_layout(title="Average Kilometers per Refill vs Date",
                      xaxis_title="Date", yaxis_title="Avg km/refill")
    return fig


def fig_cumulative_cost():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fuel_data["Date"], y=fuel_data["cumulative_cost"],
        fill="tozeroy", fillcolor="rgba(99,110,250,0.2)",
        line=dict(width=2),
        name="Cumulative Cost",
    ))
    total = fuel_data["Price"].sum()
    fig.update_layout(
        title=f"Cumulative Fuel Cost Over Time  (total: €{total:,.2f})",
        xaxis_title="Date", yaxis_title="Cumulative fuel spend (€)",
    )
    return fig


def fig_price_per_liter():
    rolling = fuel_data.set_index("Date")["Price/L"].rolling("90D").mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fuel_data["Date"], y=fuel_data["Price/L"],
        mode="lines+markers", name="€/L per refill",
        marker_size=4, opacity=0.5,
    ))
    fig.add_trace(go.Scatter(
        x=rolling["Date"], y=rolling["Price/L"],
        mode="lines", name="90-day rolling avg",
        line=dict(color="red", width=2),
    ))
    fig.update_layout(title="Fuel Price per Liter Over Time",
                      xaxis_title="Date", yaxis_title="€/L")
    return fig


def fig_violin(y_col: str, title: str, y_range=None, filter_fn=None):
    df = fuel_data if filter_fn is None else filter_fn(fuel_data)
    df = df.copy()
    df["Year_str"] = df["Year_name"].astype(str)
    means = df.groupby("Year_str")[y_col].mean().reset_index()

    fig = go.Figure()
    for yr in sorted(df["Year_str"].unique()):
        fig.add_trace(go.Violin(
            x=df[df["Year_str"] == yr]["Year_str"],
            y=df[df["Year_str"] == yr][y_col],
            name=yr, box_visible=True, meanline_visible=True,
            points=False,
        ))
    fig.add_trace(go.Scatter(
        x=means["Year_str"], y=means[y_col],
        mode="markers+lines", name="Mean",
        marker=dict(color="red", size=8),
        line=dict(color="red", width=1),
    ))
    fig.update_layout(title=title, xaxis_title="Year", yaxis_title=y_col,
                      showlegend=False)
    if y_range:
        fig.update_yaxes(range=y_range)
    return fig


def fig_box(y_col: str, title: str, y_label: str):
    df = fuel_data.copy()
    df["Year_str"] = df["Year_name"].astype(str)
    means = df.groupby("Year_str")[y_col].mean().reset_index()
    fig = go.Figure()
    for yr in sorted(df["Year_str"].unique()):
        fig.add_trace(go.Box(
            x=df[df["Year_str"] == yr]["Year_str"],
            y=df[df["Year_str"] == yr][y_col],
            name=yr, boxmean=True,
        ))
    fig.add_trace(go.Scatter(
        x=means["Year_str"], y=means[y_col],
        mode="markers+lines", name="Mean",
        marker=dict(color="red", size=8),
        line=dict(color="red", width=1),
    ))
    fig.update_layout(title=title, xaxis_title="Year", yaxis_title=y_label,
                      showlegend=False)
    return fig


def fig_histogram_stacked(col: str, title: str, x_label: str, filter_fn=None):
    frames = []
    for yr, grp in fuel_data.groupby("Year_name"):
        series = grp[col] if filter_fn is None else grp[col][filter_fn(grp[col])]
        tmp = series.rename(col).to_frame()
        tmp["Year"] = str(yr)
        frames.append(tmp)
    df_plot = pd.concat(frames)
    fig = px.histogram(
        df_plot, x=col, color="Year",
        barmode="stack", nbins=30,
        title=title,
        labels={col: x_label, "count": "Count"},
    )
    fig.update_layout(xaxis_title=x_label, yaxis_title="Count (stacked)")
    return fig


def fig_heatmap_km():
    km_heat = fuel_data.pivot_table(index="Month", columns="Year_name",
                                    values="km_diff", aggfunc="sum")
    km_heat.index = [calendar.month_abbr[m] for m in km_heat.index]

    fig = px.imshow(
        km_heat, text_auto=".0f", color_continuous_scale="YlOrRd",
        title="Total km per Month × Year",
        labels=dict(x="Year", y="Month", color="km"),
    )
    return fig


def fig_heatmap_cost():
    cost_heat = fuel_data.pivot_table(index="Month", columns="Year_name",
                                      values="Price", aggfunc="sum")
    cost_heat.index = [calendar.month_abbr[m] for m in cost_heat.index]

    fig = px.imshow(
        cost_heat, text_auto=".0f", color_continuous_scale="Blues",
        title="Total Fuel Cost (€) per Month × Year",
        labels=dict(x="Year", y="Month", color="€"),
    )
    return fig


def fig_regression(x_col: str, y_col: str, title: str, y_range=None):
    df = fuel_data[[x_col, y_col]].dropna()
    coef, pval = stats.pearsonr(df[x_col], df[y_col])
    m, b = np.polyfit(df[x_col], df[y_col], 1)
    x_line = np.linspace(df[x_col].min(), df[x_col].max(), 200)
    y_line = m * x_line + b

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="markers", name="Data",
        marker=dict(size=5, opacity=0.6),
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines", name=f"Trend (r={coef:.3f}, p={pval:.3g})",
        line=dict(color="red", width=2),
    ))
    fig.update_layout(
        title=f"{title}<br><sup>Pearson r = {coef:.3f}, p = {pval:.3g}</sup>",
        xaxis_title=x_col, yaxis_title=y_col,
    )
    if y_range:
        fig.update_yaxes(range=y_range)
    return fig


def fig_monthly_trend_year(year: int):
    year_data = fuel_data[fuel_data["Year_name"] == year]
    monthly = year_data.groupby("Month").agg(
        MonthName=("MonthName", "first"),
        Avgkm_refill=("Avgkm/refill", "mean"),
        Maxkm=("Maxkm/month", "max"),
        Minkm=("Minkm/month", "min"),
        monthly_km=("monthly_km", "mean"),
    ).reset_index()
    monthly = all_months_df.merge(monthly, on="Month", how="left")
    monthly["MonthName"] = all_months_df["MonthName"]
    monthly[["Avgkm_refill", "Maxkm", "Minkm", "monthly_km"]] = (
        monthly[["Avgkm_refill", "Maxkm", "Minkm", "monthly_km"]].fillna(0)
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["MonthName"], y=monthly["monthly_km"],
        mode="lines+markers", name="Total km/month",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["MonthName"], y=monthly["Avgkm_refill"],
        mode="markers", name="Avg km/refill",
        marker=dict(size=6),
    ))
    # Min–Max shaded area
    fig.add_trace(go.Scatter(
        x=pd.concat([monthly["MonthName"], monthly["MonthName"].iloc[::-1]]),
        y=pd.concat([monthly["Maxkm"], monthly["Minkm"].iloc[::-1]]),
        fill="toself", fillcolor="rgba(128,128,128,0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Min–Max Range",
    ))
    fig.update_layout(
        title=f"Monthly km Distribution — {year}",
        xaxis_title="Month", yaxis_title="km",
        yaxis_range=[0, 4000],
    )
    return fig


def build_annual_summary_table():
    summary = (
        fuel_data.groupby("Year_name")
        .agg(
            Total_km=("km_diff", "sum"),
            Total_liters=("Fuel (L)", "sum"),
            Total_cost=("Price", "sum"),
            Avg_kml=("km/l", "mean"),
            Avg_eur_km=("Eur/km", lambda x: x[x < 0.5].mean()),
            Refills=("Price", "count"),
        )
        .round(2)
        .reset_index()
    )
    summary.columns = ["Year", "Total km", "Total L", "Total € spent", "Avg km/L", "Avg €/km", "# Refills"]
    return summary


def build_monthly_km_pivot():
    pivot = (
        fuel_data.pivot_table(index="MonthName", columns="Year_name",
                              values="km_diff", aggfunc="sum")
        .reindex(all_months_df["MonthName"])
    )
    pivot.loc["Mean [km]"] = pivot.mean(axis=0).values
    pivot["Mean [km]"] = pivot.mean(axis=1).values
    return pivot.round(2).reset_index()


def build_monthly_cost_pivot():
    pivot = (
        fuel_data.pivot_table(index="MonthName", columns="Year_name",
                              values="Price", aggfunc="sum")
        .reindex(all_months_df["MonthName"])
    )
    pivot.loc["Mean [€]"] = pivot.mean(axis=0).values
    pivot["Mean [€]"] = pivot.mean(axis=1).values
    return pivot.round(2).reset_index()


# ─── KPI cards ────────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str) -> html.Div:
    return html.Div([
        html.P(label, style={"margin": "0", "fontSize": "0.8rem", "color": "#888"}),
        html.H3(value, style={"margin": "0", "fontSize": "1.4rem"}),
    ], style={
        "background": "#1e1e2e", "borderRadius": "8px",
        "padding": "14px 20px", "minWidth": "160px", "flex": "1",
    })


def kpi_row() -> html.Div:
    total_km = fuel_data["km_diff"].sum()
    total_cost = fuel_data["Price"].sum()
    avg_kml = fuel_data["km/l"].mean()
    avg_eur_km = fuel_data[fuel_data["Eur/km"] < 0.5]["Eur/km"].mean()
    total_liters = fuel_data["Fuel (L)"].sum()
    refills = len(fuel_data)

    return html.Div([
        kpi_card("Total km", f"{total_km:,.0f} km"),
        kpi_card("Total Fuel", f"{total_liters:,.0f} L"),
        kpi_card("Total Spent", f"€{total_cost:,.2f}"),
        kpi_card("Avg km/L", f"{avg_kml:.2f}"),
        kpi_card("Avg €/km", f"€{avg_eur_km:.3f}"),
        kpi_card("# Refills", str(refills)),
    ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"})


# ─── DataTable helper ─────────────────────────────────────────────────────────

def make_table(df: pd.DataFrame, table_id: str) -> dash_table.DataTable:
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": str(c), "id": str(c)} for c in df.columns],
        data=df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={
            "backgroundColor": "#1e1e2e", "color": "#cdd6f4",
            "border": "1px solid #313244", "padding": "6px 10px",
            "fontFamily": "monospace", "fontSize": "0.82rem",
        },
        style_header={
            "backgroundColor": "#313244", "fontWeight": "bold",
            "color": "#89b4fa", "border": "1px solid #45475a",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#181825"},
        ],
        page_size=20,
    )


# ─── Layout ───────────────────────────────────────────────────────────────────

TAB_STYLE = {"backgroundColor": "#1e1e2e", "color": "#cdd6f4", "padding": "8px 16px"}
TAB_SELECTED_STYLE = {**TAB_STYLE, "backgroundColor": "#313244", "borderTop": "2px solid #89b4fa"}
GRAPH_STYLE = {"height": "600px"}

app = dash.Dash(__name__, title="Car Analysis")
app.layout = html.Div(
    style={"backgroundColor": "#11111b", "color": "#cdd6f4",
           "fontFamily": "Inter, sans-serif", "padding": "20px"},
    children=[
        html.H1("🚗 Fuelio Fuel Consumption Analysis",
                style={"marginBottom": "8px", "color": "#cdd6f4"}),
        html.P("BMW 118i (2017) — Interactive Dashboard",
               style={"color": "#888", "marginBottom": "20px"}),

        kpi_row(),

        dcc.Tabs(
            style={"marginBottom": "16px"},
            children=[

                # ── Overview ───────────────────────────────────────────────
                dcc.Tab(label="Overview", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_odometer(), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_cumulative_cost(), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_avg_km_refill(), style=GRAPH_STYLE),
                        ]),

                # ── Distance ───────────────────────────────────────────────
                dcc.Tab(label="Distance", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_violin("monthly_km",
                                                        "Distribution of Monthly km by Year"), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_box("monthly_km",
                                                     "Monthly km Boxplot by Year", "Monthly km"), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_histogram_stacked(
                                "monthly_mean_km",
                                "Stacked Distribution of Avg km/month by Year",
                                "Avg km/month",
                            ), style=GRAPH_STYLE),

                            html.H3("Monthly km Trend — Select Year",
                                    style={"marginTop": "24px", "color": "#89b4fa"}),
                            dcc.Dropdown(
                                id="year-dropdown",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=years[-1],
                                clearable=False,
                                style={"backgroundColor": "#313244", "color": "#cdd6f4",
                                       "border": "none", "maxWidth": "600px"},
                            ),
                            dcc.Graph(id="monthly-trend-graph", style=GRAPH_STYLE),
                        ]),

                # ── Efficiency ─────────────────────────────────────────────
                dcc.Tab(label="Efficiency", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_violin("km/l",
                                                        "Distribution of km/l by Year",
                                                        y_range=[0, 20]), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_violin("Fuel (L)",
                                                        "Distribution of Fuel (L) by Year",
                                                        y_range=[0, 52]), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_histogram_stacked(
                                "km/l",
                                "Stacked Distribution of km/l by Year (excl. zeros)",
                                "km/l",
                                filter_fn=lambda s: s > 0,
                            ), style=GRAPH_STYLE),
                        ]),

                # ── Costs ──────────────────────────────────────────────────
                dcc.Tab(label="Costs", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_price_per_liter(), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_violin("Eur/km",
                                                        "Distribution of €/km by Year",
                                                        filter_fn=lambda df: df[df["Eur/km"] < 0.5]),
                                      style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_box("Price",
                                                     "Fuel Price Boxplot by Year", "Price (€)"), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_histogram_stacked(
                                "monthly_cost",
                                "Stacked Distribution of Monthly Cost by Year",
                                "Monthly Cost (€)",
                            ), style=GRAPH_STYLE),
                        ]),

                # ── Heatmaps ───────────────────────────────────────────────
                dcc.Tab(label="Heatmaps", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_heatmap_km(), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_heatmap_cost(), style=GRAPH_STYLE),
                        ]),

                # ── Correlations ───────────────────────────────────────────
                dcc.Tab(label="Correlations", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            dcc.Graph(figure=fig_regression(
                                "Price", "km/l",
                                "Price vs Fuel Efficiency",
                                y_range=[0, 20],
                            ), style=GRAPH_STYLE),
                            dcc.Graph(figure=fig_regression(
                                "km/l", "Fuel (L)",
                                "Fuel Efficiency vs Volume Refilled",
                                y_range=[0, 55],
                            ), style=GRAPH_STYLE),
                        ]),

                # ── Tables ─────────────────────────────────────────────────
                dcc.Tab(label="Tables", style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                        children=[
                            html.H3("Annual Summary", style={"color": "#89b4fa", "marginTop": "16px"}),
                            make_table(build_annual_summary_table(), "annual-table"),

                            html.H3("Monthly km by Year (km)", style={"color": "#89b4fa", "marginTop": "24px"}),
                            make_table(build_monthly_km_pivot(), "km-pivot-table"),

                            html.H3("Monthly Cost by Year (€)", style={"color": "#89b4fa", "marginTop": "24px"}),
                            make_table(build_monthly_cost_pivot(), "cost-pivot-table"),
                        ]),
            ],
        ),
    ],
)

# ─── Callbacks ────────────────────────────────────────────────────────────────

@app.callback(
    Output("monthly-trend-graph", "figure"),
    Input("year-dropdown", "value"),
)
def update_monthly_trend(year):
    return fig_monthly_trend_year(int(year))


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=8050)
