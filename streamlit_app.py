import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

def create_map_poster(city, country, dist):
    place = f"{city}, {country}"
    # Pridobivanje podatkov o cestah
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    
    # Ustvarjanje figure z večjim spodnjim robom za napise
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color="#FFFFFF", edge_linewidth=0.8,
        bgcolor="#202124", show=False, close=False
    )
    
    # DODAJANJE VELIKIH NAPISOV
    # Prilagoditev robov, da je spodaj dovolj prostora
    plt.subplots_adjust(bottom=0.25)
    
    # Glavni napis mesta (VELIKE ČRKE, KREPKO)
    # Uporabimo ax.text namesto plt.text za boljšo kontrolo
    fig.text(0.5, 0.15, city.upper(), fontsize=35, color="white", 
             ha="center", fontweight="bold", family="sans-serif")
    
    # Napis države (manjši, malce prosojen)
    fig.text(0.5, 0.08, country.upper(), fontsize=15, color="white", 
             ha="center", alpha=0.6, family="sans-serif")

    # Shranjevanje v visoki ločljivosti
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#202124", dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# Nastavitve Streamlit vmesnika
st.title("🎨 Generator mestnih posterjev")
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)

if st.button("🚀 Ustvari poster"):
    with st.spinner("Ustvarjam poster z velikimi napisi..."):
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
            st.error(f"Prišlo je do napake: {e}")

# PayPal gumb za donacije (povezava iz tvojih prejšnjih korakov)
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p>Podpri projekt in mi časti kavo! ☕</p>
        <a href="{paypal_url}" target="_blank">
            <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate">
        </a>
    </div>
''', unsafe_allow_html=True)