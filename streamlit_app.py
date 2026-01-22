import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME
THEMES = {
    "Dark Mode": {"bg": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Vintage": {"bg": "#f4f1ea", "roads": "#5b5b5b", "text": "#333333"},
    "Neon": {"bg": "#000000", "roads": "#ff00ff", "text": "#00ffff"}
}

# 2. ISKANJE KOORDINAT
def get_coords(city, country):
    try:
        geolocator = Nominatim(user_agent="poster_gen_2026")
        loc = geolocator.geocode(f"{city}, {country}")
        return f"{abs(loc.latitude):.4f}° {'N' if loc.latitude >= 0 else 'S'} / {abs(loc.longitude):.4f}° {'E' if loc.longitude >= 0 else 'W'}"
    except:
        return "COORDINATES NOT FOUND"

# 3. USTVARJANJE POSTERJA
def create_map_poster(city, country, dist, theme):
    place = f"{city}, {country}"
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    colors = THEMES[theme]
    
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color=colors["roads"], edge_linewidth=0.8,
        bgcolor=colors["bg"], show=False, close=False
    )
    
    plt.subplots_adjust(bottom=0.28)
    
    # Napisi
    fig.text(0.5, 0.16, city.upper(), fontsize=32, color=colors["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.11, country.upper(), fontsize=14, color=colors["text"], ha="center", alpha=0.6)
    
    # KOORDINATE
    coords = get_coords(city, country)
    fig.text(0.5, 0.07, coords, fontsize=10, color=colors["text"], ha="center", alpha=0.5, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=colors["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# 4. VMESNIK
st.title("🎨 Premium City Poster Generator")
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Zoom", 500, 5000, 2500)
theme = st.selectbox("Stil", list(THEMES.keys()))

if st.button("🚀 Ustvari poster"):
    with st.spinner("Pridobivam podatke in koordinate..."):
        try:
            img = create_map_poster(city, country, dist, theme)
            st.image(img, use_container_width=True)
            st.download_button("Prenesi poster", img, file_name=f"{city}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# PAYPAL
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'<div style="text-align:center"><a href="{paypal_url}" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif"></a></div>', unsafe_allow_html=True)