import streamlit as st
import matplotlib.pyplot as plt
from staticmap import StaticMap
from geopy.geocoders import Nominatim
import io

st.set_page_config(page_title="Mestna Poezija")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Ime kraja", "Ljubljana")
drzava = st.text_input("Država", "Slovenija")
zoom = st.slider("Zoom nivo", 10, 15, 12)

if st.button("✨ Ustvari poster"):
    try:
        # Uporabimo zelo specifičen user_agent, da nas ne blokirajo
        geolocator = Nominatim(user_agent="mestna_poezija_haloze_2026_unique_v1")
        loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
        
        if loc:
            lat, lon = loc.latitude, loc.longitude
        else:
            st.warning("Kraja nisem našel, uporabljam privzete koordinate.")
            lat, lon = 46.0569, 14.5058 # Ljubljana
            
        with st.spinner("Ustvarjam zemljevid..."):
            m = StaticMap(800, 1000, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
            image = m.render(zoom=zoom, center=[lon, lat])
            
            fig, ax = plt.subplots(figsize=(10, 14), facecolor='#F1F4F7')
            ax.imshow(image)
            ax.axis('off')
            
            # Dodajanje napisov na dno
            plt.text(0.5, -0.05, mesto.upper(), transform=ax.transAxes, fontsize=45, ha='center', fontweight='bold', color='#063951')
            plt.text(0.5, -0.10, drzava.upper(), transform=ax.transAxes, fontsize=22, ha='center', color='#063951')
            plt.text(0.5, -0.14, f"{abs(lat):.4f}° {'S' if lat>=0 else 'J'} / {abs(lon):.4f}° {'V' if lon>=0 else 'Z'}", 
                     transform=ax.transAxes, fontsize=14, ha='center', family='monospace', color='#063951')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.5)
            st.image(buf)
            st.download_button("📥 Prenesi PNG", buf, file_name=f"{mesto}_poster.png")
            
    except Exception as e:
        st.error(f"Prišlo je do napake pri povezavi: {e}. Poskusi čez nekaj sekund.")

# --- PAYPAL ---
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)