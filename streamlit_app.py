import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. OFFLINE KOORDINATE (Zaščita pred Reddit navaloma)
def dobi_koordinate_offline(mesto):
    mesto = mesto.lower().strip()
    db = {
        "ljubljana": "46.0569° N / 14.5058° E",
        "piran": "45.5283° N / 13.5683° E",
        "portorož": "45.5144° N / 13.5906° E",
        "izola": "45.5397° N / 13.6593° E",
        "koper": "45.5469° N / 13.7294° E",
        "maribor": "46.5547° N / 15.6459° E",
        "haloze": "46.3333° N / 15.9333° E",
        "celje": "46.2360° N / 15.2677° E"
    }
    return db.get(mesto, "46.0500° N / 14.5000° E")

# 3. GLAVNA FUNKCIJA
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    ox.settings.timeout = 120  # Povečan timeout za Reddit naval
    ox.settings.use_cache = True
    
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    try:
        G = ox.graph_from_address(kraj, dist=razdalja, network_type="all", retain_all=True)
    except:
        G = ox.graph_from_address(mesto, dist=razdalja, network_type="all", retain_all=True)
    
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(4.5)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.5)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.8)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.22)
    
    mesto_str = "  ".join(mesto.upper())
    drzava_str = "    ".join(drzava.upper()) if drzava else ""
    
    fig.text(0.5, 0.14, mesto_str, fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava_str, fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    koordinata_str = dobi_koordinate_offline(mesto)
    fig.text(0.5, 0.06, koordinata_str, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI PREOBRAZBA ---
st.set_page_config(page_title="Mestna Poezija Premium", layout="centered")
st.markdown("<style>header {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #0e1117; color: white;}</style>", unsafe_allow_html=True)

st.title("🎨 MESTNA POEZIJA")
st.write("Vnesi podatke in ustvari unikatno vektorsko karto.")

# Uporaba stolpcev za boljši UI
col1, col2 = st.columns(2)

with col1:
    mesto_vnos = st.text_input("Ime mesta", "Piran")
    # Zamenjava sliderja z number_input
    zoom_vnos = st.number_input("Zoom (v metrih od središča)", min_value=100, max_value=20000, value=2500, step=100)

with col2:
    drzava_vnos = st.text_input("Država", "Slovenija")
    tema_vnos = st.selectbox("Izberi umetniški slog", list(TEME.keys()))

st.write("---")

if st.button("✨ GENERIRAJ PERFEKTEN POSTER"):
    with st.spinner("Pridobivanje vektorskih podatkov in risanje..."):
        try:
            poster = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
            st.image(poster, use_container_width=True)
            st.download_button("📥 PRENESI SLIKO (300 DPI)", poster, file_name=f"{mesto_vnos}_poezija.png", mime="image/png")
        except Exception as e:
            st.error(f"Strežnik je zaseden ali kraj ni najden. Poskusi z manjšim zoomom. (Podrobnosti: {e})")

# Podpora za tvoje sanje o morju
st.write("---")
st.markdown(f'''
    <div style="text-align: center;">
        <p style="color: #aaa;">Ti je aplikacija všeč? Pomagaj mi do stanovanja na morju!</p>
        <a href="https://www.paypal.me/NeonPunkSlo" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 15px 30px; border-radius: 40px; font-weight: bold; display: inline-block; font-size: 1.2em;">
                💛 PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)