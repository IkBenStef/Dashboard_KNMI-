import streamlit as st
import pandas as pd
import locale
import plotly.graph_objects as go
import plotly.express as px
from data_loader import get_cbsodata_energie
from data_loader import load_knmi_data
from stations import station_dict
import datetime

st.sidebar.header("Instellingen")
selected_station_name = st.sidebar.selectbox("Selecteer station",list(station_dict.keys()))
station = station_dict[selected_station_name]
df, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain, z = load_knmi_data(station=station)


df_energie = get_cbsodata_energie()
df_energie = df_energie[~df_energie['Perioden'].str.contains('1e|2e|3e|4e', na=False)]
df_energie = df_energie[df_energie['Perioden'].str.count(' ') == 1]

maand_map = {"januari": 1, "februari": 2, "maart": 3, "april": 4,"mei": 5, "juni": 6, "juli": 7, "augustus": 8,"september": 9, "oktober": 10, "november": 11, "december": 12,}
df_energie[['jaar', 'maand']] = df_energie['Perioden'].str.split(' ', n=1, expand=True)
df_energie['maand'] = df_energie['maand'].str.strip()
df_energie['date'] = pd.to_datetime({'year': df_energie['jaar'].astype(int),'month': df_energie['maand'].map(maand_map),'day': 1}, errors='coerce')


st.header('Energie dataframe van cbsodata')
st.dataframe(df_energie)

energy_cols = ['Kernenergie_4', 'Kolen_6', 'Olieproducten_7', 'Aardgas_8', 'Biomassa_9', 'Waterkracht_11', 'WindenergieTotaal_12', 'Zonnestroom_15']

EnergieProductie = go.Figure()

for col in energy_cols:
    EnergieProductie.add_trace(go.Scatter(
        x=df_energie['date'],
        y=df_energie[col],
        mode='lines+markers',
        name=col,  # Gebruikt de kolomnaam als label in de legenda
        yaxis='y1'
    ))

EnergieProductie.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="KiloWatt"),
    title="Verschillende Energie Producties in Nederland",
    xaxis=dict(range=['2000-01-01', df_energie['date'].max() + pd.DateOffset(years=1)])
)


st.plotly_chart(EnergieProductie, use_container_width=True)

EnergieProductieTot = go.Figure()

EnergieProductieTot.add_trace(go.Scatter(
    x=df_energie['date'],
    y=df_energie['BrutoProductie_1'],
    mode='lines+markers', 
    yaxis='y1'
))

EnergieProductieTot.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="KiloWatt"),
    title="Totale Energie Productie in Nederland",
    xaxis=dict(range=['1975-01-01', df_energie['date'].max() + pd.DateOffset(years=1)])
)
st.plotly_chart(EnergieProductieTot, use_container_width=True)

st.divider()

st.header('Samengevoegde Dataframe')
df_knmi_energie = pd.merge(df, df_energie, on='date', how='inner')
st.dataframe(df_knmi_energie)

st.header("Heatmap correlatie energie en KNMI (met waarden)")
# Selecteer kolommen voor correlatie
corr_cols = ['Temperatuur_C', 'Neerslag_MM', 'BrutoProductie_1'] + energy_cols
corr_matrix = df_knmi_energie[corr_cols].corr()

# Maak de heatmap met tekst in vakjes
heatmap_fig = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    colorscale='RdBu',
    zmin=-1, zmax=1,
    text=corr_matrix.round(2).values,
    texttemplate="%{text}",
    colorbar=dict(title="Correlatie")
))

heatmap_fig.update_layout(
    template="plotly_white",
    title="Correlatie tussen energieproductie en KNMI-gegevens"
)

st.plotly_chart(heatmap_fig, use_container_width=True)

st.divider() # ------------------------------------------------------------------------------- vanaf hier grafieken

# corrolatie waterenergie temperatuur
Corr_water = go.Figure()
Corr_water.add_trace(go.Line(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Temperatuur_C'],
    name='Gemiddelde temperatuur',
    mode='lines+markers',
))
Corr_water.add_trace(go.Line(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Waterkracht_11'],
    name='Opwekking Waterkracht',
    mode='lines+markers',
))


Corr_water.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Gemiddelde temperatuur (°C)",
    title="Corrolatie waterkracht <-> Temperatuur",
    xaxis=dict(range=['2014-01-01', df_energie['date'].max() + pd.DateOffset(years=1)])
)
st.plotly_chart(Corr_water, use_container_width=True)
# corrolatie zonnenenergie temperatuur
Corr_zon = go.Figure()
Corr_zon.add_trace(go.Line(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Temperatuur_C'],
    name='Gemiddelde temperatuur',
    mode='lines+markers',
))
Corr_zon.add_trace(go.Line(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Zonnestroom_15']/100,
    name='Opwekking Zonnestroom',
    mode='lines+markers',
))


Corr_zon.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Gemiddelde temperatuur (°C)",
    title="Corrolatie Zonnestroom <-> Temperatuur",
    xaxis=dict(range=['2014-01-01', df_energie['date'].max() + pd.DateOffset(years=1)])
)
st.plotly_chart(Corr_zon, use_container_width=True)
