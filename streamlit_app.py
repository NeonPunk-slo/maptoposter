import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. NASTAVITVE - To mora biti čisto prva stvar
st.set_page_config(page_title="MESTNA POEZIJA", page_icon="🎨")

# 2. TEME (Tvoje originalne)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#A5D1E8", "text": "#063951", "ac": "#E67E22", "glavne": "#063951"},
    "Gozdna tišina (Zelen)": {"bg": "#F9FBF7", "water": "#DDEBDB", "text": "#2D4221", "ac": "#8B4513", "glavne": "#4B633D"},
    "Skandinavski minimal": {"bg": "#FFFFFF", "water": "#E5E5E5", "text": "#222222", "ac": "#000000", "glavne": "#666666"},
    "Cyberpunk Original": {"bg": "#050B16", "water": "#0D1B2A", "text": "#FFD700", "ac": "#FF00FF", "glavne": "#FFD700"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#0F161E", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF"},
    "Polnočni neon": {"bg": "#000000", "water": "#111111", "text": "#00FF41", "ac": "#00FF41", "glavne": "#FFFFFF"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F"}
}

# 3. KLJUČ DO STABILNOSTI: Cache z omejitvijo
# max_entries=20 prepreči, da bi preveč shranjenih slik zapolnilo ves RAM
@st.cache_data(show_spinner="Gorenjska tehnologija pripravlja poster...", max_entries=20)
def ustvari_poster_cached(mesto, drzava, razdalja, ime_teme):
    try:
        lat, lon = ox.geocode(f"{mesto}, {drzava}")
        
        barve = TEME[ime_teme]
        ox.settings.timeout = 300
        
        north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)

        # Uporabimo network_type="drive", da je hitreje in zavzame manj spomina
        G = ox.graph_from_point((lat, lon), dist=razdalja, network_type="drive", simplify=True)
        
        try:
            water = ox.features_from_bbox(north, south, east, west, tags={'natural': ['water', 'bay'], 'waterway': ['riverbank']})
        except:
            water = None

        road_colors, road_widths = [], []
        for u, v, k, data in G.edges(data=True, keys=True):
            h_type = data.get("highway", "unclassified")
            if isinstance(h_type, list): h_type = h_type[0]
            if h_type in ["motorway", "trunk"]:
                road_colors.append(barve["ac"]); road_widths.append(3.0)
            else:
                road_colors.append(barve["glavne"]); road_widths.append(0.6)

        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor=barve["bg"])
        ax.set_facecolor(barve["bg"])
        
        if water is not None and not water.empty:
            water.plot(ax=ax, color=barve["water"], edgecolor='none')
        
        ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, 
                      edge_linewidth=road_widths, show=False, close=False)
        
        ax.set_ylim(south, north)
        ax.set_xlim(west, east)
        ax.axis('off')
        
        plt.subplots_adjust(bottom=0.22)
        fig.text(0.5, 0.11, mesto.upper(), fontsize=32, color=barve["text"], ha="center", fontweight='bold')
        fig.text(0.5, 0.08, drzava.upper(), fontsize=14, color=barve["text"], ha="center", alpha=0.7)
        
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight', pad_inches=0.4) # DPI na 150 za stabilnost
        buf.seek(0)
        plt.close(fig) # Vedno zapremo figuro, da sprostimo RAM
        return buf.getvalue()
    except Exception as e:
        return str(e)

# 4. UI (Streamlit)
st.title("🎨 MESTNA POEZIJA")

col1, col2 = st.columns(2)
with col1:
    mesto_vnos = st.text_input("Mesto", "Piran")
    drzava_vnos = st.text_input("Država", "Slovenija")
with col2:
    zoom_vnos = st.number_input("Mera zooma (metri)", 500, 10000, 2500, 500) # Omejen max zoom
    tema_vnos = st.selectbox("Izberi slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ MOJSTROVINO"):
    rezultat = ustvari_poster_cached(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
    
    if isinstance(rezultat, bytes):
        st.image(rezultat, use_container_width=True)
        st.download_button("📥 PRENESI A4 POSTER", rezultat, file_name=f"{mesto_vnos}.png")
    else:
        st.error(f"Napaka: {rezultat}")

# ... (tvoj PayPal del ostane isti)