import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME (Uravnotežene za tisk)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. OFFLINE KOORDINATE (Da te reddit naval ne sesuje)
def dobi_koordinate_perfect(mesto):
    mesto = mesto.lower().strip()
    db = {
        "ljubljana": "46.0569° N / 14.5058° E",
        "piran": "45.5283° N / 13.5683° E",
        "portorož": "45.5144° N / 13.5906° E",
        "izola": "45.5397° N / 13.6593° E",
        "koper": "45.5469° N / 13.7294° E",
        "maribor": "46.5547° N / 15.6459° E",
        "haloze": "46.3333° N / 15.9333° E"
    }
    return db.get(mesto, "46.0500° N / 14.5000° E")

# 3. GLAVNA FUNKCIJA ZA IZRIS
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Pridobivanje cest - OSMnx (najbolj stabilen del)
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    # Stil cest (perfekcija linij)
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(4.2)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.2)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.7)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    # Postavitev besedila v stilu luksuznih posterjev
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.22)
    
    fig.text(0.5, 0.14, mesto.upper(), fontsize=68, color=barve["text"], ha="center", fontweight="bold", letterspacing=6)
    fig.text(0.5, 0.10, drzava.upper(), fontsize=26, color=barve["text"], ha="center", alpha=0.8, letterspacing=12)
    
    koordinata_str = dobi_koordinate_perfect(mesto)
    fig.text(0.5, 0.06, koordinata_str, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija Premium", layout="centered")

# Skrijemo Streamlit UI elemente za boljši vtis
st.markdown("<style>header {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: black;}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>Mestna Poezija</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Premium vektorski posterji za tvoj dom.</p>", unsafe_allow_html=True)

with st.form("generator_form"):
    mesto = st.text_input("Vnesi ime mesta (npr. Piran, Ljubljana...)", "Piran")
    razdalja = st.slider("Velikost območja (m)", 500, 10000, 2500)
    izbrana_tema = st.selectbox("Izberi umetniški slog", list(TEME.keys()))
    submit = st.form_submit_button("✨ USTVARI PERFEKTEN POSTER")

if submit:
    with st.spinner("Rišem tvojo umetnino..."):
        try:
            slika = ustvari_poster(mesto, "Slovenija", razdalja, izbrana_tema)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI SLIKO VISOKE LOČLJIVOSTI (PNG)", slika, file_name=f"{mesto}_premium.png", mime="image/png")
        except Exception as e:
            st.error("Napaka pri generiranju. Poskusi z drugim mestom ali manjšim zoomom.")

# Monetizacija
st.write("---")
st.markdown(f'''<div style="text-align: center;"><p style="color: white;">Ti je projekt všeč? Pomagaj mi do stanovanja na morju!</p><a href="https://www.paypal.me/NeonPunkSlo" target="_blank" style="text-decoration: none;"><div style="background-color: #ffc439; color: black; padding: 15px 30px; border-radius: 40px; font-weight: bold; display: inline-block; font-size: 20px;">💛 PayPal Donacija</div></a></div>''', unsafe_allow_html=True)