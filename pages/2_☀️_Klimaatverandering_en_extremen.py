import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from data_loader import load_knmi_data
from stations import station_dict


# PAGINA CONFIGURATIE

st.set_page_config(page_title="Klimaatverandering & Extremen", layout="wide")
st.title("Klimaatverandering & Extremen")

st.markdown(
    """
Deze pagina gebruikt KNMI-observaties om te kijken of er tekenen zijn van opwarming
en of extreme weersituaties vaker voorkomen (hitte, vorst, zware neerslag).

"""
)
st.divider()


# SIDEBAR: INSTELLINGEN

st.sidebar.header("Instellingen")

selected_station_name = st.sidebar.selectbox(
    "Selecteer station",
    list(station_dict.keys())
)
station = station_dict[selected_station_name]

# Data laden via data_loader 
df_meteo, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data(station=station)

min_year = int(df_meteo["year"].min())
max_year = int(df_meteo["year"].max())

selected_year_range = st.sidebar.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(max(min_year, 1950), max_year) 
)

st.sidebar.markdown("---")
# Recent window voor trend vergelijking
recent_years = st.sidebar.selectbox(
    "Definitie van 'recente jaren'",
    options=[10, 20, 30, 40],
    index=2
)
# Drempels voor extremen
temp_threshold = st.sidebar.selectbox(
    "Drempel voor hitte-dagen",
    options=[25, 30],
    index=0
)

rain_threshold = st.sidebar.selectbox(
    "Drempel voor zware neerslag",
    options=[10, 20, 30],
    index=1
)



show_frost = st.sidebar.checkbox("Toon ook vorstdagen (TN < 0°C)", value=True)
show_max_rain = st.sidebar.checkbox("Toon max. dagneerslag per jaar", value=True)




# DATA FILTEREN EN OPSCHONEN

start_year, end_year = selected_year_range

df = df_meteo[
    (df_meteo["year"] >= start_year) &
    (df_meteo["year"] <= end_year)
].copy()

# positieve waarden
if "Neerslag_MM" in df.columns:
    df.loc[df["Neerslag_MM"] < 0, "Neerslag_MM"] = np.nan

# een heid omzetten naar°C.
if "TX" in df.columns:
    df["TempMax_C"] = df["TX"] * 0.1
else:
    df["TempMax_C"] = np.nan

if "TN" in df.columns:
    df["TempMin_C"] = df["TN"] * 0.1
else:
    df["TempMin_C"] = np.nan



#  LINEAIRE TREND BEREKENEN

def linear_trend(x: pd.Series, y: pd.Series):
    """
    Bereken lineaire trend y = a*x + b.
    Return: (a, b). Als te weinig punten: (None, None).
    """
    x = pd.to_numeric(x, errors="coerce")
    y = pd.to_numeric(y, errors="coerce")
    mask = x.notna() & y.notna()
    if mask.sum() < 2:
        return None, None
    a, b = np.polyfit(x[mask], y[mask], 1)
    return a, b


# 1) TEMPERATUURTREND 
st.subheader("1) Opwarming: jaarlijkse gemiddelde temperatuur (TG)")

df_year_temp = (
    df.groupby("year")["Temperatuur_C"]
      .mean()
      .reset_index()
      .rename(columns={"Temperatuur_C": "Temp_mean"})
)

a_all, b_all = linear_trend(df_year_temp["year"], df_year_temp["Temp_mean"])

recent_start = max(start_year, end_year - recent_years + 1)
df_recent = df_year_temp[df_year_temp["year"] >= recent_start].copy()
a_recent, b_recent = linear_trend(df_recent["year"], df_recent["Temp_mean"])

# KPI's bovenaan
k1, k2, k3 = st.columns(3)

avg_temp_total = float(df_year_temp["Temp_mean"].mean()) if len(df_year_temp) else np.nan
k1.metric("Gem. temperatuur (gekozen periode)", f"{avg_temp_total:.2f} °C" if pd.notna(avg_temp_total) else "—")

k2.metric("Trend (gekozen periode)", f"{a_all*10:.3f} °C/decennium" if a_all is not None else "—")
k3.metric(f"Trend (laatste {recent_years} jaar)", f"{a_recent*10:.3f} °C/decennium" if a_recent is not None else "—")

fig_temp = go.Figure()

fig_temp.add_trace(go.Scatter(
    x=df_year_temp["year"],
    y=df_year_temp["Temp_mean"],
    mode="lines+markers",
    name="Jaarlijkse gemiddelde temp (TG)"
))

if a_all is not None:
    df_year_temp["trend_all"] = a_all * df_year_temp["year"] + b_all
    fig_temp.add_trace(go.Scatter(
        x=df_year_temp["year"],
        y=df_year_temp["trend_all"],
        mode="lines",
        name="Trend (hele periode)",
        line=dict(dash="dash")
    ))

if a_recent is not None:
    df_recent["trend_recent"] = a_recent * df_recent["year"] + b_recent
    fig_temp.add_trace(go.Scatter(
        x=df_recent["year"],
        y=df_recent["trend_recent"],
        mode="lines",
        name=f"Trend (laatste {recent_years} jaar)",
        line=dict(dash="dot")
    ))

fig_temp.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Temperatuur (°C)"
)

