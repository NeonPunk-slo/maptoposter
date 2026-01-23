import streamlit as st
import matplotlib.pyplot as plt
from staticmap import StaticMap
import io

st.set_page_config(page_title="Mestna Poezija")
st.title("🎨 Mestna Poezija")

# Namesto avtomatskega iskanja, ki naju blokira, bova koordinate vpisala ročno
mesto = st.text_input("Ime kraja", "Ljubljana")
drzava = st.text_input("Država", "Slovenija")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Zemljepisna širina (Latitude)", value=46.0569, format="%.4f")
with col2:
    lon = st.number_input("Zemljepisna dolžina (Longitude)", value=14.5058, format="%.4f")

zoom = st.slider("Zoom nivo", 10, 15, 12)

if st.button("✨ Ustvari poster"):
    try:
        with st.spinner("Rišem tvoj umetniški poster..."):
            # Uporabimo direkten naslov do zemljevidov
            m = StaticMap(800, 1000, url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
            image = m.render(zoom=zoom, center=[lon, lat])
            
            fig, ax = plt.subplots(figsize=(10, 14), facecolor='#F1F4F7')
            ax.imshow(image)
            ax.axis('off')
            
            # Napisi na dnu
            plt.text(0.5, -0.05, mesto.upper(), transform=ax.transAxes, fontsize=45, ha='center', fontweight='bold', color='#063951')
            plt.text(0.5, -0.10, drzava.upper(), transform=ax.transAxes, fontsize=22, ha='center', color='#063951')
            plt.text(0.5, -0.14, f"{abs(lat):.4f}° S / {abs(lon):.4f}° V", transform=ax.transAxes, fontsize=14, ha='center', family='monospace', color='#063951')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.5)
            st.image(buf)
            st.download_button("📥 Prenesi PNG", buf, file_name=f"{mesto}_poster.png")
            
    except Exception as e:
        st.error(f"Napaka: {e}")

st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none; cursor: pointer;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)