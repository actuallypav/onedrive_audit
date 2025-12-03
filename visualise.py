import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timezone


# config
CSV_FILE = "drive_index.csv"
CHART_DIR = "visualisations"
HTML_DIR = "visualisations_interactive"
STALE_DAYS = 365
COST_PER_GB = 0.02

os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

# Load Data
df = pd.read_csv(CSV_FILE, parse_dates=["modified"])
now = pd.Timestamp.now(tz=timezone.utc)

df["size_gb"] = df["size"] / (1024**3)
df["age_days"] = (now - df["modified"]).dt.days

total_gb = df["size_gb"].sum()
unused_gb = df.loc[df["age_days"] > STALE_DAYS, "size_gb"].sum()
unused_pct = (unused_gb / total_gb) * 100 if total_gb else 0
waste = unused_gb * COST_PER_GB

df["month"] = df["modified"].dt.tz_localize(None).dt.to_period("M").astype(str)
growth = df.groupby("month", as_index=False)["size_gb"].sum()
growth["cumulative_gb"] = growth["size_gb"].cumsum()
monthly_growth = growth["size_gb"].mean().round(2)

def status_color(value, thresholds):
    low, high = thresholds
    if value < low:
        return "#16A34A"   # green
    elif value < high:
        return "#F59E0B"   # amber
    else:
        return "#DC2626"   # red

#kpi

total_color  = "#1F3A8A"  # neutral blue
unused_color = status_color(unused_pct, (30, 50))
growth_color = status_color(monthly_growth, (0.5, 2))
waste_color  = status_color(waste, (1, 5))

tiles = [
    ("Total data", f"{total_gb:.1f} GB", total_color),
    ("Unused >1yr", f"{unused_pct:.1f}%", unused_color),
    ("Monthly growth", f"{monthly_growth:.2f} GB", growth_color),
    ("£ waste / mo", f"£{waste:.2f}", waste_color),
]

kpi_fig = go.Figure()
TW = len(tiles)
TH = 1

for i, (title, value, color) in enumerate(tiles):

    kpi_fig.add_shape(
        type="rect",
        x0=i, y0=0, x1=i+1, y1=TH,
        fillcolor=color,
        line=dict(color="black", width=1),
        layer="below"
    )

    kpi_fig.add_annotation(
        x=i + 0.5, y=0.62,
        text=f"<b>{title}</b>",
        showarrow=False,
        font=dict(size=16, color="white"),
        align="center"
    )

    kpi_fig.add_annotation(
        x=i + 0.5, y=0.30,
        text=value,
        showarrow=False,
        font=dict(size=28, color="white"),
        align="center"
    )

kpi_fig.update_layout(
    title=dict(text="KPIs", x=0.5, font=dict(size=22)),
    xaxis=dict(showticklabels=False, range=[0, TW], fixedrange=True),
    yaxis=dict(showticklabels=False, range=[0, TH], fixedrange=True),
    height=260,
    width=1000,
    margin=dict(l=40, r=40, t=60, b=20),
    plot_bgcolor="white"
)

kpi_fig.update_xaxes(visible=False, showgrid=False, zeroline=False)
kpi_fig.update_yaxes(visible=False, showgrid=False, zeroline=False)

kpi_fig.write_image(f"{CHART_DIR}/kpi.png", scale=2)
kpi_fig.write_html(f"{HTML_DIR}/kpi.html")

# treemap
# OLD file treemap
# top = df.sort_values("size_gb", ascending=False).head(30).copy()
# top["label"] = top["path"].str.rsplit("/", n=1).str[-1]

# treemap = px.treemap(
#     top,
#     path=["label"],
#     values="size_gb",
#     title="Top Space Consumers (GB)"
# )
# treemap.write_image(f"{CHART_DIR}/treemap.png", scale=2)
# treemap.write_html(f"{HTML_DIR}/treemap.html")

#FOLDER treemap
df["folder"] = df["path"].str.split("/").str[0]
df["folder"] = df["folder"].replace("", "(root)")

folder_sizes = df.groupby("folder", as_index=False)["size_gb"].sum()
top_folders = folder_sizes.sort_values("size_gb", ascending=False).head(30)

folder_treemap = px.treemap(
    top_folders,
    path=["folder"],
    values="size_gb",
    title="Top Level Folder Storage Usage (GB)"
)

folder_treemap.update_layout(
    margin=dict(t=50, l=0, r=0, b=0)
)

folder_treemap.update_traces(hovertemplate="%{label}<br>%{value:.2f} GB<extra></extra>")

folder_treemap.write_image(f"{CHART_DIR}/treemap.png", scale=2)
folder_treemap.write_html(f"{HTML_DIR}/treemap.html")

# histogram
bins = [0, 30, 90, 180, 365, 730, 1500, 3000, 6000]
labels = ["30d","1–3m","3–6m","6–12m","1–2y","2–4y","4–8y","8+y"]
df["bucket"] = pd.cut(df["age_days"], bins=bins, labels=labels)

age_counts = df["bucket"].value_counts().sort_index().reset_index()
age_counts.columns = ["Bucket", "Count"]

age_fig = px.bar(age_counts, x="Bucket", y="Count", title="File Age Distribution")
age_fig.update_layout(
    xaxis_title="File age",
    yaxis_title="Number of files",
)
age_fig.write_image(f"{CHART_DIR}/age_hist.png", scale=2)
age_fig.write_html(f"{HTML_DIR}/age_hist.html")

# growth trend
growth_fig = px.line(
    growth, x="month", y="cumulative_gb", markers=True,
    title="Storage Growth Over Time (GB)"
)
growth_fig.update_layout(xaxis_title="Month", yaxis_title="Total GB")
growth_fig.write_image(f"{CHART_DIR}/growth.png", scale=2)
growth_fig.write_html(f"{HTML_DIR}/growth.html")

print("Generated:")
for f in ["kpi.png","treemap.png","age_hist.png","growth.png"]:
    print(" ", CHART_DIR + "/" + f)
for f in ["kpi.html","treemap.html","age_hist.html","growth.html"]:
    print(" ", HTML_DIR + "/" + f)
