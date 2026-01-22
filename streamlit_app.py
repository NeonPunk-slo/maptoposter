import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (AC so kontra barve)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00FFFF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_fix_coords")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "46.0569° S / 14.5058° V"
    except:
        return "46.0569° S / 14.5058° V"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # Pridobivanje vode
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    # Kontrastne ceste
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(4.0)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.0)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.6)

    # Izris
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    ax.axis('off')
    
    # POMEMBNO: Pustimo dovolj prostora spodaj (bottom=0.2)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)
    
    # Dodajanje besedila s fiksnimi koordinatami y
    fig.text(0.5, 0.14, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koordinata = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.06, koordinata, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    # KLJUČNA SPREMEMBA: Odstranjen bbox_inches='tight'
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- VMESNIK ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Ime kraja", "Piran")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Zoom (v metrih)", min_value=500, value=3500)
izbrana_tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("🚀 Ustvari poster"):
    with st.spinner("Rišem zemljevid in koordinate..."):
        try:
            slika = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika, use_container_width=True)
            st.download_button("📥 Prenesi PNG", slika, file_name=f"{mesto}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")