import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from shapely.geometry import box

# 1. TEME (Pripravljene na kontrast kopno/morje)
THEMES = {
    "Morski razgled (Moder)": {"bg_sea": "#0077BE", "land": "#F1F4F7", "roads": "#757575", "text": "#063951"},
    "Klasičen temen": {"bg_sea": "#1a1a1b", "land": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Neon Punk": {"bg_sea": "#1a0033", "land": "#000000", "roads": "#ff00ff", "text": "#00ffff"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_final_v5")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° N / {abs(loc.longitude):.4f}° E"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # 1. Pridobivanje cest
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # 2. Pridobivanje obalne linije / kopnega
    try:
        # Iskanje kopnega preko administrativnih meja ali obale
        kopno = ox.features_from_address(kraj, tags={"place": "suburb", "boundary": "administrative", "landuse": ["residential", "commercial"]}, dist=razdalja)
    except:
        kopno = None

    # Ustvarjanje figure - OZADJE JE BARVA MORJA
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg_sea"])
    ax.set_facecolor(barve["bg_sea"])
    
    # Izris kopnega (če obstaja, sicer bo ozadje ostalo modro pod cestami)
    if kopno is not None and not kopno.empty:
        kopno.plot(ax=ax, color=barve["land"], zorder=0)
    
    # Izris cest
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.7, show=False, close=False)
    
    ax.axis('off')
    
    # DODAJANJE BELEGA PASU SPODAJ (Mora biti čez vse)
    plt.subplots_adjust(bottom=0.25)
    rect = plt.Rectangle((0, 0), 1, 0.25, transform=fig.transFigure, facecolor="#F1F4F7", zorder=10)
    fig.patches.append(rect)
    
    # NAPISI IN KOORDINATE (Znotraj belega pasu)
    fig.text(0.5, 0.14, mesto.upper(), fontsize=60, color=barve["text"], ha="center", fontweight="bold", zorder=11)
    fig.text(0.5, 0.09, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8, zorder=11)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.05, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace", zorder=11)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg_sea"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT VMESNIK ---
st.title("🎨 Popoln Generator Posterjev")

mesto = st.text_input("Ime mesta", "Piran")
drzava = st.text_input("Država", "Slovenia")
razdalja = st.slider("Zoom (metri)", 1000, 8000, 4000)
izbrana_tema = st.selectbox("Izberi stil", list(THEMES.keys()))

if st.button("🚀 Ustvari Poster"):
    with st.spinner("Generiram morje in koordinate..."):
        try:
            slika = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika, use_container_width=True)
            st.download_button("Preuzmi Poster", slika, file_name=f"{mesto}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")