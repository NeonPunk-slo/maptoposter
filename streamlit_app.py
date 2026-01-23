import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. TEME
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00FFFF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. FIKSNI SEZNAM KOORDINAT (Brez interneta!)
def dobi_koordinate_offline(mesto):
    mesto = mesto.lower().strip()
    lokalni_podatki = {
        "ljubljana": "46.0569° S / 14.5058° V",
        "piran": "45.5283° S / 13.5683° V",
        "maribor": "46.5547° S / 15.6459° V",
        "koper": "45.5469° S / 13.7294° V",
        "celje": "46.2360° S / 15.2677° V",
        "haloze": "46.3333° S / 15.9333° V"
    }
    # Če kraja ni na seznamu, vrne generične koordinate, da se koda ne ustavi
    return lokalni_podatki.get(mesto, "46.0500° S / 14.5000° V")

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # OSMnx uporablja Overpass API (ponavadi ne blokira)
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(4.0)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.0)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.6)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.22)
    
    fig.text(0.5, 0.14, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    # TUKAJ JE KLJUČ: Pokličemo offline funkcijo
    koordinata_str = dobi_koordinate_offline(mesto)
    fig.text(0.5, 0.06, koordinata_str, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)

mesto = st.text_input("Ime kraja", "Piran")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Zoom (v metrih)", min_value=500, max_value=20000, value=3000)
izbrana_tema = st.selectbox("Umetniški slog", list(TEME.keys()))

if st.button("✨ Ustvari poster"):
    with st.spinner("Pripravljam umetnino..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}_poezija.png")
        except Exception as e:
            st.error(f"Prišlo je do napake pri iskanju cest. Poskusi čez par minut ali zamenjaj kraj. Napaka: {e}")

# Donacija
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank" style="text-decoration: none;"><div style="background-color: #ffc439; color: black; padding: 14px 28px; border-radius: 30px; font-weight: bold; display: inline-block;">💛 PayPal Donacija</div></a></div>''', unsafe_allow_html=True)