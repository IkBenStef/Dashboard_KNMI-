import pandas as pd
import numpy as np
import requests
import streamlit as st
import io
import cbsodata

@st.cache_data
def load_knmi_data(station="260"):
    url = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"
    params = {"stns": station, "vars": "TG:RH:FG", "start": "19000101", "end": "20251231"}
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
    csv_data = header_line + "\n" + "\n".join(data_lines)
    df_meteorologisch = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True)

    # Datum correct zetten
    df_meteorologisch['YYYYMMDD'] = pd.to_datetime(df_meteorologisch['YYYYMMDD'], format='%Y%m%d')
    df_meteorologisch.rename(columns={'YYYYMMDD': 'date'}, inplace=True)

    # Eenheden corrigeren
    df_meteorologisch['Temperatuur_C'] = df_meteorologisch['TG'] * 0.1
    df_meteorologisch['Neerslag_MM'] = df_meteorologisch['RH'] * 0.1
    df_meteorologisch['Windsnelheid_ms'] = df_meteorologisch['FG'] * 0.1

    df_meteorologisch['year'] = df_meteorologisch['date'].dt.year
    df_meteorologisch['month'] = df_meteorologisch['date'].dt.month

    # Jaarlijkse groepering
    df_yearly_temp = df_meteorologisch.groupby('year')['Temperatuur_C'].mean().reset_index()
    df_yearly_rain = df_meteorologisch.groupby('year')['Neerslag_MM'].sum().reset_index()
    # Maandelijkse groepering
    df_monthly_temp = df_meteorologisch.groupby(['year', 'month'])['Temperatuur_C'].mean().reset_index()
    df_monthly_rain = df_meteorologisch.groupby(['year', 'month'])['Neerslag_MM'].sum().reset_index()

    return df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain

@st.cache_data(ttl=1800)
def load_weather_forecast(latitude, longitude):
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
    url = (f"https://nominatim.openstreetmap.org/reverse"f"?lat={latitude}&lon={longitude}&format=json")
    headers = {"User-Agent": "streamlit-weather-app"}
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

def get_cbsodata_energie():
    dataset = ('84575NED')
    data = cbsodata.get_data(dataset)
    df_energie = pd.DataFrame(data)
    return df_energie
