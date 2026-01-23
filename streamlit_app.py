import streamlit as st
import matplotlib.pyplot as plt
from staticmap import StaticMap, CircleMarker
from geopy.geocoders import Nominatim
import io

st.set_page_config(page_title="Mestna Poezija")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Ime kraja", "Ljubljana")
drzava = st.text_input("Država", "Slovenija")
zoom = st.slider("Zoom nivo", 10, 15, 12)

if st.button("✨ Ustvari poster"):
    geolocator = Nominatim(user_agent="mestna_poezija_haloze")
    loc = geolocator.geocode(f"{mesto}, {drzava}")
    
    if loc:
        m = StaticMap(800, 1000, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
        image = m.render(zoom=zoom, center=[loc.longitude, loc.latitude])
        
        # Priprava za prikaz
        fig, ax = plt.subplots(figsize=(10, 14), facecolor='#F1F4F7')
        ax.imshow(image)
        ax.axis('off')
        
        # Napisi
        plt.text(0.5, -0.1, mesto.upper(), transform=ax.transAxes, fontsize=40, ha='center', fontweight='bold')
        plt.text(0.5, -0.15, drzava.upper(), transform=ax.transAxes, fontsize=20, ha='center')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.5)
        st.image(buf)
        st.download_button("📥 Prenesi PNG", buf, file_name=f"{mesto}.png")

st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)