import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Z usklajenimi barvami za vodo in koordinate)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00FFFF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_voda_fix")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Pridobivanje cest
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # PRIDOBIVANJE VODE (Razširjen nabor za morje in reke)
    # Dodane oznake: coastline, bay, strait, river
    try:
        voda = ox.features_from_address(kraj, 
                                        tags={"natural": ["water", "coastline", "bay", "strait"], 
                                              "water": True, 
                                              "waterway": ["river", "canal"]}, 
                                        dist=razdalja)
    except:
        voda = None

    # Logika za barve cest
    road_colors = []
    road_widths = []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"])
            road_widths.append(3.8)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"])
            road_widths.append(1.8)
        else:
            road_colors.append(barve["ostalo"])
            road_widths.append(0.5)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # IZRIS VODE (Najprej voda, da so ceste čez njo)
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1, alpha=1.0)
    
    # Izris cest
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    ax.axis('off')
    plt.subplots_adjust(bottom=0.28)
    
    # NAPISI IN KOORDINATE (Fiksno na dnu)
    fig.text(0.5, 0.18, mesto.upper(), fontsize=70, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.13, drzava.upper(), fontsize=28, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate_tekst = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.08, koordinate_tekst, fontsize=20, color=barve["text"], ha="center", alpha=0.7, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- VMESNIK ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.markdown("<h1 style='text-align: center;'>Mestna Poezija</h1>", unsafe_allow_html=True)

mesto = st.text_input("Ime kraja", "Piran")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Zoom (v metrih)", min_value=500, max_value=30000, value=3500, step=100)
izbrana_tema = st.selectbox("Izberi slog", list(TEME.keys()))

if st.button("✨ Ustvari umetniško delo"):
    with st.spinner("Rišem morje, ceste in koordinate..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster", data=slika_buf, file_name=f"{mesto}_art.png", mime="image/png")
        except Exception as e:
            st.error(f"Prišlo je do napake pri pridobivanju podatkov: {e}")

# --- PAYPAL ---
st.write("---")
st.markdown(f'''
    <div style="text-align: center;">
        <p style="color: #888;">Podpri razvoj "Mestne Poezije"!</p>
        <a href="https://www.paypal.me/NeonPunkSlo" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block;">
                PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)