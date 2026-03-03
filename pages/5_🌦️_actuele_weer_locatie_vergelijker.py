import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_weather_forecast, get_location_name
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
 
st.set_page_config(page_title="Locatie Weer Vergelijking", layout="wide")
st.header('Locatie Weer Vegelijking')
defaults = {
    "loc1": {"lat": 52.37, "lon": 4.89, "name": "Amsterdam"},
    "loc2": {"lat": 40.71, "lon": -74.00, "name": "New York"}
}
 
col1, col2 = st.columns(2)
 
with col1:
    st.subheader("Locatie A")
    m1 = folium.Map(location=[defaults["loc1"]["lat"], defaults["loc1"]["lon"]], zoom_start=4)
    map_a = st_folium(m1, width=None, height=300, key="map_a")
   
    lat_a = map_a["last_clicked"]["lat"] if map_a and map_a["last_clicked"] else defaults["loc1"]["lat"]
    lon_a = map_a["last_clicked"]["lng"] if map_a and map_a["last_clicked"] else defaults["loc1"]["lon"]
   
    raw_data_a = load_weather_forecast(lat_a, lon_a)
    name_a = get_location_name(lat_a, lon_a)
    st.info(f"{name_a}: {raw_data_a['hourly']['temperature_2m'][0]}°C")
 
with col2:
    st.subheader("Locatie B")
    m2 = folium.Map(location=[defaults["loc2"]["lat"], defaults["loc2"]["lon"]], zoom_start=4)
    map_b = st_folium(m2, width=None, height=300, key="map_b")
   
    lat_b = map_b["last_clicked"]["lat"] if map_b and map_b["last_clicked"] else defaults["loc2"]["lat"]
    lon_b = map_b["last_clicked"]["lng"] if map_b and map_b["last_clicked"] else defaults["loc2"]["lon"]
   
    raw_data_b = load_weather_forecast(lat_b, lon_b)
    name_b = get_location_name(lat_b, lon_b)
    st.info(f"{name_b}: {raw_data_b['hourly']['temperature_2m'][0]}°C")
 
st.divider()
 
# --- 1. AANGEPASTE SLIDER ---
interval = st.select_slider(
    "Selecteer tijdsperiode",
    options=["Minuten", "Uur", "Week"],
    value="Uur",
    help="Minuten = komende 2u, Uur = komende 24u, Week = komende 7 dagen"
)
 
def prepare_data(data, interval_type):
    now = datetime.now()
    # Afronden naar het begin van het huidige uur voor een schone start
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
 
    if interval_type == "Minuten":
        df = pd.DataFrame({
            "time": pd.to_datetime(data["hourly"]["time"]),
            "temp": data["hourly"]["temperature_2m"],
            "wind": data["hourly"].get("wind_speed_10m", data["hourly"].get("windspeed_10m", 0)),
            "rain": data["hourly"]["precipitation"]
        })
        return df[df["time"] >= current_hour_start].head(2)
   
    elif interval_type == "Uur":
        df = pd.DataFrame({
            "time": pd.to_datetime(data["hourly"]["time"]),
            "temp": data["hourly"]["temperature_2m"],
            "wind": data["hourly"].get("wind_speed_10m", data["hourly"].get("windspeed_10m", 0)),
            "rain": data["hourly"]["precipitation"]
        })
        return df[df["time"] >= current_hour_start].head(24)
   
    else:
        df = pd.DataFrame({
            "time": pd.to_datetime(data["daily"]["time"]),
            "temp": data["daily"]["temperature_2m_max"],
            "wind": data["daily"].get("wind_speed_10m_max", data["daily"].get("windspeed_10m_max", 0)),
            "rain": data["daily"]["precipitation_sum"]
        })
        today_start = pd.Timestamp(now.date())
        return df[df["time"] >= today_start].head(7)
 
df_locatieA = prepare_data(raw_data_a, interval)
df_locatieB = prepare_data(raw_data_b, interval)
 
# --- Grafieken ---
 
st.subheader("Temperatuur Vergelijking (°C)")
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=df_locatieA["time"], y=df_locatieA["temp"], name=name_a, line=dict(color='#1f77b4', width=3)))
fig_temp.add_trace(go.Scatter(x=df_locatieB["time"], y=df_locatieB["temp"], name=name_b, line=dict(color='#ff7f0e', width=3)))
fig_temp.update_layout(template="plotly_white", hovermode="x unified", height=350)
st.plotly_chart(fig_temp, use_container_width=True)
 
st.subheader("Windsnelheid Vergelijking (km/h)")
fig_wind = go.Figure()
fig_wind.add_trace(go.Scatter(x=df_locatieA["time"], y=df_locatieA["wind"], name=name_a, line=dict(color='#1f77b4', dash='dot')))
fig_wind.add_trace(go.Scatter(x=df_locatieB["time"], y=df_locatieB["wind"], name=name_b, line=dict(color='#ff7f0e', dash='dot')))
fig_wind.update_layout(template="plotly_white", hovermode="x unified", height=300)
st.plotly_chart(fig_wind, use_container_width=True)
 
st.subheader("Neerslag Vergelijking (mm)")
fig_rain = go.Figure()
fig_rain.add_trace(go.Bar(x=df_locatieA["time"], y=df_locatieA["rain"], name=name_a, marker_color='#1f77b4', opacity=0.7))
fig_rain.add_trace(go.Bar(x=df_locatieB["time"], y=df_locatieB["rain"], name=name_b, marker_color='#ff7f0e', opacity=0.7))
fig_rain.update_layout(template="plotly_white", barmode='group', height=300)
st.plotly_chart(fig_rain, use_container_width=True)
 
st.divider()
 
with st.expander('Ruwe data'): 
    c_tab1, c_tab2 = st.columns(2)
    with c_tab1:
        st.write(f"Details {name_a}")
        st.dataframe(df_locatieA, use_container_width=True)
    with c_tab2:
        st.write(f"Details {name_b}")
        st.dataframe(df_locatieB, use_container_width=True)