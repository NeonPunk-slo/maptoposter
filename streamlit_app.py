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

# 2. FIKSNE KOORDINATE
def dobi_lat_lon(mesto):
    db = {
        "ljubljana": (46.0569, 14.5058),
        "piran": (45.5283, 13.5683),
        "maribor": (46.5547, 15.6459),
        "haloze": (46.3333, 15.9333)
    }
    return db.get(mesto.lower().strip(), (46.0569, 14.5058))

# 3. PERFEKCIONISTIČNA FUNKCIJA ZA IZRIS
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    lat, lon = dobi_lat_lon(mesto)
    barve = TEME[ime_teme]
    
    ox.settings.timeout = 240
    ox.settings.use_cache = True
    
    # KLJUČNA SPREMEMBA: simplify=False in retain_all=True
    # To prepreči, da bi OSMnx "optimiziral" (beri: izbrisal) dele obvoznice
    G = ox.graph_from_point((lat, lon), dist=razdalja + 500, network_type="all", simplify=False, retain_all=True)
    
    try:
        voda = ox.features_from_point((lat, lon), tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        # AC in trunk (vse kar tvori obroč)
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"]); road_widths.append(7.0) # Ekstremna debelina za zlitje
        # Glavne ceste
        elif h_type in ["primary", "secondary", "primary_link", "secondary_link"]:
            road_colors.append(barve["glavne"]); road_widths.append(3.8)
        # Vse ostalo
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.8)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Izris z zaobljenimi robovi linij (solid_capstyle), da ni lukenj med segmenti
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, 
                  show=False, close=False, edge_alpha=1)
    
    # Ponovno umerjanje pogleda na točen zoom
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # Tekstovni del
    plt.subplots_adjust(bottom=0.2)
    mesto_clean = "  ".join(mesto.upper())
    fig.text(0.5, 0.14, mesto_clean, fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, "  ".join(drzava.upper()), fontsize=24, color=barve["text"], ha="center", alpha=0.8)
    
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
    mesto_vnos = st.text_input("Ime mesta", "Ljubljana")
    zoom_vnos = st.number_input("Zoom (m)", 500, 15000, 4000)
with c2:
    drzava_vnos = st.text_input("Država", "Slovenija")
    tema_vnos = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ PERFEKCIJO"):
    with st.spinner("Nalagam surovo mrežo (brez poenostavljanja)... to bo trajalo kakšno minuto."):
        try:
            slika = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI (PNG)", slika, file_name=f"{mesto_vnos}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

st.write("---")
st.markdown('<center><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color:#ffc439; border-radius:20px; padding:12px 24px; font-weight:bold; border:none; cursor:pointer;">💛 PayPal Donacija</button></a></center>', unsafe_allow_html=True)