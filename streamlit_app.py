import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. DEFINICIJA TEM
TEME = {
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"}
}

# 2. FIKSNE KOORDINATE (Da preprečiva Connection Refused napako)
def dobi_koordinate_fiksno(mesto):
    # Ročni vpis za najpogostejše kraje, da ne rabiš interneta
    podatki = {
        "Piran": "45.5283° S / 13.5683° V",
        "Ljubljana": "46.0569° S / 14.5058° V",
        "Maribor": "46.5547° S / 15.6459° V",
        "Haloze": "46.3333° S / 15.9333° V"
    }
    return podatki.get(mesto, "46.0500° S / 14.5000° V")

# 3. FUNKCIJA ZA IZRIS
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Tukaj OSMnx še vedno rabi dostop, a običajno ne blokira tako hitro kot Nominatim
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline"], "water": True}, dist=razdalja)
    except:
        voda = None

    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk"]:
            road_colors.append(barve["ac"]); road_widths.append(3.5)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(1.8)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.5)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    plt.subplots_adjust(bottom=0.2)
    fig.text(0.5, 0.12, mesto.upper(), fontsize=70, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.08, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.7)
    
    # Uporaba fiksne funkcije namesto klica na Nominatim
    koordinata_str = dobi_koordinate_fiksno(mesto)
    fig.text(0.5, 0.05, koordinata_str, fontsize=16, color=barve["text"], ha="center", alpha=0.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

# 4. VMESNIK
st.set_page_config(page_title="Mestna Poezija")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Kraj", "Piran")
razdalja = st.slider("Zoom (metri)", 500, 5000, 2500)
tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ"):
    try:
        res = ustvari_poster(mesto, "Slovenija", razdalja, tema)
        st.image(res)
    except Exception as e:
        st.error(f"OSMnx strežnik je preobremenjen. Počakaj na zadnji požirek piva in poskusi znova. Napaka: {e}")