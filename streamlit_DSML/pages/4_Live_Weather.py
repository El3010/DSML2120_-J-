import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Live Weather (Open-Meteo)", page_icon="🌤️", layout="wide")

# Disable fade/transition so charts don't blink between reruns
st.markdown(
    """
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌤️ Live Weather — Denver (Open-Meteo)")
st.caption("Current temperature from Open-Meteo, cached and collected into a time series.")

# ---------------- Config ----------------
lat, lon = 39.7392, -104.9903  # Denver
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

# timezone=auto makes the returned times local (Denver) instead of GMT
wurl = (
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    f"&current=temperature_2m,wind_speed_10m&timezone=auto"
)

# Hourly temperatures for the past day, so the chart has a real trend right away
hurl = (
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    f"&hourly=temperature_2m&past_days=1&forecast_days=1&timezone=auto"
)


# ---------------- Fetch (cached) ----------------
@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def get_weather():
    """Return (df, error_message). Never raise."""
    try:
        r = requests.get(wurl, timeout=10, headers=HEADERS)
        r.raise_for_status()
        j = r.json()["current"]
        df = pd.DataFrame(
            [
                {
                    "time": pd.to_datetime(j["time"]),
                    "temperature": j["temperature_2m"],
                    "wind": j["wind_speed_10m"],
                }
            ]
        )
        return df, None
    except (requests.RequestException, KeyError, ValueError) as e:
        return None, f"Weather API error: {e}"


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def get_hourly():
    """Hourly temps (past 24h up to now). Return (df, error_message)."""
    try:
        r = requests.get(hurl, timeout=10, headers=HEADERS)
        r.raise_for_status()
        h = r.json()["hourly"]
        df = pd.DataFrame({"time": pd.to_datetime(h["time"]), "temperature": h["temperature_2m"]})
        now = pd.Timestamp.now(tz="America/Denver").tz_localize(None)
        df = df[(df["time"] <= now) & (df["time"] >= now - pd.Timedelta(hours=24))]
        return df, None
    except (requests.RequestException, KeyError, ValueError) as e:
        return None, f"Hourly API error: {e}"


# ---------------- Session-state history ----------------
if "weather_history" not in st.session_state:
    st.session_state.weather_history = pd.DataFrame(columns=["time", "temperature", "wind"])

# ---------------- Refresh controls ----------------
st.subheader("🔁 Auto Refresh Settings")
c1, c2 = st.columns([3, 1])
refresh_sec = c1.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = c2.toggle("Enable auto-refresh", value=False)
if c2.button("Clear history"):
    st.session_state.weather_history = st.session_state.weather_history.iloc[0:0]
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# ---------------- Main view ----------------
df, err = get_weather()

if err:
    st.warning(f"{err}\nShowing the readings collected so far.")
else:
    hist = st.session_state.weather_history
    # Only add a row when the API reports a new observation time
    if hist.empty or df["time"].iloc[0] not in set(hist["time"]):
        st.session_state.weather_history = pd.concat([hist, df], ignore_index=True).tail(100)

hist = st.session_state.weather_history

# Metrics
if not hist.empty:
    latest = hist.iloc[-1]
    temp_delta = None
    if len(hist) > 1:
        temp_delta = f"{latest['temperature'] - hist.iloc[-2]['temperature']:+.1f} °C"
    m1, m2, m3 = st.columns(3)
    m1.metric("Temperature", f"{latest['temperature']:.1f} °C", temp_delta)
    m2.metric("Wind speed", f"{latest['wind']:.1f} km/h")
    m3.metric("Observed at", pd.to_datetime(latest["time"]).strftime("%H:%M"))

# Chart 1: past 24 hours (hourly)
hourly, herr = get_hourly()
if herr:
    st.info(herr)
elif not hourly.empty:
    fig24 = px.line(
        hourly,
        x="time",
        y="temperature",
        markers=True,
        title="Temperature — past 24 hours (hourly)",
        labels={"time": "Time", "temperature": "Temperature (°C)"},
    )
    st.plotly_chart(fig24, use_container_width=True)

# Chart 2: live readings collected this session
st.subheader("Live readings this session")
if hist.empty:
    st.info("No readings yet — the API may be unavailable.")
else:
    fig = px.line(
        hist,
        x="time",
        y="temperature",
        markers=True,
        title="Current temperature over time (session history)",
        labels={"time": "Time", "temperature": "Temperature (°C)"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Open-Meteo updates 'current' data about every 15 minutes, "
        "so a new point appears only when a new observation arrives."
    )
    st.dataframe(hist, use_container_width=True)

# If auto-refresh is ON, wait and rerun the app
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()
