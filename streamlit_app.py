import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. NASTAVITVE STRANI
st.set_page_config(page_title="MESTNA POEZIJA", page_icon="🎨", layout="centered")

# 2. TVOJE PERFEKCIONISTIČNE TEME
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#A5D1E8", "text": "#063951", "ac": "#E67E22", "glavne": "#063951"},
    "Gozdna tišina (Zelen)": {"bg": "#F9FBF7", "water": "#DDEBDB", "text": "#2D4221", "ac": "#8B4513", "glavne": "#4B633D"},
    "Skandinavski minimal": {"bg": "#FFFFFF", "water": "#E5E5E5", "text": "#222222", "ac": "#000000", "glavne": "#666666"},
    "Cyberpunk Original": {"bg": "#050B16", "water": "#0D1B2A", "text": "#FFD700", "ac": "#FF00FF", "glavne": "#FFD700"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#0F161E", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF"},
    "Polnočni neon": {"bg": "#000000", "water": "#111111", "text": "#00FF41", "ac": "#00FF41", "glavne": "#FFFFFF"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F"}
}

# 3. CACHING - Da aplikacija ne crkne ob navalu (shrani zadnjih 20 iskanj)
@st.cache_data(show_spinner="Ustvarjam vaš A4 poster (PNG + SVG)...", max_entries=20)
def ustvari_poster_final(mesto, drzava, razdalja, ime_teme):
    try:
        # Pridobivanje koordinat
        lat, lon = ox.geocode(f"{mesto}, {drzava}")
        barve = TEME[ime_teme]
        ox.settings.timeout = 300
        
        # Omejitev območja
        north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)

        # Pridobivanje cest (network_type="all" za detajle)
        G = ox.graph_from_point((lat, lon), dist=razdalja, network_type="all", simplify=True, retain_all=True)
        
        # Pridobivanje vode
        try:
            water = ox.features_from_bbox(north, south, east, west, tags={
                'natural': ['water', 'bay', 'strait'], 
                'waterway': ['riverbank', 'dock', 'canal'],
                'place': 'sea'
            })
        except:
            water = None

        # Barve in debeline cest
        road_colors, road_widths = [], []
        for u, v, k, data in G.edges(data=True, keys=True):
            h_type = data.get("highway", "unclassified")
            if isinstance(h_type, list): h_type = h_type[0]
            if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
                road_colors.append(barve["ac"]); road_widths.append(3.5)
            else:
                road_colors.append(barve["glavne"]); road_widths.append(0.7)

        # Izris A4 formata
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
        
        # Napisi: Ime, Država in Koordinate
        fig.text(0.5, 0.11, mesto.upper(), fontsize=32, color=barve["text"], ha="center", fontweight='bold')
        fig.text(0.5, 0.08, drzava.upper(), fontsize=14, color=barve["text"], ha="center", alpha=0.7)
        
        koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
        fig.text(0.5, 0.05, koord_tekst, fontsize=9, color=barve["text"], ha="center", family="monospace", alpha=0.5)

        # Shranjevanje v PNG buffer (za predogled)
        buf_png = io.BytesIO()
        fig.savefig(buf_png, format="png", facecolor=barve["bg"], dpi=200, bbox_inches='tight', pad_inches=0.4)
        buf_png.seek(0)

        # Shranjevanje v SVG buffer (za vektorski prenos)
        buf_svg = io.BytesIO()
        fig.savefig(buf_svg, format="svg", bbox_inches='tight', pad_inches=0.4)
        buf_svg.seek(0)

        plt.close(fig) # Sprostitev RAM-a
        return buf_png.getvalue(), buf_svg.getvalue()
    except Exception as e:
        return str(e), None

# --- UI (Streamlit) ---
st.title("🎨 MESTNA POEZIJA")
st.write("Ustvari vektorski poster svojega mesta. Primerno za tisk na A4.")

col1, col2 = st.columns(2)
with col1:
    mesto_vnos = st.text_input("Mesto", "Piran")
    drzava_vnos = st.text_input("Država", "Slovenija")
with col2:
    zoom_vnos = st.number_input("Zoom (metri)", 500, 15000, 2500, 100)
    tema_vnos = st.selectbox("Slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ MOJSTROVINO"):
    png_data, svg_data = ustvari_poster_final(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
    
    if svg_data:
        st.image(png_data, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 PRENESI PNG", png_data, file_name=f"{mesto_vnos}.png")
        with c2:
            st.download_button("🚀 PRENESI VEKTORSKI (SVG)", svg_data, file_name=f"{mesto_vnos}.svg")
    else:
        st.error(f"Napaka: {png_data}")

# --- PAYPAL DONACIJA ---
st.write("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px;">
        <h4 style="color: #555;">Ti je projekt všeč? ☕</h4>
        <p style="color: #777; font-size: 0.9em;">Več kot 400 ljudi je danes že ustvarilo svoj poster. Podpri projekt z majhno donacijo.</p>
        <a href="https://www.paypal.me/NeonPunkSlo" target="_blank" style="text-decoration: none;">
            <div style="background-color: #0070ba; color: white; padding: 12px 25px; border-radius: 50px; display: inline-block; font-weight: bold; font-family: sans-serif;">
                💛 Doniraj prek PayPal
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)