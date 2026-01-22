import streamlit as st
from poster import create_map_poster, THEMES

# Naslov strani
st.title("🎨 Generator mestnih posterjev")
st.write("Vnesi podatke in si prenesi svoj umetniški zemljevid.")

# Vnosni podatki na strani
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)
theme_name = st.selectbox("Izberi stil", list(THEMES.keys()))

if st.button("🚀 Ustvari poster"):
    colors = THEMES[theme_name]
    place = f"{city}, {country}"
    
    # Spinner mora biti pravilno zamaknjen (4 presledki)
    with st.spinner("Pridobivam podatke iz zemljevidov... Počakaj trenutek."):
        try:
            # Koda znotraj spinnerja mora biti še dodatno zamaknjena
            img = create_map_poster(place, colors, dist)
            st.image(img, caption=f"{city}, {country}", use_container_width=True)
            
            # Gumb za prenos slike
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="Prenesi poster",
                data=byte_im,
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Prišlo je do napake: {e}")

# Razdelek za donacije (PayPal)
st.write("---")
st.subheader("☕ Podpri projekt")
st.write("Če ti je generator všeč, lahko podpreš moj trud z majhno donacijo. Vsak evro pomaga pri razvoju in vzdrževanju strani!")

# Tvoja uradna PayPal povezava
paypal_url = "https://www.paypal.me/NeonPunkSlo"

st.markdown(f'''
    <a href="{paypal_url}" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate with PayPal">
    </a>
''', unsafe_allow_html=True)

st.caption("Hvala za tvojo podporo! 🚀")