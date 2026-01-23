import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Mestna Poezija", layout="wide")

# CSS za temen izgled aplikacije (da se ujema s premium stilom)
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #ffffff; }
    .stTextInput > div > div > input { background-color: #1a1c23; color: #00f2ff; border: 1px solid #333; }
    .stSelectbox > div > div > div { background-color: #1a1c23; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff; font-family: sans-serif; letter-spacing: 3px;'>🎨 MESTNA POEZIJA</h1>", unsafe_allow_html=True)

# Nastavitve v stranskem meniju
with st.sidebar:
    st.header("Konfiguracija")
    mesto = st.text_input("Ime kraja", "Ljubljana")
    drzava = st.text_input("Država", "Slovenija")
    
    # Tukaj je tvojih 5 tem
    slog = st.selectbox("Izberi temo", [
        "1. Premium Dark (Neon)", 
        "2. Minimalist White", 
        "3. Retro Toner (Black & White)", 
        "4. Midnight Blue", 
        "5. Classic Outdoor"
    ])
    
    zoom = st.slider("Zoom nivo", 10, 18, 13)

# Definiranje povezav do slogov
tiles_dict = {
    "1. Premium Dark (Neon)": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "2. Minimalist White": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "3. Retro Toner (Black & White)": "https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
    "4. Midnight Blue": "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    "5. Classic Outdoor": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
}

# Iskanje lokacije
try:
    geolocator = Nominatim(user_agent="mestna_poezija_2026_final_v5")
    loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
    lat, lon = (loc.latitude, loc.longitude) if loc else (46.0569, 14.5058)
except:
    lat, lon = 46.0569, 14.5058

# Ustvarjanje zemljevida
m = folium.Map(
    location=[lat, lon],
    zoom_start=zoom,
    tiles=tiles_dict[slog],
    attr='CartoDB / OpenStreetMap',
    zoom_control=False
)

# Izris interaktivnega dela
st_folium(m, width=1200, height=600, use_container_width=True)

# Barva napisa glede na temo
text_color = "#ffffff" if "Dark" in slog or "Midnight" in slog or "Retro" in slog else "#000000"
bg_color = "#0b0d11" if text_color == "#ffffff" else "#ffffff"

# Spodnji del s podatki
st.markdown(f"""
    <div style='text-align: center; background-color: {bg_color}; padding: 50px; border-radius: 10px; margin-top: 20px;'>
        <h1 style='font-size: 80px; color: {text_color}; font-weight: bold; margin-bottom: 0;'>{mesto.upper()}</h1>
        <p style='font-size: 25px; color: {text_color}; letter-spacing: 12px; margin-top: 5px;'>{drzava.upper()}</p>
        <p style='font-family: monospace; color: #666; margin-top: 20px;'>{abs(lat):.4f}° S / {abs(lon):.4f}° V</p>
    </div>
""", unsafe_allow_html=True)

# PayPal Donacija
st.write("---")
st.markdown(f'''<div style="text-align: center; padding-bottom: 60px;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 12px 24px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)