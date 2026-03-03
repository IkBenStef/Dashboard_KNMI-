import streamlit as st
import pandas as pd
import locale
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from data_loader import get_cbsodata_energie
from data_loader import load_knmi_data
from stations import station_dict
import datetime

# ======================================================================================== Sidebar instellen
st.set_page_config(layout="wide")
st.sidebar.header("Instellingen")

selected_station_name = st.sidebar.selectbox("Selecteer station",list(station_dict.keys()))
station = station_dict[selected_station_name]

# ======================================================================================== Data ophalen
df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data(station=station)
df_energie = get_cbsodata_energie()
df_energie = df_energie[~df_energie['Perioden'].str.contains('1e|2e|3e|4e', na=False)]
df_energie = df_energie[df_energie['Perioden'].str.count(' ') == 1]

maand_map = {"januari": 1, "februari": 2, "maart": 3, "april": 4,"mei": 5, "juni": 6, "juli": 7, "augustus": 8,"september": 9, "oktober": 10, "november": 11, "december": 12,}

df_energie[['jaar', 'maand']] = df_energie['Perioden'].str.split(' ', n=1, expand=True)
df_energie['maand'] = df_energie['maand'].str.strip()

df_energie['date'] = pd.to_datetime({
    'year': df_energie['jaar'].astype(int),
    'month': df_energie['maand'].map(maand_map),
    'day': 1
}, errors='coerce')

# ======================================================================================== Jaarslider
min_year = int(df_energie['date'].dt.year.min())
max_year = int(df_energie['date'].dt.year.max())

default_start = max(2000, min_year)

selected_years = st.sidebar.slider(
    "Selecteer jaarbereik",
    min_value=min_year,
    max_value=max_year,
    value=(default_start, max_year)
)

start_year, end_year = selected_years

df_energie = df_energie[
    (df_energie['date'].dt.year >= start_year) &
    (df_energie['date'].dt.year <= end_year)
]

df_meteorologisch = df_meteorologisch[
    (df_meteorologisch['date'].dt.year >= start_year) &
    (df_meteorologisch['date'].dt.year <= end_year)
]

# ======================================================================================== Dataframes
# samenvoegen dataframes
df_knmi_energie = pd.merge(df_meteorologisch, df_energie, on='date', how='inner')

with st.expander('Ruwe data'): 
    st.write(
        "Let op: energie is uitgedrukt in miljoen kilowattuur (mln kWh). "
        "1 miljoen kilowattuur is 1.000.000 kilowattuur. "
        "Een windmolen maakt ongeveer 20.000 kilowattuur per dag en een gemiddeld huishouden verbruikt ongeveer 3.000 kilowattuur per dag."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Energie dataframe van cbsodata')
        st.dataframe(df_energie)
    with col2:
        st.header("Meteorologisch dataframe van KNMI")
        st.dataframe(df_meteorologisch)
    with col3:
        st.header('Samengevoegde dataframe')
        st.dataframe(df_knmi_energie)
    st.divider()

# ======================================================================================== Energie plots
energy_cols = ['Kernenergie_4', 'Kolen_6', 'Olieproducten_7', 'Aardgas_8', 'Biomassa_9', 'Waterkracht_11', 'WindenergieTotaal_12', 'Zonnestroom_15']

EnergieProductie = go.Figure()
for col in energy_cols:
    EnergieProductie.add_trace(go.Scatter(
        x=df_energie['date'],
        y=df_energie[col],
        mode='lines+markers',
        name=col,
        yaxis='y1'
    ))

EnergieProductie.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="mln kWh"),
    title="Verschillende Energie Producties in Nederland"
)

st.plotly_chart(EnergieProductie, use_container_width=True)

# ======================================================================================== Totaal energieproductie
EnergieProductieTot = go.Figure()

EnergieProductieTot.add_trace(go.Scatter(
    x=df_energie['date'],
    y=df_energie['BrutoProductie_1'],
    mode='lines+markers',
    name='Bruto Energie Productie'
))
EnergieProductieTot.add_trace(go.Scatter(
    x=df_energie['date'],
    y=df_energie['NettoVerbruikBerekend_30'],
    mode='lines+markers',
    name='Netto Energie Verbruik'
))

EnergieProductieTot.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="mln kWh"),
    title="Totale Energie Productie in Nederland"
)

st.plotly_chart(EnergieProductieTot, use_container_width=True)
st.divider()

