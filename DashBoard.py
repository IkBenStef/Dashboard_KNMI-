import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Titel van de app
st.title("Simpele Streamlit Grafiek")

# Genereer voorbeelddata
x = np.arange(0, 10, 0.5)
y = np.sin(x)

df = pd.DataFrame({
    "x": x,
    "y": y
})

# Toon dataframe (optioneel)
st.write("Voorbeelddata:")
st.dataframe(df)

# Maak grafiek
fig, ax = plt.subplots()
ax.plot(df["x"], df["y"])
ax.set_xlabel("X-as")
ax.set_ylabel("Y-as")
ax.set_title("Sinusgrafiek")

# Toon grafiek in Streamlit
st.pyplot(fig)
