import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Mestna Poezija", layout="wide")

st.markdown("<h1 style='text-align: center; color: #063951;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)

# 1. PRIPRAVA PODATKOV
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

# 2. ISKANJE LOKACIJE (Z varnostnim mehanizmom)
@st.cache_data(timeout=600) # Shrani rezultat, da ne sprašuje preveč pogosto
def dobi_lokacijo(m, d):
    try:
        # Unikaten agent, da nas ne zavrnejo
        geolocator = Nominatim(user_agent="neon_punk_haloze_final_fix")
        return geolocator.geocode(f"{m}, {d}", timeout=5)
    except:
        return None

loc = dobi_lokacijo(mesto, drzava)

# Če iskanje ne dela, uporabi privzete koordinate (Ljubljana), da stran ne ostane prazna
if loc:
    lat, lon = loc.latitude, loc.longitude
else:
    st.sidebar.warning("Baza koordinat trenutno ne odgovarja, prikazujem privzeto lokacijo.")
    lat, lon = 46.0569, 14.5058 

# 3. IZRIS ZEMLJEVIDA
m = folium.Map(
    location=[lat, lon],
    zoom_start=zoom,
    tiles=slogi[slog],
    attr='CartoDB',
    zoom_control=False
)

st_folium(m, width=1200, height=600, use_container_width=True)

# 4. NAPIS NA DNU
st.markdown(f"""
    <div style='text-align: center; border-top: 2px solid #eee; padding-top: 20px;'>
        <h1 style='font-size: 70px; margin-bottom: 0;'>{mesto.upper()}</h1>
        <p style='font-size: 20px; letter-spacing: 10px;'>{drzava.upper()}</p>
        <p style='font-family: monospace;'>{abs(lat):.4f}° {'S' if lat>=0 else 'J'} / {abs(lon):.4f}° {'V' if lon>=0 else 'Z'}</p>
    </div>
""", unsafe_allow_html=True)

# PayPal Donacija
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)