import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_weather_forecast, get_location_name
from datetime import datetime
import folium
from streamlit_folium import st_folium

st.title("Weer voorspelling")

# Standaard startlocatie (Nederland)
start_lat = 52.37
start_lon = 4.89

# =
# Kaart om een locatie te kiezen
# =
m = folium.Map(location=[start_lat, start_lon], zoom_start=7)

with st.sidebar:
    st.write('Kies een plek op de kaart')
    map_data = st_folium(m, width=300, height=400)

if map_data and map_data["last_clicked"]:
    latitude = map_data["last_clicked"]["lat"]
    longitude = map_data["last_clicked"]["lng"]
else:
    latitude = start_lat
    longitude = start_lon
data = load_weather_forecast(latitude, longitude)
if map_data and map_data["last_clicked"]:
    folium.Marker(
        [latitude, longitude],
        tooltip="Geselecteerde locatie"
    ).add_to(m)

# =
# HUIDIGE TEMPERATUUR
# =

current_temp = data["hourly"]["temperature_2m"][0]

st.markdown(f"## 🌡️ {current_temp} °C")
location_name = get_location_name(latitude, longitude)
st.markdown(f"📍 {location_name} — {datetime.now().strftime('%d %B %Y')}")

st.divider()

# =
# UURDATA VAN VANDAAG
# =

hourly_df = pd.DataFrame({
    "time": pd.to_datetime(data["hourly"]["time"]),
    "temperature": data["hourly"]["temperature_2m"],
    "precipitation": data["hourly"]["precipitation"]
})

today = datetime.now().date()
hourly_today = hourly_df[hourly_df["time"].dt.date == today]

# Temperatuur grafiek
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(
    x=hourly_today["time"],
    y=hourly_today["temperature"],
    mode="lines+markers",
    name="Temperatuur"
))

fig_temp.update_layout(
    template="plotly_white",
    title="Temperatuur per uur (vandaag)",
    xaxis_title="Tijd",
    yaxis_title="°C"
)

st.plotly_chart(fig_temp, use_container_width=True)

# Regen grafiek
fig_rain = go.Figure()
fig_rain.add_trace(go.Bar(
    x=hourly_today["time"],
    y=hourly_today["precipitation"],
    name="Neerslag (mm)"
))

fig_rain.update_layout(
    template="plotly_white",
    title="Neerslag per uur (aankomende 24 uur)",
    xaxis_title="Tijd",
    yaxis_title="mm"
)

st.plotly_chart(fig_rain, use_container_width=True)

st.divider()

# =
# 7-DAAGSE FORECAST
# =

st.subheader("7-daagse voorspelling")

daily_df = pd.DataFrame({
    "date": pd.to_datetime(data["daily"]["time"]),
    "temp_max": data["daily"]["temperature_2m_max"],
    "temp_min": data["daily"]["temperature_2m_min"],
    "rain": data["daily"]["precipitation_sum"]
})

cols = st.columns(7)

for i, col in enumerate(cols):
    with col:
        st.markdown(f"**{daily_df['date'][i].strftime('%a')}**")
        st.markdown(f"{daily_df['temp_max'][i]}° / {daily_df['temp_min'][i]}°")

        st.markdown(f"🌧️ {daily_df['rain'][i]} mm")
