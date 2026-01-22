import streamlit as st
import io
import osmnx as ox
from PIL import Image

# Funkcija za ustvarjanje zemljevida (zdaj je direktno tukaj)
def create_map_poster(place, colors, dist):
    # Pridobivanje podatkov iz OpenStreetMap
    gdf = ox.features_from_place(place, tags={"highway": True}, buffer_dist=dist)
    
    # Risanje s statično barvno shemo
    fig, ax = ox.plot_graph(
        ox.graph_from_address(place, dist=dist),
        node_size=0,
        edge_color=colors["roads"],
        edge_linewidth=1,
        bgcolor=colors["land"],
        show=False,
        close=True
    )
    
    # Pretvorba v sliko za Streamlit
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=300)
    buf.seek(0)
    return Image.open(buf)

# Nastavitve strani
st.title("🎨 Generator mestnih posterjev")
st.write("Vnesi podatke in ustvari svoj unikatni zemljevid.")

# Vnosi
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)

# Barvna shema
colors = {
    "land": "#202124",
    "roads": "#FFFFFF"
}

if st.button("🚀 Ustvari poster"):
    place = f"{city}, {country}"
    with st.spinner("Pridobivam podatke... To lahko traja do 1 minute."):
        try:
            img = create_map_poster(place, colors, dist)
            st.image(img, caption=place, use_container_width=True)
            
            # Gumb za prenos
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="Prenesi poster",
                data=buf.getvalue(),
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Napaka pri generiranju. Poskusi drugo mesto ali večjo razdaljo. Opis: {e}")

# PayPal razdelek
st.write("---")
st.subheader("☕ Podpri projekt")
st.write("Če ti je generator všeč, me lahko podpreš za kavo!")

# Tvoja povezava
paypal_url = "https://www.paypal.me/NeonPunkSlo"

st.markdown(f'''
    <a href="{paypal_url}" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="PayPal">
    </a>
''', unsafe_allow_html=True)