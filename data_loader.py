import pandas as pd
import numpy as np
import requests
import streamlit as st
import io
import cbsodata

# knmi meteorologisch api = https://www.knmi.nl/nederland-nu/klimatologie/daggegevens
# cbsodata energie    api = https://opendata.cbs.nl/portal.html?_la=nl&_catalog=CBS&tableId=83140NED&_theme=123
# meteo voorspelling  api = https://open-meteo.com/

@st.cache_data
def load_knmi_data(station="260"):
    url = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"
    params = {"stns": station, "vars": "TG:TX:TN:RH:FG", "start": "19000101", "end": "20251231"}
    response = requests.post(url, data=params)
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

    # Eenheden corrigeren met nieuwe kolommen
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

def get_location_name(latitude, longitude):
    url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "localityLanguage": "gb"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return "Onbekende locatie"

    data = response.json()
    admin = data.get("localityInfo", {}).get("administrative", [])
    #st.write(data)
    stad = admin[4]["name"]
    gemeente = admin[3]["name"]
    provincie = admin[2]["name"]
    land = admin[1]["name"]

    plek = stad + ', ' + gemeente + ', ' + provincie + ', ' + land
    return plek

@st.cache_data
def get_cbsodata_energie():
    dataset_energie = ('84575NED')
    df_energie = pd.DataFrame(cbsodata.get_data(dataset_energie))
    return df_energie






