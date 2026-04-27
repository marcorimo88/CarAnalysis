"""
Synology disk temperature timeline — Plotly Dash app.

Polls disk temps via SNMP on a configurable interval and stores readings
in a run-length-encoded CSV: each row is (t_start, t_end, <one int °C
column per disk>). When a new poll matches the previous reading, only
t_end is updated; a new row is appended only when a temperature changes.
History is reloaded on restart so the timeline survives across sessions.
"""

import csv
import logging
import os
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State, no_update

from Synology import get_disks

HOST = os.environ.get("SYNOLOGY_HOST", "192.168.1.150")
SNMP_USER = os.environ.get("SYNOLOGY_SNMP_USER", "test")
SNMP_AUTH_KEY = os.environ.get("SYNOLOGY_SNMP_AUTH_KEY", "testnuovo")
SNMP_PRIV_KEY = os.environ.get("SYNOLOGY_SNMP_PRIV_KEY", "testnuovo")
CSV_PATH = Path(__file__).parent / "synology_temps.csv"

# Run-length-encoded wide schema:
#   t_start, t_end, <disk1 °C>, <disk2 °C>, ...
# When a new poll matches the previous reading, the last row's t_end is
# extended in place; only when temperatures change is a new row appended.

REFRESH_OPTIONS = [
    {"label": "1 s",  "value": 1},
    {"label": "10 s",  "value": 10},
    {"label": "30 s",  "value": 30},
    {"label": "1 min", "value": 60},
    {"label": "5 min", "value": 300},
    {"label": "15 min","value": 900},
    {"label": "1 h",   "value": 3600},
]
DEFAULT_REFRESH_S = 60


def _read_header():
    """Return the disk-name columns (excluding t_start, t_end) from the CSV header,
    or None if file is missing / empty / not in RLE format."""
    if not CSV_PATH.exists():
        return None
    with CSV_PATH.open("r", newline="") as f:
        first = f.readline().strip()
    if not first:
        return None
    cols = first.split(",")
    if cols[:2] != ["t_start", "t_end"]:
        return None
    return cols[2:]


def _migrate_csv():
    """Migrate any older CSV format to the RLE wide format in-place."""
    if not CSV_PATH.exists():
        return
    with CSV_PATH.open("r", newline="") as f:
        first = f.readline().strip().split(",")
    if first[:2] == ["t_start", "t_end"]:
        return  # already RLE

    df = pd.read_csv(CSV_PATH)
    if df.empty:
        return

    # Old long format: t,d,c → pivot to wide first.
    if list(df.columns) == ["t", "d", "c"]:
        df = df.pivot_table(index="t", columns="d", values="c", aggfunc="last")
        df = df.sort_index().reset_index()

    if "t" not in df.columns:
        return

    disk_cols = [c for c in df.columns if c != "t"]
    df = df.sort_values("t").reset_index(drop=True)

    # Run-length encode: collapse consecutive identical readings.
    rows = []
    for _, r in df.iterrows():
        temps_tuple = tuple(r[c] for c in disk_cols)
        if rows and rows[-1]["temps"] == temps_tuple:
            rows[-1]["t_end"] = int(r["t"])
        else:
            rows.append({"t_start": int(r["t"]), "t_end": int(r["t"]), "temps": temps_tuple})

    out = pd.DataFrame([
        {"t_start": r["t_start"], "t_end": r["t_end"],
         **dict(zip(disk_cols, r["temps"]))}
        for r in rows
    ])
    out.to_csv(CSV_PATH, index=False)


def append_reading(disks):
    ts = int(time.time())
    names = [d["name"] for d in disks]
    temps = {d["name"]: d["temp_c"] for d in disks}

    header = _read_header()
    if header is None:
        with CSV_PATH.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t_start", "t_end", *names])
            w.writerow([ts, ts, *[temps[n] for n in names]])
        return

    # Expand header if a new disk appeared.
    new_cols = [n for n in names if n not in header]
    if new_cols:
        df = load_history_wide()
        for col in new_cols:
            df[col] = pd.NA
        header = header + new_cols
        df = df[["t_start", "t_end", *header]]
        df.to_csv(CSV_PATH, index=False)

    new_temps = [temps.get(n, "") for n in header]
    new_temps_str = [str(v) for v in new_temps]

    with CSV_PATH.open("r", newline="") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        with CSV_PATH.open("a", newline="") as f:
            csv.writer(f).writerow([ts, ts, *new_temps])
        return

    last = lines[-1].rstrip("\r\n").split(",")
    last_temps_str = last[2:]

    if last_temps_str == new_temps_str:
        # Same reading — just extend t_end on the previous row.
        lines[-1] = ",".join([last[0], str(ts), *last_temps_str]) + "\n"
        with CSV_PATH.open("w", newline="") as f:
            f.writelines(lines)
    else:
        with CSV_PATH.open("a", newline="") as f:
            csv.writer(f).writerow([ts, ts, *new_temps])


def load_history_wide():
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=["t_start", "t_end"])
    return pd.read_csv(CSV_PATH)


