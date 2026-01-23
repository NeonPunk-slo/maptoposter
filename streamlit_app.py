import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Mestna Poezija", layout="wide")

st.markdown("<h1 style='text-align: center; color: #063951;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)

# Nastavitve v stranskem meniju
mesto = st.sidebar.text_input("Ime kraja", "Ljubljana")
drzava = st.sidebar.text_input("Država", "Slovenija")
slog = st.sidebar.selectbox("Slog", ["Svetel", "Temen", "Retro"])
zoom = st.sidebar.slider("Zoom", 10, 18, 13)

# Slogi zemljevidov
slogi = {
    "Svetel": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "Temen": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "Retro": "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
}

# Enostavno iskanje lokacije
try:
    geolocator = Nominatim(user_agent="neon_punk_final_fix_2026")
    loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
    if loc:
        lat, lon = loc.latitude, loc.longitude
    else:
        lat, lon = 46.0569, 14.5058 # Rezerva: Ljubljana
except:
    lat, lon = 46.0569, 14.5058

# Izris interaktivnega zemljevida
m = folium.Map(
    location=[lat, lon],
    zoom_start=zoom,
    tiles=slogi[slog],
    attr='CartoDB',
    zoom_control=False
)

st_folium(m, width=1200, height=600, use_container_width=True)

# Estetski napis na dnu
st.markdown(f"""
    <div style='text-align: center; border-top: 2px solid #eee; padding-top: 20px; margin-top: 20px;'>
        <h1 style='font-size: 70px; font-weight: bold; margin-bottom: 0;'>{mesto.upper()}</h1>
        <p style='font-size: 20px; letter-spacing: 10px; color: #666;'>{drzava.upper()}</p>
        <p style='font-family: monospace; color: #999;'>{abs(lat):.4f}° S / {abs(lon):.4f}° V</p>
    </div>
""", unsafe_allow_html=True)

# PayPal Donacija
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)