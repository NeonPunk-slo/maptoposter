import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

def create_map_poster(city, country, dist):
    place = f"{city}, {country}"
    # Pridobivanje podatkov
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    
    # Ustvarjanje figure
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color="#FFFFFF", edge_linewidth=0.8,
        bgcolor="#202124", show=False, close=False
    )
    
    # DODAJANJE NAPISOV
    # Premaknemo graf malce navzgor, da naredimo prostor za tekst
    plt.subplots_adjust(bottom=0.2)
    
    # Velik napis mesta
    plt.text(0.5, 0.12, city.upper(), fontsize=25, color="white", 
             ha="center", transform=fig.transFigure, fontweight="bold", letterspacing=2)
    
    # Manjši napis države
    plt.text(0.5, 0.07, country.upper(), fontsize=12, color="white", 
             ha="center", transform=fig.transFigure, alpha=0.7)

    # Shranjevanje
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#202124", dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

st.title("🎨 Generator mestnih posterjev")
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)

if st.button("🚀 Ustvari poster"):
    with st.spinner("Ustvarjam poster z napisi..."):
        try:
            img_buf = create_map_poster(city, country, dist)
            st.image(img_buf, use_container_width=True)
            
            st.download_button(
                label="Prenesi poster",
                data=img_buf,
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Napaka: {e}")

# PayPal
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'<a href="{paypal_url}" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif"></a>', unsafe_allow_html=True)