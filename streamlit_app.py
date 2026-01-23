import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00F2FF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. FIKSNE KOORDINATE (Da Reddit naval ne sesuje iskanja)
def dobi_lat_lon(mesto):
    db = {
        "ljubljana": (46.0569, 14.5058),
        "piran": (45.5283, 13.5683),
        "maribor": (46.5547, 15.6459),
        "haloze": (46.3333, 15.9333)
    }
    return db.get(mesto.lower().strip(), (46.0569, 14.5058))

# 3. GLAVNA FUNKCIJA Z FIXOM ZA AC
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    lat, lon = dobi_lat_lon(mesto)
    barve = TEME[ime_teme]
    
    # Nastavitve za stabilnost
    ox.settings.timeout = 180
    ox.settings.use_cache = True
    
    # Naložimo graf (večje območje za stabilne robove)
    G = ox.graph_from_point((lat, lon), dist=razdalja + 500, network_type="all", simplify=True, retain_all=True)
    
    # Poskusimo naložiti vodo
    try:
        voda = ox.features_from_point((lat, lon), tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    # LOGIKA ZA DEBELINE (Fix za prekinjene AC)
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        # AC in vse obvoznice (vključno s priključki)
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"]); road_widths.append(6.0) # Še debelejše za vizualno zveznost
        # Glavne vpadnice
        elif h_type in ["primary", "secondary", "primary_link", "secondary_link"]:
            road_colors.append(barve["glavne"]); road_widths.append(3.5)
        # Ostalo
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.8)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Izris grafa
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    # Omejitev pogleda na točen zoom
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # Stilsko besedilo
    plt.subplots_adjust(bottom=0.2)
    mesto_clean = mesto.upper().replace("", "  ").strip()
    fig.text(0.5, 0.14, mesto_clean, fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper().replace("", "    ").strip(), fontsize=24, color=barve["text"], ha="center", alpha=0.8)
    
    # Koordinate
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.06, koord_tekst, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija Premium")
st.markdown("<h1 style='text-align: center;'>🎨 MESTNA POEZIJA</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    mesto = st.text_input("Ime mesta", "Ljubljana")
    zoom = st.number_input("Zoom (m od središča)", 500, 15000, 4000)
with c2:
    drzava = st.text_input("Država", "Slovenija")
    tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ PRESEŽEK"):
    with st.spinner("Rišem brezhibne linije..."):
        try:
            slika = ustvari_poster(mesto, drzava, zoom, tema)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI (PNG)", slika, file_name=f"{mesto}_premium.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

st.write("---")
st.markdown('<center><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color:#ffc439; border-radius:20px; padding:12px 24px; font-weight:bold; border:none; cursor:pointer;">💛 PayPal Donacija</button></a></center>', unsafe_allow_html=True)