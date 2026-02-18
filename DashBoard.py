import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

# --- Titel ---
st.title("KNMI Temperatuur Dashboard")
st.markdown("Jaargemiddelde temperatuur in Nederland met trendlijn")

# --- API settings ---
API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVlNDFjMWI0MjlkODQ2MThiNWI4ZDViZDAyMTM2YTM3IiwiaCI6Im11cm11cjEyOCJ9"
dataset = "homogenization_daily_temperature_principal_stations_netherlands"
version = "1.0"

headers = {"Authorization": API_KEY}

# --- Haal lijst van bestanden ---
url = f"https://api.dataplatform.knmi.nl/open-data/v1/datasets/{dataset}/versions/{version}/files"
response = requests.get(url, headers=headers)
response.raise_for_status()
files = response.json()["files"]
df_files = pd.DataFrame(files)

# --- Kies eerste CSV file ---
csv_file = df_files.iloc[0]["filename"]
download_url_endpoint = f"https://api.dataplatform.knmi.nl/open-data/v1/datasets/{dataset}/versions/{version}/files/{csv_file}/url"
download_url = requests.get(download_url_endpoint, headers=headers).json()["temporaryDownloadUrl"]

# --- Lees CSV in DataFrame ---
df_temp = pd.read_csv(download_url)

# --- Datum & jaar verwerken ---
df_temp['date'] = pd.to_datetime(df_temp['date'])
df_temp['year'] = df_temp['date'].dt.year
df_temp['year_month'] = df_temp['date'].dt.to_period('M').dt.to_timestamp()

# --- Bereken gemiddelde per jaar en per maand ---
df_yearly = df_temp.groupby('year')['original'].mean().reset_index()
df_monthly = df_temp.groupby('year_month')['original'].mean().reset_index()

# --- Trend berekenen ---
z = np.polyfit(df_yearly['year'], df_yearly['original'], 1)
p = np.poly1d(z)
df_yearly['trend'] = p(df_yearly['year'])

# --- Sidebar filters ---
st.sidebar.header("Filters")
min_year = int(df_yearly['year'].min())
max_year = int(df_yearly['year'].max())
selected_year_range = st.sidebar.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

df_filtered = df_yearly[(df_yearly['year'] >= selected_year_range[0]) & 
                        (df_yearly['year'] <= selected_year_range[1])]

# --- Plotly grafiek ---
fig = go.Figure()

# Originele lijn
fig.add_trace(go.Scatter(
    x=df_filtered['year'],
    y=df_filtered['original'],
    mode='lines+markers',
    name='Gemiddelde temperatuur'
))

# Trendlijn
fig.add_trace(go.Scatter(
    x=df_filtered['year'],
    y=p(df_filtered['year']),
    mode='lines',
    name='Trend',
    line=dict(dash='dash')
))

fig.update_layout(
    template='plotly_white',
    title='Jaargemiddelde temperatuur met trend',
    xaxis_title='Jaar',
    yaxis_title='Gemiddelde temperatuur (°C)',
    title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)

# --- Toon stijging per jaar ---
st.markdown(f"**Gemiddelde stijging per jaar:** {z[0]:.4f} °C")
