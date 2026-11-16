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

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="NYC Uber Pickup Explorer", page_icon="🚕", layout="wide")

DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

@st.cache_data(show_spinner="Loading the example pickup data...")
def load_data(number_of_rows=100_000):
    """Load a portion of the public dataset, no API key or local file needed."""
    data = pd.read_csv(DATA_URL, nrows=number_of_rows)
    data.columns = [str(name).lower() for name in data.columns]
    data["date/time"] = pd.to_datetime(data["date/time"], errors="coerce")
    data = data.dropna(subset=["date/time", "lat", "lon"]).copy()
    data["date"] = data["date/time"].dt.date
    data["hour"] = data["date/time"].dt.hour
    return data


def make_map(points, visualization="heat"):
    """Make either a 2D density heat map or a 3D hexagon map."""
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
    else:
        layer = pdk.Layer(
            "HeatmapLayer",
            data=points,
            get_position="[lon, lat]",
            get_weight=1,
            radius_pixels=55,
        )
    return pdk.Deck(
        map_style=None,  # Match the Streamlit theme. No API key required.
        initial_view_state=pdk.ViewState(
            latitude=40.75, longitude=-73.98, zoom=10.5, pitch=42 if visualization == "3d" else 0
        ),
        layers=[layer],
    )

st.title("🚕 Uber pickups in New York City")
st.write(
    "Explore *historical* Uber pickup locations from September 2014. "
    "Choose a date and hour, then watch how concentrations of pickups "
    "change during the day."
)
st.caption("Demonstration project for BA261 — no programming background required to explore it.")

try:
    data = load_data()
except Exception as error:
    st.error("The example dataset could not be downloaded at this time.")
    st.info("Check the internet connection or try again later. The data source is linked below.")
    st.stop()

available_dates = sorted(data["date"].unique())
selected_date = st.selectbox("Date to explore", available_dates, format_func=lambda d: d.strftime("%B %d, %Y"))
selected_hour = st.slider("Hour of day (24-hour clock)", 0, 23, 17)
daily_data = data[data["date"] == selected_date]
hour_data = daily_data[daily_data["hour"] == selected_hour]

m1, m2, m3 = st.columns(3)
m1.metric("Pickups in selected date", f"{len(daily_data):,}")
m2.metric("Pickups in selected hour", f"{len(hour_data):,}")
m3.metric("Time shown", f"{selected_hour:02d}:00–{(selected_hour + 1):02d}:00")

st.subheader("Pickups by hour")
counts = np.bincount(daily_data["hour"].to_numpy(), minlength=24)
hourly_counts = pd.DataFrame({"Hour": range(24), "Pickups": counts})
st.bar_chart(hourly_counts.set_index("Hour"))

st.subheader("Map for your selected hour")
map_kind = st.radio("Map style", ["2D heat map", "3D hexagons"], horizontal=True)
st.pydeck_chart(make_map(hour_data, "3d" if map_kind == "3D hexagons" else "heat"), height=440)
st.caption("Bright clusters or tall columns indicate higher concentrations of pickup locations.")

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
        movie_area.pydeck_chart(make_map(current), height=440, key="daily_animation_map")
        time.sleep(seconds_per_hour)
    st.success("The 24-hour animation is complete. Press Play to watch it again.")

if st.checkbox("Show the first 100 data rows"):
    st.dataframe(daily_data.head(100))

st.markdown("---")
st.caption(
    "Source: Streamlit's public Uber pickup tutorial and September 2014 dataset. "
    "Only the first 100,000 records in the original file are loaded, so dates "
    "near the end of this sample may be incomplete. "
    "Patterns in a historical sample do not establish causes."
)
st.markdown(
    "[Streamlit tutorial](https://docs.streamlit.io/get-started/tutorials/create-an-app) | "
    "[Original demo repository and dataset](https://github.com/streamlit/demo-uber-nyc-pickups)"
)
