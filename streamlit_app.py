import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. MOČNEJŠI ISKALNIK KOORDINAT
@st.cache_data
def pridobi_lat_lon(mesto, drzava):
    # Fiksne točke za 100% zanesljivost
    fiksno = {
        "ljubljana": (46.0569, 14.5058),
        "piran": (45.5283, 13.5683),
        "maribor": (46.5547, 15.6459),
        "haloze": (46.3333, 15.9333)
    }
    m = mesto.lower().strip()
    if m in fiksno: return fiksno[m]
    
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_2026_final")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        return (loc.latitude, loc.longitude) if loc else (46.05, 14.50)
    except:
        return (46.05, 14.50)

# 3. GLAVNA FUNKCIJA (Izboljšano nalaganje mreže)
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    lat, lon = pridobi_lat_lon(mesto, drzava)
    barve = TEME[ime_teme]
    
    # Nalaganje mreže okoli točke (bolj stabilno kot naslov)
    ox.settings.timeout = 180
    G = ox.graph_from_point((lat, lon), dist=razdalja, network_type="all", simplify=True)
    
    try:
        voda = ox.features_from_point((lat, lon), tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        # Razširjen nabor za AC (vključno z obvoznicami)
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link", "motorway_junction"]:
            road_colors.append(barve["ac"]); road_widths.append(5.0)
        elif h_type in ["primary", "secondary", "primary_link", "secondary_link"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.8)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.8)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    # Napisi
    plt.subplots_adjust(bottom=0.2)
    mesto_str = "  ".join(mesto.upper())
    fig.text(0.5, 0.14, mesto_str, fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    # Dinamične koordinate
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.06, koord_tekst, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija Premium")
st.title("🎨 MESTNA POEZIJA")

c1, c2 = st.columns(2)
with c1:
    mesto = st.text_input("Mesto", "Ljubljana")
    zoom = st.number_input("Zoom (m)", 500, 15000, 4000)
with c2:
    drzava = st.text_input("Država", "Slovenija")
    tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ USTVARI"):
    with st.spinner("Pridobivam podatke (to lahko traja, ker rišem vse AC)..."):
        try:
            res = ustvari_poster(mesto, drzava, zoom, tema)
            st.image(res, use_container_width=True)
            st.download_button("📥 PRENESI", res, file_name=f"{mesto}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# PayPal
st.write("---")
st.markdown(f'<center><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color:#ffc439; border-radius:20px; padding:10px 20px; font-weight:bold; cursor:pointer; border:none;">💛 PayPal Donacija</button></a></center>', unsafe_allow_html=True)