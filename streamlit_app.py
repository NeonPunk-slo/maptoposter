import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# 1. Popolna odstranitev vseh Streamlit elementov (header, footer, menu)
st.set_page_config(page_title="Mestna Poezija", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .stApp {
        background-color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Nastavitve v stranskem meniju (edini element, ki ostane)
with st.sidebar:
    st.markdown("<h1 style='color: #00f2ff; font-family: sans-serif;'>MAP POSTER</h1>", unsafe_allow_html=True)
    mesto = st.text_input("Kraj", "Ljubljana")
    drzava = st.text_input("Država", "Slovenija")
    slog = st.selectbox("Slog", ["Midnight Neon", "Toner Art", "Silver"])
    zoom = st.slider("Zoom", 10, 18, 13)
    st.write("---")
    st.markdown(f'<a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="width:100%; background-color:#ffc439; border-radius:10px; border:none; padding:10px; font-weight:bold;">💛 Podpri projekt</button></a>', unsafe_allow_html=True)

# 3. Logika za koordinate
try:
    geolocator = Nominatim(user_agent="mestna_poezija_gallery_2026")
    loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
    lat, lon = (loc.latitude, loc.longitude) if loc else (46.0569, 14.5058)
except:
    lat, lon = 46.0569, 14.5058

# 4. Izbira stila
tiles = {
    "Midnight Neon": "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    "Toner Art": "https://stamen-tiles.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png",
    "Silver": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
}

# 5. Izris čez celoten zaslon
m = folium.Map(
    location=[lat, lon],
    zoom_start=zoom,
    tiles=tiles[slog],
    attr='CartoDB',
    zoom_control=False,
    dragging=True
)

# Prikaz brez kakršnihkoli robov
st_folium(m, width=2000, height=800, use_container_width=True)

# 6. Velik, premium napis na dnu zaslona
st.markdown(f"""
    <div style='text-align: center; color: white; background-color: black; padding: 100px 0px; width: 100%;'>
        <h1 style='font-size: 120px; font-weight: 100; letter-spacing: 25px; margin: 0; font-family: serif;'>{mesto.upper()}</h1>
        <p style='font-size: 25px; letter-spacing: 15px; color: #555; margin-top: 10px;'>{drzava.upper()}</p>
        <p style='font-family: monospace; color: #333; font-size: 14px; margin-top: 40px;'>{abs(lat):.4f}° S / {abs(lon):.4f}° V</p>
    </div>
""", unsafe_allow_html=True)