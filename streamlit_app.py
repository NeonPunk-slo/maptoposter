import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. DEFINICIJA TEM (Barvne palete, ki so ti bile všeč)
TEME = {
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. VARNOSTNO ISKANJE KOORDINAT (Z uporabo cache-a, da nas ne blokirajo)
@st.cache_data(show_spinner=False)
def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_final_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "46.0569° S / 14.5058° V"
    except:
        # Če nas Nominatim blokira (tvoja napaka), vrnemo fiksno vrednost, da aplikacija ne crkne
        return "Koordinate začasno nedostopne"

# 3. GLAVNA FUNKCIJA ZA IZRIS POSTERJA
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Pridobivanje vektorskih podatkov o cestah
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    try:
        # Pridobivanje vodnih površin
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    # Barve in debeline glede na tip ceste
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(3.5)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(1.8)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.5)

    # Ustvarjanje slike (Matplotlib)
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # Risanje vode
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Risanje cest
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    # Prostor za besedilo
    plt.subplots_adjust(bottom=0.2)
    
    # Stilski napisi
    fig.text(0.5, 0.12, mesto.upper(), fontsize=70, color=barve["text"], ha="center", fontweight="bold", letterspacing=5)
    fig.text(0.5, 0.08, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.7, letterspacing=15)
    
    koordinata_str = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.05, koordinata_str, fontsize=16, color=barve["text"], ha="center", alpha=0.5, family="monospace")

    # Priprava za prikaz in prenos
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

# 4. STREAMLIT VMESNIK
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.markdown("<style>.stApp {background-color: #000000; color: white;}</style>", unsafe_allow_html=True)

st.title("🎨 Mestna Poezija")

col1, col2 = st.columns(2)
with col1:
    vnos_mesto = st.text_input("Kraj", "Piran")
    vnos_zoom = st.slider("Zoom (metri)", 500, 10000, 3000)
with col2:
    vnos_drzava = st.text_input("Država", "Slovenija")
    vnos_tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ UMETNINO"):
    with st.spinner("Pripravljam tvoj poster... to lahko traja minuto."):
        try:
            poster_buf = ustvari_poster(vnos_mesto, vnos_drzava, vnos_zoom, vnos_tema)
            st.image(poster_buf)
            st.download_button("📥 Prenesi PNG", poster_buf, file_name=f"{vnos_mesto}_poster.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka pri risanju: {e}")

# Donacija
st.write("---")
st.markdown(f'<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; padding: 10px 20px; border-radius: 20px; border: none; font-weight: bold; cursor: pointer;">💛 PayPal Donacija</button></a></div>', unsafe_allow_html=True)