def load_history():
    """Return long-form (timestamp, disk, temp_c) with two points per RLE row
    (t_start and t_end), so the plot draws horizontal segments."""
    df = load_history_wide()
    if df.empty or "t_start" not in df.columns:
        return pd.DataFrame(columns=["timestamp", "disk", "temp_c"])

    long = df.melt(id_vars=["t_start", "t_end"], var_name="disk", value_name="temp_c")
    long = long.dropna(subset=["temp_c"])

    starts = long.rename(columns={"t_start": "t"})[["t", "disk", "temp_c"]]
    ends = long.rename(columns={"t_end": "t"})[["t", "disk", "temp_c"]]
    out = pd.concat([starts, ends], ignore_index=True)
    out = out.drop_duplicates(["t", "disk"]).sort_values(["disk", "t"])
    out["timestamp"] = pd.to_datetime(out["t"], unit="s")
    return out[["timestamp", "disk", "temp_c"]]


DEBUG = False

# Silence Werkzeug's per-request access log unless debug is on.
logging.getLogger("werkzeug").setLevel(logging.ERROR)


def poll_once():
    try:
        disks = get_disks(HOST, SNMP_USER, SNMP_AUTH_KEY, SNMP_PRIV_KEY)
        if DEBUG:
            print(f"[debug] poll {time.strftime('%Y-%m-%d %H:%M:%S')} host={HOST} disks={disks}", flush=True)
        append_reading(disks)
        return None
    except Exception as e:
        if DEBUG:
            print(f"[debug] poll error: {e!r}", flush=True)
        return str(e)


def build_figure(df):
    fig = go.Figure()
    if not df.empty:
        for disk, grp in df.groupby("disk"):
            grp = grp.sort_values("timestamp")
            fig.add_trace(go.Scatter(
                x=grp["timestamp"], y=grp["temp_c"],
                mode="markers", name=str(disk),
            ))
    fig.update_layout(
        title="Synology disk temperature",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


_migrate_csv()

app = dash.Dash(__name__)
app.title = "Synology disk temperature"

app.layout = html.Div(
    style={"fontFamily": "sans-serif", "maxWidth": "1100px", "margin": "auto"},
    children=[
        html.H2("Synology disk temperature timeline"),
        html.Div(
            style={"display": "flex", "gap": "1rem", "alignItems": "center"},
            children=[
                html.Label("Refresh every:"),
                dcc.Dropdown(
                    id="refresh-rate",
                    options=REFRESH_OPTIONS,
                    value=DEFAULT_REFRESH_S,
                    clearable=False,
                    style={"width": "160px"},
                ),
                html.Button("Refresh now", id="refresh-now", n_clicks=0),
                dcc.Checklist(
                    id="debug-toggle",
                    options=[{"label": " Verbose terminal debug", "value": "on"}],
                    value=[],
                    style={"marginLeft": "0.5rem"},
                ),
                html.Span(id="status", style={"color": "#666"}),
            ],
        ),
        dcc.Interval(id="tick", interval=DEFAULT_REFRESH_S * 1000, n_intervals=0),
        dcc.Interval(id="sync-tick", interval=1000, n_intervals=0),
        dcc.Store(id="rate-sink"),
        dcc.Graph(id="temp-graph", figure=build_figure(load_history())),
    ],
)


# Persist the dropdown value to localStorage whenever it changes.
app.clientside_callback(
    """
    function(value) {
        if (value !== null && value !== undefined) {
            localStorage.setItem('synology-refresh-rate', JSON.stringify(value));
        }
        return null;
    }
    """,
    Output("rate-sink", "data"),
    Input("refresh-rate", "value"),
)


# Poll localStorage so other tabs pick up the new value.
app.clientside_callback(
    """
    function(n, current) {
        const raw = localStorage.getItem('synology-refresh-rate');
        if (raw === null) return window.dash_clientside.no_update;
        const stored = JSON.parse(raw);
        if (stored === current) return window.dash_clientside.no_update;
        return stored;
    }
    """,
    Output("refresh-rate", "value"),
    Input("sync-tick", "n_intervals"),
    State("refresh-rate", "value"),
)


@app.callback(
    Output("tick", "interval"),
    Input("refresh-rate", "value"),
)
def update_interval(seconds):
    return int(seconds) * 1000


@app.callback(
    Output("debug-toggle", "value"),
    Input("debug-toggle", "value"),
)
def update_debug(value):
    global DEBUG
    DEBUG = "on" in (value or [])
    logging.getLogger("werkzeug").setLevel(logging.INFO if DEBUG else logging.ERROR)
    print(f"[debug] verbose logging {'ENABLED' if DEBUG else 'disabled'}", flush=True)
    return value


@app.callback(
    Output("temp-graph", "figure"),
    Output("status", "children"),
    Input("tick", "n_intervals"),
    Input("refresh-now", "n_clicks"),
    State("refresh-rate", "value"),
    prevent_initial_call=False,
)
def refresh(_n, _clicks, _rate):
    err = poll_once()
    df = load_history()
    if err:
        status = f"poll failed: {err} (showing history with {len(df)} rows)"
    else:
        last = df["timestamp"].max() if not df.empty else "—"
        status = f"{len(df)} readings · last {last}"
    return build_figure(df), status


if __name__ == "__main__":
    app.run(debug=False, port=8051)
