import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Cyberpunk Original": {"bg": "#050B16", "water": "#0A1A2F", "text": "#FFD700", "ac": "#FF00FF", "glavne": "#FFD700", "ostalo": "#FFD700"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"}
}

# 2. FUNKCIJA ZA DINAMIČNO ISKANJE (Brez fiksnih koordinat!)
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    # Poiščemo koordinate za katerokoli vpisano mesto
    try:
        lat, lon = ox.geocode(f"{mesto}, {drzava}")
    except:
        raise ValueError(f"Mesta '{mesto}' ni bilo mogoče najti. Preveri črkovanje.")

    barve = TEME[ime_teme]
    ox.settings.timeout = 240
    
    # Naložimo surovo mrežo (simplify=False zagotavlja, da so AC zvezne)
    G = ox.graph_from_point((lat, lon), dist=razdalja + 500, network_type="all", simplify=False, retain_all=True)
    
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        # AC (motorway in trunk) dobijo rožnato barvo in maksimalno debelino
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"]); road_widths.append(7.0)
        else:
            road_colors.append(barve["glavne"]); road_widths.append(1.2)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    # Omejimo pogled na točno izbrano razdaljo
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # IZBOLJŠAN IZPIS BESEDILA (Brez letterspacing napake)
    plt.subplots_adjust(bottom=0.2)
    
    # Ročno naredimo razmik med črkami s presledki
    mesto_spaced = "  ".join(mesto.upper())
    drzava_spaced = "    ".join(drzava.upper())
    
    fig.text(0.5, 0.16, mesto_spaced, fontsize=60, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.11, drzava_spaced, fontsize=24, color=barve["text"], ha="center", alpha=0.8)
    
    # Pravilne koordinate za točno to lokacijo
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.07, koord_tekst, fontsize=18, color=barve["text"], ha="center", family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija Premium")
st.title("🎨 MESTNA POEZIJA")

mesto_vnos = st.text_input("Vnesi ime mesta (npr. Jesenice, Maribor, Haloze...)", "Jesenice")
drzava_vnos = st.text_input("Država", "Slovenija")
zoom_vnos = st.number_input("Zoom (m)", 500, 10000, 3000)
tema_vnos = st.selectbox("Izberi slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ MOJSTROVINO"):
    with st.spinner(f"Iščem {mesto_vnos} in pripravljam tisk..."):
        try:
            slika = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI SLIKO", slika, file_name=f"{mesto_vnos}_poster.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

st.write("---")
st.markdown('<center><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color:#ffc439; border-radius:20px; padding:12px 24px; font-weight:bold; border:none; cursor:pointer;">💛 PayPal Donacija</button></a></center>', unsafe_allow_html=True)