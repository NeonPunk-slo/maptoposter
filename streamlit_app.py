import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. PERFEKCIONISTIČNE TEME
TEME = {
    "Cyberpunk Original": {"bg": "#050B16", "water": "#0D1B2A", "text": "#FFD700", "ac": "#FF00FF", "glavne": "#FFD700"},
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#A5D1E8", "text": "#063951", "ac": "#E67E22", "glavne": "#063951"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#0F161E", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F"}
}

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    try:
        lat, lon = ox.geocode(f"{mesto}, {drzava}")
    except:
        raise ValueError(f"Mesta '{mesto}' ni bilo mogoče najti.")

    barve = TEME[ime_teme]
    ox.settings.timeout = 300
    
    # Pridobivanje meja (bbox)
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)

    # Pridobivanje podatkov o cestah
    G = ox.graph_from_point((lat, lon), dist=razdalja, network_type="all", simplify=True, retain_all=True)
    
    # Pridobivanje podatkov o vodi
    try:
        water = ox.features_from_bbox(north, south, east, west, tags={
            'natural': ['water', 'bay', 'strait'], 
            'waterway': ['riverbank', 'dock', 'canal'],
            'place': 'sea'
        })
    except:
        water = None

    # Barve cest
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"]); road_widths.append(3.5)
        else:
            road_colors.append(barve["glavne"]); road_widths.append(0.7)

    # --- A4 FORMAT (8.27 x 11.69 in) ---
    fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # 1. NAJPREJ VODA (osnova)
    if water is not None and not water.empty:
        water.plot(ax=ax, color=barve["water"], edgecolor='none')
    
    # 2. NATO CESTE (brez zorder argumenta, se narišejo čez)
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, 
                  edge_linewidth=road_widths, show=False, close=False)
    
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # --- POSODOBLJEN ELEGANTEN NAPIS ---
    plt.subplots_adjust(bottom=0.12)
    
    # Ime mesta (manjše in bolj skupaj)
    fig.text(0.5, 0.08, mesto.upper(), fontsize=28, color=barve["text"], 
             ha="center", fontweight='bold')
    
    # Država
    fig.text(0.5, 0.06, drzava.upper(), fontsize=12, color=barve["text"], 
             ha="center", alpha=0.7)
    
    # Koordinate (diskretne)
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.04, koord_tekst, fontsize=8, color=barve["text"], 
             ha="center", family="monospace", alpha=0.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.4)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT UI ---
st.set_page_config(page_title="Mestna Poezija Premium", page_icon="🎨")
st.title("🎨 MESTNA POEZIJA PRO")

mesto_vnos = st.text_input("Vnesi mesto", "Piran")
drzava_vnos = st.text_input("Država", "Slovenija")
zoom_vnos = st.slider("Zoom (metri)", 500, 10000, 2500)
tema_vnos = st.selectbox("Izberi slog", list(TEME.keys()))

if st.button("✨ GENERIRAJ MOJSTROVINO"):
    with st.spinner("Pripravljam vaš A4 poster..."):
        try:
            slika = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
            st.image(slika, use_container_width=True)
            st.download_button("📥 PRENESI A4 POSTER (PNG)", slika, file_name=f"{mesto_vnos}_A4.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- PAYPAL DONACIJA ---
st.write("---")
st.markdown(
    """
    <div style="text-align: center;">
        <p style="color: gray; font-size: 0.8em;">Ti je aplikacija všeč? Podpri razvoj.</p>
        <a href="https://www.paypal.me/NeonPunkSlo" target="_blank">
            <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" title="PayPal - Varno plačevanje" alt="Donate with PayPal button" />
        </a>
    </div>
    """,
    unsafe_allow_html=True
)