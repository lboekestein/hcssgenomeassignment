# dashboard.py
"""
Sets up a basic streamlit dashboard to visualize results
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.episodes import ALL_EPISODES
from src.hostility import compute_hostility_index
from src.theme import COLORS, FONT_FAMILY, LOGO_PATH

# -------------
# Set up, style
# -------------
st.set_page_config(
    page_title="GENOME Conflict Episode Explorer",
    layout="wide",
    page_icon=str(LOGO_PATH),
)
st.markdown(
    f"""
<style>
html, body, [class*="css"] {{
    font-family: {FONT_FAMILY};
}}
.block-container {{
    padding-top: 3rem;
}}
</style>
""",
    unsafe_allow_html=True,
)

st.logo(str(LOGO_PATH))

# ----------------------
# Read in data
# Filter based on selection
# ----------------------
data = pd.read_csv("data/processed/processed_data.csv", parse_dates=["event_date"])

# Conflict episode selector
episode_labels = {ep.label: ep for ep in ALL_EPISODES}
selected_label = st.sidebar.selectbox(
    "Select conflict episode", list(episode_labels.keys())
)
episode = episode_labels[selected_label]

# Get available data for countries involved in this episode
episode_data = data[data["dyad"] == episode.dyad]
data_min = episode_data["event_date"].min().date()
data_max = episode_data["event_date"].max().date()

onset = episode.onset_date
required_end = episode.end_date if episode.end_date is not None else onset

# Sidebar slider to filter on time
default_start = max(data_min, onset.date() - pd.Timedelta(days=365))
default_end = (
    min(data_max, required_end.date() + pd.Timedelta(days=30))
    if not episode.ongoing
    else data_max
)

st.sidebar.subheader("Time range")
selected_range = st.sidebar.slider(
    "Show data from / to",
    min_value=data_min,
    max_value=data_max,
    value=(default_start, default_end),
    format="YYYY-MM-DD",
)
start_date, end_date_filter = selected_range

# Apply data filter
filtered_data = episode_data[
    (episode_data["event_date"].dt.date >= start_date)
    & (episode_data["event_date"].dt.date <= end_date_filter)
]

df = compute_hostility_index(filtered_data, episode).reset_index()

# --------
# Title and general info
# --------

st.markdown(
    f"<p style='color:{COLORS['grey']}; font-size:0.85rem; letter-spacing:0.05em; "
    f"text-transform:uppercase; margin-bottom:0;'>GENOME Conflict Episode Explorer</p>",
    unsafe_allow_html=True,
)

st.title(f"{episode.label}")
col1, col2, col3 = st.columns(3)
col1.badge(
    "Ongoing" if episode.ongoing else "Ended",
    icon=":material/alarm:",
    color="orange" if episode.ongoing else "grey",
)
col2.caption(f"**Onset Date:** {episode.onset_date.date()}")
col3.caption(
    f"**End Date:** {episode.end_date.date() if episode.end_date else 'Ongoing'}"
)
st.divider()

# ------------------------------------
# Main plot; hostility index over time
# ------------------------------------

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df["event_date"],
        y=df["normalized_hostility_combined"],
        name="Net hostility",
        line=dict(color=COLORS["accent"], width=3),
        customdata=df[["normalized_hostility_combined", "event_count_combined"]],
        hovertemplate=(
            "<b>Net Hostility</b><br>"
            "Hostility level: %{customdata[0]:.2f}<br>"
            "Events: %{customdata[1]}"
            "<extra></extra>"
        ),
    )
)

direction_cols = [
    c
    for c in df.columns
    if c.startswith("normalized_hostility_") and c != "normalized_hostility_combined"
]
direction_colors = ["#8E44AD", "#E67E22"]

for col, color in zip(direction_cols, direction_colors):
    direction_label = col.replace("normalized_hostility_", "").replace("_", " → ")
    fig.add_trace(
        go.Scatter(
            x=df["event_date"],
            y=df[col],
            name=direction_label,
            line=dict(color=color, width=1.5, dash="dot"),
            customdata=df[[col, col.replace("normalized_hostility_", "event_count_")]],
            hovertemplate=(
                f"<b>{direction_label}</b><br>"
                "Hostility level: %{customdata[0]:.2f}<br>"
                "Events: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

fig.add_vline(
    x=episode.onset_date,
    line_dash="dash",
    line_color=COLORS["conflict"],
    annotation_text="Onset",
    annotation_position="top",
)
if episode.end_date is not None:
    fig.add_vline(
        x=episode.end_date,
        line_dash="dash",
        line_color=COLORS["cooperation"],
        annotation_text="End",
        annotation_position="top",
    )

fig.update_layout(
    title=f"Weekly hostility index ",
    xaxis_title="Week",
    yaxis_title="Hostility score",
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.02,
    ),
    plot_bgcolor=COLORS["plot_bg"],
    paper_bgcolor=COLORS["plot_bg"],
    font=dict(family=FONT_FAMILY, color=COLORS["grey"], size=13),
    hovermode="x unified",
    margin=dict(l=50, r=30, t=60, b=50),
)
fig.update_xaxes(showgrid=True, gridcolor=COLORS["plot_bg"], zeroline=False)
fig.update_yaxes(
    showgrid=True,
    gridcolor=COLORS["plot_bg"],
    zeroline=True,
    zerolinecolor=COLORS["dark"],
    zerolinewidth=1,
)


col1, col2 = st.columns([0.7, 0.3])

# brief caption explaining measure
col1.caption(
    "The **hostility index** tracks how conflictual or cooperative interactions "
    "between the two countries have been each week. Positive values mean conflict "
    "(threats, sanctions, military action) outweighed cooperation; negative values "
    "mean the opposite. The score also rises with the *number* of events, not just "
    "their intensity, which means a busy week of conflict scores higher than a single hostile event."
)

col1.plotly_chart(fig, width="stretch")

# ---------------------------------
# Additional descriptive statistics
# ---------------------------------

# filter to only events during conflict
episode_df = df[df["event_date"] >= episode.onset_date]
if episode.end_date is not None:
    episode_df = episode_df[episode_df["event_date"] <= episode.end_date]

col2.subheader("Conflict episode summary:")
col2.metric(
    "Peak hostility",
    round(episode_df["normalized_hostility_combined"].max(), 2),
    delta_color="blue",
    border=True,
    chart_type="line",
    chart_data=episode_df[["normalized_hostility_combined"]],
)
col2.metric(
    "Total events",
    int(episode_df["event_count_combined"].sum()),
    border=True,
    delta_color="blue",
    chart_type="bar",
    chart_data=episode_df[["event_count_combined"]],
)

with col2.expander("How is the hostility index calculated?"):
    st.markdown("""
    Each GENOME event has an **intensity** score from –1 (most conflictual) to +1 
    (most cooperative). We flip the sign so higher values mean more hostile, then:

    - **Weekly totals** are the *sum* of all events' hostility scores that week — 
      so both how hostile events were, and how many occurred, affect the index.
    - **Directional lines** (dotted) show each country's hostility *toward* the 
      other separately — useful for seeing whether one side is driving the trend, 
      or both are escalating together.
    - **Net hostility** (solid line) combines both directions into a single 
      dyad-level score.

    Onset and end dates (dashed vertical lines) mark the documented start and 
    resolution of this conflict episode, based on external reporting rather than 
    the GENOME data itself.
    """)

st.divider()

# ---------
# Plot with evolution of four PLOVER categories
# ---------

category_evolution = (
    filtered_data.set_index("event_date")
    .groupby([pd.Grouper(freq="W"), "quadrant"])
    .size()
    .reset_index(name="count")
)

# fixed colors per quadrant so they stay consistent across episodes/reruns —
# worth adding these two new keys to theme.py's COLORS dict alongside your existing ones
quadrant_colors = {
    "material_conflict": COLORS["conflict"],
    "verbal_conflict": COLORS["lightconflict"],
    "material_cooperation": COLORS["cooperation"],
    "verbal_cooperation": COLORS["lightcooperation"],
}

evo_fig = go.Figure()
for quadrant, color in quadrant_colors.items():
    sub = category_evolution[category_evolution["quadrant"] == quadrant]
    evo_fig.add_trace(
        go.Scatter(
            x=sub["event_date"],
            y=sub["count"],
            name=quadrant.replace("_", " ").title(),
            line=dict(color=color, width=2),
            hovertemplate="%{y} events<extra></extra>",
        )
    )

evo_fig.add_vline(x=episode.onset_date, line_dash="dash", line_color=COLORS["dark"])
if episode.end_date is not None:
    evo_fig.add_vline(x=episode.end_date, line_dash="dash", line_color=COLORS["dark"])

evo_fig.update_layout(
    title="Weekly event frequency by category",
    xaxis_title="Week",
    yaxis_title="Number of events",
    plot_bgcolor=COLORS["plot_bg"],
    paper_bgcolor=COLORS["plot_bg"],
    font=dict(family=FONT_FAMILY, color=COLORS["grey"], size=13),
    hovermode="x unified",
    margin=dict(l=50, r=30, t=60, b=50),
    height=420,
)
evo_fig.update_xaxes(showgrid=True, gridcolor=COLORS["plot_bg"])
evo_fig.update_yaxes(showgrid=True, gridcolor=COLORS["plot_bg"])

col1, col2 = st.columns([0.3, 0.7])

col2.subheader("Prevalence of Conflict and Cooperation events")

col1.subheader("Most common events")

col2.plotly_chart(evo_fig, width="stretch")


# -----------------------
# Plot most common events
# -----------------------

for category in ["CONFLICT", "COOPERATION"]:

    category_data = filtered_data[filtered_data["category"] == category]
    counts = category_data["event_type"].value_counts().head(3)

    fig = go.Figure(
        go.Bar(
            x=counts.values.tolist(),
            y=counts.index.tolist(),
            orientation="h",
            marker_color=COLORS[f"light{category.lower()}"],
        )
    )
    fig.update_layout(
        title=f"{category.capitalize()} events",
        plot_bgcolor=COLORS["plot_bg"],
        paper_bgcolor=COLORS["plot_bg"],
        font=dict(family=FONT_FAMILY, color=COLORS["grey"], size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(autorange="reversed"),  # highest count at top
        height=200,
    )

    col1.plotly_chart(fig, width="stretch")

st.divider()