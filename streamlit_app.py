"""Optional BA261 activity: explore New York City Uber pickups with Streamlit.

Source data and original concept: Streamlit's Uber NYC tutorial
https://docs.streamlit.io/get-started/tutorials/create-an-app
https://github.com/streamlit/demo-uber-nyc-pickups

Workshop guidance: Chris L. Santo, Scottsdale Community College,
NITIC Summer Working Connections, Advanced Data Analytics with Python, APIs and AI,
Columbus, Ohio, June 1-4, 2026.

Animated heat map and related classroom exploration:
Professor Brian Daily, BA261, with AI-assisted development.

This demonstration uses public, historical sample data from September 2014.
"""

import time

import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="NYC Uber Pickup Explorer", page_icon="🚕", layout="wide")

DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

LOCATION_PRESETS = {
    "NYC Overview (Manhattan)": {"latitude": 40.75, "longitude": -73.98, "zoom": 10.5},
    "Midtown Manhattan": {"latitude": 40.7549, "longitude": -73.9840, "zoom": 13.0},
    "JFK Airport": {"latitude": 40.6413, "longitude": -73.7781, "zoom": 13.0},
    "LaGuardia Airport (LGA)": {"latitude": 40.7769, "longitude": -73.8740, "zoom": 13.2},
    "Williamsburg, Brooklyn": {"latitude": 40.7081, "longitude": -73.9571, "zoom": 13.0},
}


@st.cache_data(show_spinner="Loading the example pickup data...")
def load_data(number_of_rows=250_000):
    """Load a portion of the public dataset and drop incomplete trailing dates."""
    data = pd.read_csv(DATA_URL, nrows=number_of_rows)
    data.columns = [str(name).lower() for name in data.columns]
    data["date/time"] = pd.to_datetime(data["date/time"], errors="coerce")
    data = data.dropna(subset=["date/time", "lat", "lon"]).copy()
    data["date"] = data["date/time"].dt.date
    data["hour"] = data["date/time"].dt.hour
    data["day_name"] = data["date/time"].dt.day_name()
    data["day_type"] = np.where(
        data["date/time"].dt.dayofweek >= 5, "Weekend (Sat–Sun)", "Weekday (Mon–Fri)"
    )

    # Drop the final date if the row limit cut it off mid-day
    unique_dates = sorted(data["date"].unique())
    if len(unique_dates) > 1:
        last_date_max_hour = data.loc[data["date"] == unique_dates[-1], "hour"].max()
        if last_date_max_hour < 23:
            data = data[data["date"] != unique_dates[-1]].copy()

    return data


def make_map(points, visualization="heat", view_preset=None):
    """Make either a 2D density heat map or a 3D hexagon map with tooltips."""
    if view_preset is None:
        view_preset = LOCATION_PRESETS["NYC Overview (Manhattan)"]

    if visualization == "3d":
        layer = pdk.Layer(
            "HexagonLayer",
            data=points,
            get_position="[lon, lat]",
            radius=210,
            elevation_scale=15,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        )
        tooltip = {
            "html": "<b>Pickups in this zone:</b> {elevationValue}",
            "style": {"backgroundColor": "#1E1E1E", "color": "#FFD700", "fontSize": "13px"},
        }
    else:
        layer = pdk.Layer(
            "HeatmapLayer",
            data=points,
            get_position="[lon, lat]",
            get_weight=1,
            radius_pixels=55,
        )
        tooltip = None

    return pdk.Deck(
        map_style=None,  # Match the Streamlit theme. No API key required.
        initial_view_state=pdk.ViewState(
            latitude=view_preset["latitude"],
            longitude=view_preset["longitude"],
            zoom=view_preset["zoom"],
            pitch=42 if visualization == "3d" else 0,
        ),
        layers=[layer],
        tooltip=tooltip,
    )


st.title("🚕 Uber Pickups in New York City")
st.write(
    "Explore *historical* Uber pickup locations from September 2014. "
    "Use the sidebar controls to filter by date, hour, and neighborhood hotspot."
)
st.caption("Demonstration project for BA261 — no programming background required to explore it.")

# Sidebar Controls
st.sidebar.header("⚙️ Explorer Controls")
row_limit = st.sidebar.slider(
    "Sample size (rows loaded)",
    min_value=100_000,
    max_value=1_000_000,
    value=250_000,
    step=50_000,
    help="Increase to load more days of September 2014 data.",
)

try:
    data = load_data(row_limit)
except Exception:
    st.error("The example dataset could not be downloaded at this time.")
    st.info("Check the internet connection or try again later. The data source is linked below.")
    st.stop()

available_dates = sorted(data["date"].unique())
selected_date = st.sidebar.selectbox(
    "Date to explore",
    available_dates,
    format_func=lambda d: d.strftime("%A, %B %d, %Y"),
)
selected_hour = st.sidebar.slider("Hour of day (24-hour clock)", 0, 23, 17)
map_kind = st.sidebar.radio("Map style", ["2D heat map", "3D hexagons"], horizontal=True)
selected_location = st.sidebar.selectbox("Location jump", list(LOCATION_PRESETS.keys()))
view_preset = LOCATION_PRESETS[selected_location]

# Filtered data & benchmarks
daily_data = data[data["date"] == selected_date]
hour_data = daily_data[daily_data["hour"] == selected_hour]

avg_daily_pickups = data.groupby("date").size().mean()
avg_hourly_for_selected_hour = (
    data[data["hour"] == selected_hour].groupby("date").size().mean()
)

