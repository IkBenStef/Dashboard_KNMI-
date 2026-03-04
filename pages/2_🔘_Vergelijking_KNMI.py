import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import load_knmi_data
from stations import station_dict

# ======================================================================================== Sidebar
st.sidebar.header("Instellingen")

selected_station_name = st.sidebar.selectbox("Selecteer station",list(station_dict.keys()))
station = station_dict[selected_station_name]
df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data(station=station)

# Jaar slider
min_year = int(df_yearly_temp['year'].min())
max_year = int(df_yearly_temp['year'].max())

selected_year_range = st.sidebar.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data op jaarrange
df_yearly_temp_filtered = df_yearly_temp[
    (df_yearly_temp['year'] >= selected_year_range[0]) &
    (df_yearly_temp['year'] <= selected_year_range[1])
]

df_yearly_rain_filtered = df_yearly_rain[
    (df_yearly_rain['year'] >= selected_year_range[0]) &
    (df_yearly_rain['year'] <= selected_year_range[1])
]

df_filtered = df_meteorologisch[
    (df_meteorologisch['year'] >= selected_year_range[0]) &
    (df_meteorologisch['year'] <= selected_year_range[1])
]

# ======================================================================================== Grafieken

st.set_page_config(page_title="Vergelijking KNMI", layout="wide")
st.subheader("Jaarlijkse temperatuur & neerslag")


# temperatuur <-> neerslag
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_yearly_temp_filtered['year'],
    y=df_yearly_temp_filtered['Temperatuur_C'],
    mode='lines+markers',
    name='Gem. temperatuur (°C)',
    yaxis='y1',
    marker=dict(color='#1C72DC')
))
fig.add_trace(go.Bar(
    x=df_yearly_rain_filtered['year'],
    y=df_yearly_rain_filtered['Neerslag_MM'],
    name='Totale neerslag (mm)',
    yaxis='y2',
    opacity=0.5,
    marker=dict(color='#B5232F')
))
fig.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="Temperatuur (°C)", side='left'),
    yaxis2=dict(title="Neerslag (mm)", overlaying='y', side='right')
)

st.plotly_chart(fig, use_container_width=True)


# Correlatieplot Temperatuur <-> Neerslag
st.divider()
st.subheader("Correlatie Temperatuur <-> Neerslag ")

fig_corr_temp_rain = px.scatter(df_filtered,x='Temperatuur_C',y='Neerslag_MM',opacity=0.7)

st.plotly_chart(fig_corr_temp_rain, use_container_width=True)

# Correlatieplot Temperatuur ↔ Windsnelheid
st.divider()
st.subheader("Correlatie Temperatuur <-> Windsnelheid ")

fig_corr_temp_wind = px.scatter(df_filtered,x='Temperatuur_C',y='Windsnelheid_ms',opacity=0.7)

st.plotly_chart(fig_corr_temp_wind, use_container_width=True)

# Correlatieplot temperatuur ↔ Windsnelheid
st.divider()
st.subheader("Correlatie Neerslag <-> Windsnelheid")

fig_corr_wind_rian = px.scatter(df_filtered,x='Windsnelheid_ms',y='Neerslag_MM',opacity=0.7)
st.plotly_chart(fig_corr_wind_rian, use_container_width=True)



