import pandas as pd
import numpy as np
import requests
import streamlit as st
import io

@st.cache_data
def load_knmi_data(station="260"):
    url = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"

    params = {
    "stns": station,
    "vars": "TG:RH",     
    "start": "19000101",
    "end": "20251231"
}

    response = requests.post(url, data=params)

    if response.status_code != 200:
        raise Exception("Fout bij ophalen KNMI data")

    lines = response.text.splitlines()

    data_lines = []
    header_line = ""

    for line in lines:
        if line.startswith('# STN'):
            header_line = line.replace('#', '').strip()
        elif not line.startswith('#') and line.strip():
            data_lines.append(line)
    print(response.status_code)
    print(response.text)
    csv_data = header_line + "\n" + "\n".join(data_lines)
    df = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True)

    # Datum correct zetten
    df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
    df.rename(columns={'YYYYMMDD': 'date'}, inplace=True)

    # Eenheden corrigeren
    df['Temperatuur_C'] = df['TG'] * 0.1
    df['Neerslag_MM'] = df['RH'] * 0.1

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Jaarlijkse gemiddelden temperatuur
    df_yearly_temp = df.groupby('year')['Temperatuur_C'].mean().reset_index()

    # Maandelijkse gemiddelden temperatuur
    df_monthly_temp = df.groupby(['year', 'month'])['Temperatuur_C'].mean().reset_index()

    # Jaarlijkse totale neerslag
    df_yearly_rain = df.groupby('year')['Neerslag_MM'].sum().reset_index()

    # Trend berekenen
    z = np.polyfit(df_yearly_temp['year'], df_yearly_temp['Temperatuur_C'], 1)
    p = np.poly1d(z)
    df_yearly_temp['trend'] = p(df_yearly_temp['year'])

    return df, df_yearly_temp, df_monthly_temp, df_yearly_rain, z

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