st.plotly_chart(fig_temp, use_container_width=True)


st.divider()



# 2) EXTREME TEMPERATUREN 

st.subheader("2) Extreme temperaturen")

# Hitte-dagen
df["is_hot"] = df["TempMax_C"] >= float(temp_threshold)

# Vorstdagen
df["is_frost"] = df["TempMin_C"] < 0.0

df_extreme_temp = (
    df.groupby("year")
      .agg(
          hot_days=("is_hot", "sum"),
          frost_days=("is_frost", "sum"),
      )
      .reset_index()
)

# Trend voor hitte-dagen
a_hot, b_hot = linear_trend(df_extreme_temp["year"], df_extreme_temp["hot_days"])

fig_hot = go.Figure()
fig_hot.add_trace(go.Bar(
    x=df_extreme_temp["year"],
    y=df_extreme_temp["hot_days"],
    name=f"Hitte-dagen (TX ≥ {temp_threshold}°C)"
))

if a_hot is not None:
    df_extreme_temp["hot_trend"] = a_hot * df_extreme_temp["year"] + b_hot
    fig_hot.add_trace(go.Scatter(
        x=df_extreme_temp["year"],
        y=df_extreme_temp["hot_trend"],
        mode="lines",
        name="Trend",
        line=dict(dash="dash")
    ))

fig_hot.update_layout(
    template="plotly_white",
    title=f"Aantal hitte-dagen per jaar ( ≥ {temp_threshold}°C)",
    xaxis_title="Jaar",
    yaxis_title="Aantal dagen"
)
st.plotly_chart(fig_hot, use_container_width=True)

# Vorstdagen 
if show_frost:
    a_frost, b_frost = linear_trend(df_extreme_temp["year"], df_extreme_temp["frost_days"])

    fig_frost = go.Figure()
    fig_frost.add_trace(go.Bar(
        x=df_extreme_temp["year"],
        y=df_extreme_temp["frost_days"],
        name="Vorstdagen (< 0°C)"
    ))

    if a_frost is not None:
        df_extreme_temp["frost_trend"] = a_frost * df_extreme_temp["year"] + b_frost
        fig_frost.add_trace(go.Scatter(
            x=df_extreme_temp["year"],
            y=df_extreme_temp["frost_trend"],
            mode="lines",
            name="Trend",
            line=dict(dash="dash")
        ))

    fig_frost.update_layout(
        template="plotly_white",
        title="Aantal vorstdagen per jaar (< 0°C)",
        xaxis_title="Jaar",
        yaxis_title="Aantal dagen"
    )
    st.plotly_chart(fig_frost, use_container_width=True)

st.divider()



# 3) EXTREME NEERSLAG 
st.subheader("3) Extreme neerslag")

df["is_heavy_rain"] = df["Neerslag_MM"] >= float(rain_threshold)

df_extreme_rain = (
    df.groupby("year")
      .agg(
          heavy_rain_days=("is_heavy_rain", "sum"),
          max_daily_rain=("Neerslag_MM", "max"),
          total_rain=("Neerslag_MM", "sum")
      )
      .reset_index()
)

a_rain_days, b_rain_days = linear_trend(df_extreme_rain["year"], df_extreme_rain["heavy_rain_days"])

fig_rain_days = go.Figure()
fig_rain_days.add_trace(go.Bar(
    x=df_extreme_rain["year"],
    y=df_extreme_rain["heavy_rain_days"],
    name=f"Zware neerslagdagen (≥ {rain_threshold} mm)"
))

if a_rain_days is not None:
    df_extreme_rain["rain_days_trend"] = a_rain_days * df_extreme_rain["year"] + b_rain_days
    fig_rain_days.add_trace(go.Scatter(
        x=df_extreme_rain["year"],
        y=df_extreme_rain["rain_days_trend"],
        mode="lines",
        name="Trend",
        line=dict(dash="dash")
    ))

fig_rain_days.update_layout(
    template="plotly_white",
    title=f"Aantal zware neerslagdagen per jaar (≥ {rain_threshold} mm/dag)",
    xaxis_title="Jaar",
    yaxis_title="Aantal dagen"
)
st.plotly_chart(fig_rain_days, use_container_width=True)

# Max dagneerslag per jaar 
if show_max_rain:
    a_max, b_max = linear_trend(df_extreme_rain["year"], df_extreme_rain["max_daily_rain"])

    fig_max_rain = go.Figure()
    fig_max_rain.add_trace(go.Scatter(
        x=df_extreme_rain["year"],
        y=df_extreme_rain["max_daily_rain"],
        mode="lines+markers",
        name="Max dagneerslag"
    ))

    if a_max is not None:
        df_extreme_rain["max_trend"] = a_max * df_extreme_rain["year"] + b_max
        fig_max_rain.add_trace(go.Scatter(
            x=df_extreme_rain["year"],
            y=df_extreme_rain["max_trend"],
            mode="lines",
            name="Trend",
            line=dict(dash="dash")
        ))

    fig_max_rain.update_layout(
        template="plotly_white",
        title="Maximale dagneerslag per jaar",
        xaxis_title="Jaar",
        yaxis_title="Neerslag (mm)"
    )
    st.plotly_chart(fig_max_rain, use_container_width=True)

st.divider()

