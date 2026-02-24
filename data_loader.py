import pandas as pd
import numpy as np
import requests
import streamlit as st


API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjIyNzBkZTRmNWRiNzRjM2ZhYWI3NzdjNjMwYjc2MzVmIiwiaCI6Im11cm11cjEyOCJ9"
dataset = "homogenization_daily_temperature_principal_stations_netherlands"
version = "1.0"
headers = {"Authorization": API_KEY}


@st.cache_data
def load_knmi_data():
    # --- Haal bestanden op ---
    url = f"https://api.dataplatform.knmi.nl/open-data/v1/datasets/{dataset}/versions/{version}/files"
    files = requests.get(url, headers=headers).json()["files"]
    df_files = pd.DataFrame(files)

    csv_file = df_files.iloc[0]["filename"]

    download_url_endpoint = f"https://api.dataplatform.knmi.nl/open-data/v1/datasets/{dataset}/versions/{version}/files/{csv_file}/url"
    download_url = requests.get(download_url_endpoint, headers=headers).json()["temporaryDownloadUrl"]

    df_temp = pd.read_csv(download_url)

    # --- Datum verwerken ---
    df_temp['date'] = pd.to_datetime(df_temp['date'])
    df_temp['year'] = df_temp['date'].dt.year
    df_temp['month'] = df_temp['date'].dt.month

    # --- Gemiddelden ---
    df_yearly = df_temp.groupby('year')['original'].mean().reset_index()
    df_monthly = df_temp.groupby(['year', 'month'])['original'].mean().reset_index()

    # --- Trend ---
    z = np.polyfit(df_yearly['year'], df_yearly['original'], 1)
    p = np.poly1d(z)
    df_yearly['trend'] = p(df_yearly['year'])

    return df_temp, df_yearly, df_monthly, z



@st.cache_data(ttl=1800)
def load_weather_forecast(latitude, longitude):
    import requests
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,precipitation"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )
    
    response = requests.get(url)
    data = response.json()
    
    return data
@st.cache_data(ttl=1800)

def get_location_name(latitude, longitude):
    import requests
    
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?lat={latitude}&lon={longitude}&format=json"
    )
    
    headers = {
        "User-Agent": "streamlit-weather-app"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    address = data.get("address", {})
    
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or "Onbekende locatie"
    )
    
    return city