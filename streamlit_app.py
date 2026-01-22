import streamlit as st
import io

# Poskusimo uvoziti funkcijo iz tvoje obstoječe datoteke poster.py
try:
    from poster import create_map_poster
except ImportError:
    st.error("Napaka: Datoteka 'poster.py' ni bila najdena ali ne vsebuje funkcije 'create_map_poster'. Preveri GitHub.")

# Naslov strani
st.title("🎨 Generator mestnih posterjev")
st.write("Vnesi podatke in si prenesi svoj umetniški zemljevid.")

# Vnosni podatki
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)

# Ročno definirane barve, da se izognemo napakam pri THEMES
colors = {
    "water": "#DEE1E6",
    "land": "#F8F9FA",
    "roads": "#FFFFFF",
    "text": "#202124"
}

if st.button("🚀 Ustvari poster"):
    place = f"{city}, {country}"
    with st.spinner("Pridobivam podatke... To lahko traja minuto."):
        try:
            img = create_map_poster(place, colors, dist)
            st.image(img, caption=place, use_container_width=True)
            
            # Priprava za prenos
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="Prenesi poster",
                data=buf.getvalue(),
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Prišlo je do napake pri generiranju: {e}")

# PayPal razdelek
st.write("---")
st.subheader("☕ Podpri projekt")
st.write("Če ti je generator všeč, me lahko podpreš za kavo!")

# Tvoja povezava iz gem19.png in gem20.png
paypal_url = "https://www.paypal.me/NeonPunkSlo"

st.markdown(f'''
    <a href="{paypal_url}" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="PayPal">
    </a>
''', unsafe_allow_html=True)