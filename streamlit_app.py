import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# Teme ostajajo enake
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

def dobi_koordinate_varno(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=5)
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
    except:
        pass
    return "Koordinate niso na voljo"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    try:
        # Pridobivanje cest
        G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
        
        # Varno pridobivanje vode
        try:
            voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
        except:
            voda = None

        road_colors, road_widths = [], []
        for u, v, k, data in G.edges(data=True, keys=True):
            h_type = data.get("highway", "unclassified")
            if h_type in ["motorway", "trunk"]:
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
        plt.subplots_adjust(bottom=0.22)
        
        # Napisi
        fig.text(0.5, 0.14, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
        fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
        
        koordinate = dobi_koordinate_varno(mesto, drzava)
        fig.text(0.5, 0.06, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=150) # Nižji DPI za hitrost
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        st.error(f"Napaka pri generiranju: {e}")
        return None

# --- VMESNIK ---
st.set_page_config(page_title="Mestna Poezija")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Ime kraja", "Ljubljana")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Zoom (metri)", min_value=500, value=5000)
izbrana_tema = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ Ustvari poster"):
    rezultat = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
    if rezultat:
        st.image(rezultat, use_container_width=True)
        st.download_button("📥 Prenesi PNG", rezultat, file_name=f"{mesto}.png")

# --- PAYPAL DONACIJA ---
st.write("---")
st.markdown(f'''<div style="text-align: center;"><a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="background-color: #ffc439; border-radius: 20px; padding: 10px 20px; font-weight: bold; border: none;">💛 PayPal Donacija</button></a></div>''', unsafe_allow_html=True)