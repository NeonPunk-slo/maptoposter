import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# Funkcija za ustvarjanje zemljevida
def create_map_poster(place, dist):
    # Pridobivanje cest (network) namesto features, kar je hitreje in bolj zanesljivo
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    
    # Risanje
    fig, ax = ox.plot_graph(
        graph,
        node_size=0,
        edge_color="#FFFFFF",
        edge_linewidth=0.8,
        bgcolor="#202124",
        show=False,
        close=True
    )
    
    # Shranjevanje v buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#202124", dpi=300, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return buf

# Nastavitve strani
st.title("🎨 Generator mestnih posterjev")
st.write("Vnesi podatke in ustvari svoj unikatni zemljevid.")

city = st.text_input("Mesto", "Jesenice")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)

if st.button("🚀 Ustvari poster"):
    place = f"{city}, {country}"
    with st.spinner("Pridobivam podatke iz zemljevidov... Počakaj trenutek."):
        try:
            img_buf = create_map_poster(place, dist)
            st.image(img_buf, caption=place, use_container_width=True)
            
            st.download_button(
                label="Prenesi poster",
                data=img_buf,
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Napaka pri generiranju: {e}")

# PayPal razdelek
st.write("---")
st.subheader("☕ Podpri projekt")
st.write("Če ti je generator všeč, me lahko podpreš za kavo!")

paypal_url = "https://www.paypal.me/NeonPunkSlo"

st.markdown(f'''
    <a href="{paypal_url}" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="PayPal">
    </a>
''', unsafe_allow_html=True)