# ======================================================================================== heatmap corrolaties
st.subheader("Heatmap correlatie energie en meteorologische waarden")

meteo_vars = ['Temperatuur_C', 'Neerslag_MM', 'Windsnelheid_ms']
corr_cols = meteo_vars + ['BrutoProductie_1', 'NettoVerbruikBerekend_30'] + energy_cols

corr_matrix = df_knmi_energie[corr_cols].corr()

col1, col2 = st.columns(2)
with col1: beperk_verticaal = st.toggle("Toon alleen meteorologische variabelen verticaal", True)
with col2: toon_meteo_horizontaal = st.toggle("Toon meteorologische variabelen horizontaal")

# Verticale selectie
if beperk_verticaal:
    y_vars = meteo_vars
else:
    y_vars = corr_matrix.index.tolist()

# Horizontale selectie
if toon_meteo_horizontaal:
    x_vars = corr_matrix.columns.tolist()
else:
    x_vars = [col for col in corr_matrix.columns if col not in meteo_vars]

corr_selected = corr_matrix.loc[y_vars, x_vars]

heatmap_fig = go.Figure(data=go.Heatmap(
    z=corr_selected.values,
    x=corr_selected.columns,
    y=corr_selected.index,
    colorscale='RdBu',
    zmin=-1,
    zmax=1,
    text=corr_selected.round(2).values,
    texttemplate="%{text}",
    colorbar=dict(title="Correlatie")
))

heatmap_fig.update_layout(
    template="plotly_white",
    height=400 if beperk_verticaal else 800
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# ======================================================================================== waterkracht vs temperatuur
corr_line_water = go.Figure()

corr_line_water.add_trace(go.Scatter(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Temperatuur_C'],
    name='Gemiddelde temperatuur',
    mode='lines+markers',
    line=dict(color="#B5232F"),
    marker=dict(color='#B5232F')
))

corr_line_water.add_trace(go.Scatter(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Waterkracht_11'],
    name='Opwekking Waterkracht',
    mode='lines+markers',
    line=dict(color="#1C72DC"),
    marker=dict(color='#1C72DC')
))

corr_line_water.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Waarde",
    title="Correlatie waterkracht <-> Temperatuur"
)

st.plotly_chart(corr_line_water, use_container_width=True)

# ======================================================================================== Zonnestroom vs temperatuur
corr_line_zon = go.Figure()

corr_line_zon.add_trace(go.Scatter(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Temperatuur_C'],
    name='Gemiddelde temperatuur',
    mode='lines+markers',
    line=dict(color="#B5232F"),
    marker=dict(color='#B5232F')
))

corr_line_zon.add_trace(go.Scatter(
    x=df_knmi_energie['date'],
    y=df_knmi_energie['Zonnestroom_15'] / 100,
    name='Opwekking Zonnestroom (/100)',
    mode='lines+markers',
    line=dict(color="#F3AA58"),
    marker=dict(color='#F3AA58')
))

corr_line_zon.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Waarde",
    title="Correlatie Zonnestroom (gedeeld door 100) <-> Temperatuur"
)

st.plotly_chart(corr_line_zon, use_container_width=True)

# ======================================================================================== TotaalStroom vs temperatuur
corr_line_energie_verbruik = make_subplots(specs=[[{"secondary_y": True}]])

corr_line_energie_verbruik.add_trace(
    go.Scatter(
        x=df_knmi_energie['date'],
        y=df_knmi_energie['Temperatuur_C'],
        name='Gemiddelde temperatuur',
        mode='lines+markers',
        line=dict(color="#B5232F"),
        marker=dict(color='#B5232F')
    ),
    secondary_y=False,
)
corr_line_energie_verbruik.add_trace(
    go.Scatter(
        x=df_knmi_energie['date'],
        y=df_knmi_energie['NettoVerbruikBerekend_30'],
        name='Netto Verbruik',
        mode='lines+markers',
        line=dict(color="#DC821C"),
        marker=dict(color='#DC821C')
    ),
    secondary_y=True,
)
corr_line_energie_verbruik.update_layout(
    template="plotly_white",
    title="Correlatie Temperatuur <-> Netto Verbruik",
    xaxis_title="Jaar",
)
corr_line_energie_verbruik.update_yaxes(title_text="Temperatuur (°C)", secondary_y=False)
corr_line_energie_verbruik.update_yaxes(title_text="Netto Verbruik (kWh)", secondary_y=True)

st.plotly_chart(corr_line_energie_verbruik, use_container_width=True)
