import streamlit as st
import plotly.graph_objects as go
import numpy as np
from data_loader import load_knmi_data
from stations import station_dict

st.set_page_config(page_title="Historische data", layout="wide")

# ========================================================= SIDEBAR

st.sidebar.header("Instellingen")
selected_station_name = st.sidebar.selectbox("Selecteer station",list(station_dict.keys()))
station = station_dict[selected_station_name]

df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data(station=station)

min_year = int(df_yearly_temp['year'].min())
max_year = int(df_yearly_temp['year'].max())

# Jaar slider
selected_year_range = st.sidebar.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

# ========================================================= MAAND SELECTIE MET SELECTEER ALLES / DESELECTEER ALLES

maand_namen = {1: "Januari", 2: "Februari", 3: "Maart", 4: "April",5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",9: "September", 10: "Oktober", 11: "November", 12: "December"}
maand_lijst = ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
# Session state initialiseren
if "selected_months" not in st.session_state:
    st.session_state.selected_months = list(maand_namen.keys())

st.sidebar.markdown("### Selecteer maanden")

col1, col2 = st.sidebar.columns(2)
if col1.button("Selecteer Alles"):
    st.session_state.selected_months = list(maand_namen.keys())
if col2.button("Selecteer Niets"):
    st.session_state.selected_months = []

selected_months = st.sidebar.multiselect(
    "Selecteer maanden",
    options=list(maand_namen.keys()),
    format_func=lambda x: maand_namen[x],
    default=st.session_state.selected_months,
    key="selected_months"
)

# ========================================================= JAARGEMIDDELDE MET TREND (MAANDAFHANKELIJK)
st.header("Historische data")
st.divider()

df_filtered = df_monthly_temp[
    (df_monthly_temp['year'] >= selected_year_range[0]) &
    (df_monthly_temp['year'] <= selected_year_range[1]) &
    (df_monthly_temp['month'].isin(selected_months))
]

df_monthly_temp_filtered = (
    df_filtered
    .groupby('year')['Temperatuur_C']
    .mean()
    .reset_index()
)

fig_year_temp = go.Figure()

fig_year_temp.add_trace(go.Scatter(
    x=df_monthly_temp_filtered['year'],
    y=df_monthly_temp_filtered['Temperatuur_C'],
    mode='lines+markers',
    name='Gemiddelde temperatuur'
))

if len(df_monthly_temp_filtered) > 1:
    yearly_trend_coefficients = np.polyfit(
        df_monthly_temp_filtered['year'],
        df_monthly_temp_filtered['Temperatuur_C'],
        1
    )

    df_monthly_temp_filtered['trend'] = (
        yearly_trend_coefficients[0] * df_monthly_temp_filtered['year'] + yearly_trend_coefficients[1]
    )

    fig_year_temp.add_trace(go.Scatter(
        x=df_monthly_temp_filtered['year'],
        y=df_monthly_temp_filtered['trend'],
        mode='lines',
        name='Trend',
        line=dict(dash='dash')
    ))

    st.markdown(f"**Gemiddelde stijging per jaar:** {yearly_trend_coefficients[0]:.4f} °C")

fig_year_temp.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Gemiddelde temperatuur (°C)",
    title="Gemiddelde jaarlijkse temperatuur",
    yaxis=dict(range=[0, 13])
)

st.plotly_chart(fig_year_temp, use_container_width=True)

st.divider()

# ========================================================= NEERSLAG PER JAAR

df_rain_filtered = df_yearly_rain[
    (df_yearly_rain['year'] >= selected_year_range[0]) &
    (df_yearly_rain['year'] <= selected_year_range[1])
]

fig_rain = go.Figure()

fig_rain.add_trace(go.Bar(
    x=df_rain_filtered['year'],
    y=df_rain_filtered['Neerslag_MM'],
    name='Totale neerslag'
))

fig_rain.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Totale neerslag (mm)",
    title="Gemiddelde neerslag per jaar"
)

st.plotly_chart(fig_rain, use_container_width=True)

st.divider()

# ========================================================= GEMIDDELDE TEMPERATUUR PER MAAND (BARPLOT)

st.header("Gemiddelde temperatuur per maand")

df_monthly_filtered_temp = df_monthly_temp[
    (df_monthly_temp['year'] >= selected_year_range[0]) &
    (df_monthly_temp['year'] <= selected_year_range[1])
]

df_monthly_avg_temp = (
    df_monthly_filtered_temp
    .groupby('month')['Temperatuur_C']
    .mean()
    .reset_index()
)

fig_month_bar = go.Figure()

fig_month_bar.add_trace(go.Bar(
    x=df_monthly_avg_temp['month'],
    y=df_monthly_avg_temp['Temperatuur_C'],
    marker=dict(
        color=df_monthly_avg_temp['Temperatuur_C'],
        colorscale='Bluered',
        colorbar=dict(title="Waarde")
    ),
    name="Maandgemiddelde"
))

fig_month_bar.update_layout(
    template="plotly_white",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=maand_lijst
    ),
    xaxis_title="Maand",
    yaxis_title="Gemiddelde temperatuur (°C)",
)

st.plotly_chart(fig_month_bar, use_container_width=True)

# ========================================================= Totale REGEN PER MAAND (BARPLOT)

st.header("Totale neerslag per maand")

df_monthly_filtered = df_monthly_rain[
    (df_monthly_rain['year'] >= selected_year_range[0]) &
    (df_monthly_rain['year'] <= selected_year_range[1])
]

df_monthly_tot_rain = (
    df_monthly_filtered
    .groupby('month')['Neerslag_MM']
    .sum()
    .reset_index()
)

fig_month_bar = go.Figure()

fig_month_bar.add_trace(go.Bar(
    x=df_monthly_tot_rain['month'],
    y=df_monthly_tot_rain['Neerslag_MM'],
    name="Maandtotaal"
))

fig_month_bar.update_layout(
    template="plotly_white",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=maand_lijst
    ),
    xaxis_title="Maand",
    yaxis_title="Totaal Neerslag_MM",
)

st.plotly_chart(fig_month_bar, use_container_width=True)

# ========================================================= Ruwe Data
st.divider()
st.header("Ruwe data")
st.dataframe(df_meteorologisch)