import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Cyberpunk Original": {"bg": "#050B16", "water": "#0A1A2F", "text": "#FFD700", "ac": "#FF00FF", "glavne": "#FFD700", "ostalo": "#FFD700"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

# 2. POPRAVLJENO: Dinamično iskanje lokacije
def dobi_koordinate_mesta(mesto, drzava):
    try:
        # Poišče dejanske koordinate katerega koli mesta na svetu
        lokacija = ox.geocode(f"{mesto}, {drzava}")
        return lokacija # Vrne (lat, lon)
    except:
        return None

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    koordinate = dobi_koordinate_mesta(mesto, drzava)
    if not koordinate:
        raise ValueError(f"Mesta '{mesto}' ni bilo mogoče najti.")
    
    lat, lon = koordinate
    barve = TEME[ime_teme]
    
    # simplify=False prepreči prekinjene linije na AC
    G = ox.graph_from_point((lat, lon), dist=razdalja + 500, network_type="all", simplify=False, retain_all=True)
    
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        # AC (motorway) dobi rožnato barvo in debelino
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"]); road_widths.append(7.0)
        else:
            road_colors.append(barve["glavne"]); road_widths.append(1.2)

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # Dinamičen izpis imena in koordinat
    plt.subplots_adjust(bottom=0.2)
    fig.text(0.5, 0.15, mesto.upper(), fontsize=70, color=barve["text"], ha="center", fontweight="bold", letterspacing=8)
    fig.text(0.5, 0.11, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.07, koord_tekst, fontsize=18, color=barve["text"], ha="center", family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- UI ---
st.set_page_config(page_title="Mestna Poezija Premium")
st.title("🎨 MESTNA POEZIJA")

mesto_vnos = st.text_input("Vnesi ime mesta (npr. Jesenice, Piran...)", "Jesenice")
drzava_vnos = st.text_input("Država", "Slovenija")
zoom_vnos = st.slider("Velikost območja (m)", 500, 10000, 3000)
tema_vnos = st.selectbox("Izberi umetniški slog", list(TEME.keys()))

if st.button("✨ USTVARI PERFEKTEN POSTER"):
    with st.spinner(f"Iščem {mesto_vnos} in rišem zemljevid..."):
        try:
            slika = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI POSTER", slika, file_name=f"{mesto_vnos}_poster.png")
        except Exception as e:
            st.error(f"Napaka: {e}. Poskusi s točnejšim imenom mesta.")