import streamlit as st

# Terminal: python -m streamlit run DashBoard.py

st.set_page_config(page_title="KNMI Dashboard", layout="wide")
st.title("KNMI Temperatuur Dashboard")
st.markdown("Gebruik het menu links om een pagina te selecteren.")
st.markdown("Dit is een DashBoard met data van KNMI api, de Open Meteo api en de cbsodata api. Dit dashboard is gemaakt door groep 1 voor de case: DashBoard")
st.divider()
st.markdown("""<style>[data-testid="stImage"] img {height: 300px;object-fit: cover;}</style>""", unsafe_allow_html=True)

kmni_afbeelding = 'https://detaalbrigade.nl/wp-content/uploads/2017/08/knmi.jpg'
open_meteo_afbeelding = 'https://camo.githubusercontent.com/07df8b2f04deae1e4f29d9cfbc7fe90d5eb6f6fe58b91e61a020b9b7aa7627fd/68747470733a2f2f63646e2e737562737461636b2e636f6d2f696d6167652f66657463682f775f313336302c635f6c696d69742c665f6175746f2c715f6175746f3a626573742c666c5f70726f67726573736976653a73746565702f68747470732533412532462532466275636b65746565722d65303562626338342d626161332d343337652d393531382d6164623332626537373938342e73332e616d617a6f6e6177732e636f6d2532467075626c6963253246696d6167657325324666643064373935332d356139642d343431632d623539662d3463646532343435303361315f393334783436312e706e67'
cbs_afbeelding = 'https://avatars.githubusercontent.com/u/43606568?v=4'

col1, col2, col3 = st.columns(3)
with col1:
    st.image(kmni_afbeelding, use_container_width=True)
with col2:
    st.image(open_meteo_afbeelding, use_container_width=True)
with col3:
    st.image(cbs_afbeelding)