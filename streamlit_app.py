import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Mestna Poezija", layout="wide")

# Naslov in stilizacija
st.markdown("<h1 style='text-align: center; color: #063951;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    mesto = st.text_input("Ime kraja", "Ljubljana")
    drzava = st.text_input("Država", "Slovenija")
    slog = st.selectbox("Umetniški slog", ["Črno-bel (Toner)", "Svetel (Positron)", "Temen (Dark Matter)"])
    zoom = st.slider("Zoom", 10, 16, 13)

# Map slogi (Tiles)
tiles = {
    "Črno-bel (Toner)": "stamentoner",
    "Svetel (Positron)": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "Temen (Dark Matter)": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
}

attr = 'CartoDB' if "Carto" in str(tiles.get(slog)) else 'Stamen'

with col2:
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_final_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        
        if loc:
            # Ustvarjanje umetniškega zemljevida
            m = folium.Map(
                location=[loc.latitude, loc.longitude], 
                zoom_start=zoom, 
                tiles=tiles[slog], 
                attr=attr,
                zoom_control=False,
                scrollWheelZoom=False,
                dragging=True
            )
            
            # Prikaz v Streamlitu
            st_folium(m, width=800, height=1000)
            
            # Podatki za tvoj poster
            st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <h1 style='font-size: 60px; margin-bottom: 0;'>{mesto.upper()}</h1>
                    <p style='font-size: 20px; letter-spacing: 5px;'>{drzava.upper()}</p>
                    <p style='font-family: monospace;'>{abs(loc.latitude):.4f}° S / {abs(loc.longitude):.4f}° V</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Kraja ni bilo mogoče najti.")
    except Exception as e:
        st.error("Trenutna preobremenitev strežnika. Prosim, osveži stran.")

# PayPal gumb na dnu
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)