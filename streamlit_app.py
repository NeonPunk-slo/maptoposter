import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# Osnovna konfiguracija strani
st.set_page_config(page_title="Mestna Poezija", layout="wide")

# Naslov aplikacije
st.markdown("<h1 style='text-align: center; color: #063951;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ustvari unikaten umetniški poster svojega kraja</p>", unsafe_allow_html=True)

# Stranski meni za nastavitve
with st.sidebar:
    st.header("Nastavitve posterja")
    mesto = st.text_input("Ime kraja", "Ljubljana")
    drzava = st.text_input("Država", "Slovenija")
    
    slog = st.selectbox("Izberi umetniški slog", [
        "Svetel (Minimal)", 
        "Temen (Premium)", 
        "Retro (Toner)",
        "Barvni (Outdoor)"
    ])
    
    zoom = st.slider("Zoom nivo", 10, 18, 13)

# Definiranje slogov zemljevidov
tiles_dict = {
    "Svetel (Minimal)": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    "Temen (Premium)": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "Retro (Toner)": "https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
    "Barvni (Outdoor)": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
}

attr_dict = {
    "Svetel (Minimal)": "CartoDB",
    "Temen (Premium)": "CartoDB",
    "Retro (Toner)": "Stamen",
    "Barvni (Outdoor)": "OpenStreetMap"
}

# Glavni del za izris
try:
    # Uporabimo unikaten user_agent za geopy, da nas ne blokirajo
    geolocator = Nominatim(user_agent="mestna_poezija_haloze_final_2026")
    loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
    
    if loc:
        # Ustvarjanje Folium zemljevida
        m = folium.Map(
            location=[loc.latitude, loc.longitude],
            zoom_start=zoom,
            tiles=tiles_dict[slog],
            attr=attr_dict[slog],
            zoom_control=False
        )
        
        # Prikaz zemljevida v Streamlitu
        st_folium(m, width=1000, height=600, use_container_width=True)
        
        # Spodnji del s podatki (kot na premium posterjih)
        st.markdown(f"""
            <div style='text-align: center; border-top: 2px solid #eee; padding-top: 20px; margin-top: 20px;'>
                <h1 style='font-size: 80px; font-weight: bold; margin-bottom: 0; color: #333;'>{mesto.upper()}</h1>
                <p style='font-size: 25px; letter-spacing: 8px; color: #666;'>{drzava.upper()}</p>
                <p style='font-family: "Courier New", Courier, monospace; font-size: 18px; color: #999;'>
                    {abs(loc.latitude):.4f}° {"S" if loc.latitude >= 0 else "J"} / 
                    {abs(loc.longitude):.4f}° {"V" if loc.longitude >= 0 else "Z"}
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Iskanje kraja ni uspelo. Preveri črkovanje.")

except Exception as e:
    st.info("Trenutno osvežujemo podatke... Prosim, počakaj trenutek.")

# PayPal Donacija (Zmeraj na dnu)
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center; padding-bottom: 50px;">
        <p style="color: #888;">Ti je aplikacija všeč? Podpri razvoj.</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block;">
                💛 PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)