# Top KPI Cards with Deltas
m1, m2, m3 = st.columns(3)
m1.metric(
    "Pickups on selected date",
    f"{len(daily_data):,}",
    delta=f"{len(daily_data) - avg_daily_pickups:+,.0f} vs. daily avg",
)
m2.metric(
    f"Pickups at {selected_hour:02d}:00",
    f"{len(hour_data):,}",
    delta=f"{len(hour_data) - avg_hourly_for_selected_hour:+,.0f} vs. {selected_hour:02d}:00 avg",
)
m3.metric(
    "Time window shown",
    f"{selected_hour:02d}:00–{(selected_hour + 1) % 24:02d}:00",
    delta=daily_data["day_type"].iloc[0] if not daily_data.empty else "",
    delta_color="off",
)

# Main Content Tabs
tab_map, tab_anim, tab_trends, tab_data = st.tabs(
    ["🗺️ Interactive Map", "🎬 24-Hour Animation", "📈 Weekday vs. Weekend", "📊 Raw Data"]
)

with tab_map:
    col_chart, col_map = st.columns([1, 1.35], gap="large")

    with col_chart:
        st.subheader("Hourly demand curve")
        counts = np.bincount(daily_data["hour"].to_numpy(), minlength=24)
        hourly_counts = pd.DataFrame(
            {
                "Hour": range(24),
                "Pickups": counts,
                "Selected": ["Selected Hour" if h == selected_hour else "Other Hours" for h in range(24)],
            }
        )

        bar_chart = (
            alt.Chart(hourly_counts)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("Hour:O", title="Hour of Day (0–23)", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Pickups:Q", title="Number of Pickups"),
                color=alt.Color(
                    "Selected:N",
                    scale=alt.Scale(
                        domain=["Selected Hour", "Other Hours"],
                        range=["#F7B731", "#95A5A6"],
                    ),
                    legend=None,
                ),
                tooltip=["Hour", "Pickups"],
            )
            .properties(height=390)
        )
        st.altair_chart(bar_chart, use_container_width=True)
        st.caption("Gold bar highlights the currently selected hour in the sidebar.")

    with col_map:
        st.subheader(f"Map: {selected_location}")
        st.pydeck_chart(
            make_map(
                hour_data,
                "3d" if map_kind == "3D hexagons" else "heat",
                view_preset=view_preset,
            ),
            height=410,
        )
        if map_kind == "3D hexagons":
            st.caption("Hover over any 3D column to see exact pickup counts in that zone.")
        else:
            st.caption("Brighter clusters indicate higher concentrations of pickup locations.")

with tab_anim:
    st.subheader("▶ 24-hour animated heat map")
    st.write(
        "Press Play to watch the selected date progress from midnight (00:00) "
        "through 11 p.m. (23:00). The animation runs once and then stops."
    )
    seconds_per_hour = st.slider("Animation speed (seconds per hour)", 0.2, 1.0, 0.5, 0.1)
    if st.button("▶ Play one full day"):
        status_area = st.empty()
        movie_area = st.empty()
        for hour in range(24):
            current = daily_data[daily_data["hour"] == hour]
            status_area.markdown(
                f"**{selected_date:%B %d, %Y} — {hour:02d}:00** — {len(current):,} pickups"
            )
            movie_area.pydeck_chart(
                make_map(current, visualization="heat", view_preset=view_preset),
                height=460,
                key="daily_animation_map",
            )
            time.sleep(seconds_per_hour)
        st.success("The 24-hour animation is complete. Press Play to watch it again.")

with tab_trends:
    st.subheader("Weekday vs. Weekend Demand Patterns")
    st.write(
        "Compare average hourly pickups across weekdays (Monday–Friday) versus weekends (Saturday–Sunday) "
        "to spot commuter rush hours vs. late-night entertainment demand."
    )
    avg_by_type = (
        data.groupby(["day_type", "hour", "date"])
        .size()
        .reset_index(name="pickups")
        .groupby(["day_type", "hour"])["pickups"]
        .mean()
        .reset_index()
    )

    line_chart = (
        alt.Chart(avg_by_type)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("hour:O", title="Hour of Day (0–23)", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("pickups:Q", title="Average Pickups per Hour"),
            color=alt.Color(
                "day_type:N",
                title="Day Type",
                scale=alt.Scale(
                    domain=["Weekday (Mon–Fri)", "Weekend (Sat–Sun)"],
                    range=["#2E86DE", "#F7B731"],
                ),
            ),
            tooltip=["day_type", "hour", alt.Tooltip("pickups:Q", format=",.0f")],
        )
        .properties(height=400)
    )
    st.altair_chart(line_chart, use_container_width=True)

with tab_data:
    st.subheader(f"Sample Records for {selected_date:%B %d, %Y}")
    st.write(f"Showing the first 100 of **{len(daily_data):,}** pickups recorded on this date.")
    st.dataframe(daily_data.head(100), use_container_width=True)

st.markdown("---")
st.caption(
    "Source: Streamlit's public Uber pickup tutorial and September 2014 dataset. "
    "Incomplete trailing dates from partial row loads are automatically excluded. "
    "Patterns in a historical sample do not establish causes."
)
st.markdown(
    "[Streamlit tutorial](https://docs.streamlit.io/get-started/tutorials/create-an-app) | "
    "[Original demo repository and dataset](https://github.com/streamlit/demo-uber-nyc-pickups)"
)
