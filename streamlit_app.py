import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box

def ustvari_piran_poster(lokacija="Piran, Slovenia", izvoz_pot="piran_z_vodo.png"):
    # 1. Nastavitve stila (temno modra kot na tvoji sliki)
    barva_vode = "#d1e3f0"  # Svetlo modra za morje
    barva_cest = "#1a3a4c"  # Temno modra za ceste in tekst
    barva_ozadja = "#fdfdfd" # Skoraj bela za kopno
    
    print(f"Pridobivam podatke za {lokacija}...")
    
    # 2. Pridobivanje cestnega omrežja
    # Razširimo razdaljo (dist), da zajamemo celoten zaliv
    graph = ox.graph_from_address(lokacija, dist=2500, network_type='all')
    nodes, edges = ox.graph_to_gdfs(graph)
    
    # 3. Pridobivanje vodnih površin (morja)
    # Uporabimo širše območje, da zapolnimo ozadje
    bbox = box(*edges.total_bounds).buffer(0.02) # Ustvarimo okvir okoli mesta
    water = ox.features_from_bbox(bbox.bounds[1], bbox.bounds[3], bbox.bounds[0], bbox.bounds[2], tags={'natural': 'water'})
    
    # 4. Kreiranje vizualizacijeimport streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from shapely.geometry import box

# 1. PERFEKCIONISTIČNE TEME (Dodana specifična barva za vodo za vsak stil)
TEME = {
    "Cyberpunk Original": {
        "bg": "#050B16", "water": "#0D1B2A", "text": "#FFD700", 
        "ac": "#FF00FF", "glavne": "#FFD700", "ostalo": "#FFD700"
    },
    "Morski razgled (Moder)": {
        "bg": "#F1F4F7", "water": "#A5D1E8", "text": "#063951", 
        "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"
    },
    "Klasičen temen": {
        "bg": "#1A1A1B", "water": "#0F161E", "text": "#FFFFFF", 
        "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"
    },
    "Starinski papir": {
        "bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", 
        "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"
    }
}

# 2. FUNKCIJA ZA IZRIS Z VODO
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    # Poiščemo koordinate
    try:
        lat, lon = ox.geocode(f"{mesto}, {drzava}")
    except:
        raise ValueError(f"Mesta '{mesto}' ni bilo mogoče najti. Preveri črkovanje.")

    barve = TEME[ime_teme]
    ox.settings.timeout = 300
    
    # Pridobivanje meja (bbox)
    north, south, east, west = ox.utils_geo.bbox_from_point((lat, lon), dist=razdalja)

    # A. Pridobivanje cest
    G = ox.graph_from_point((lat, lon), dist=razdalja, network_type="all", simplify=True, retain_all=True)
    
    # B. Pridobivanje vode (Morje, reke, zalivi)
    try:
        # Iščemo naravne vodne površine in obale
        water = ox.features_from_bbox(north, south, east, west, tags={
            'natural': ['water', 'bay', 'strait'], 
            'waterway': 'riverbank',
            'place': 'sea'
        })
    except:
        water = None

    # Priprava cestnih barv in debelin
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if isinstance(h_type, list): h_type = h_type[0]
        
        if h_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            road_colors.append(barve["ac"])
            road_widths.append(4.0)
        else:
            road_colors.append(barve["glavne"])
            road_widths.append(0.8)

    # Ustvarjanje slike
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # 1. IZRIS VODE (Najnižji sloj - zorder=1)
    if water is not None and not water.empty:
        water.plot(ax=ax, color=barve["water"], edgecolor='none', zorder=1)
    
    # 2. IZRIS CEST (Srednji sloj - zorder=2)
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, 
                  edge_linewidth=road_widths, show=False, close=False, zorder=2)
    
    # Nastavitev pogleda na točen zoom
    ax.set_ylim(south, north)
    ax.set_xlim(west, east)
    ax.axis('off')
    
    # 3. BESEDILO (Spodnji del)
    plt.subplots_adjust(bottom=0.25)
    
    mesto_spaced = "  ".join(mesto.upper())
    drzava_spaced = "    ".join(drzava.upper())
    
    fig.text(0.5, 0.18, mesto_spaced, fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.13, drzava_spaced, fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    koord_tekst = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
    fig.text(0.5, 0.09, koord_tekst, fontsize=16, color=barve["text"], ha="center", family="monospace")

    # Shranjevanje v buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.3)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT UI ---
st.set_page_config(page_title="Mestna Poezija Premium", layout="wide")
st.title("🎨 MESTNA POEZIJA PRO")
st.write("Generiraj minimalističen zemljevid z vključenimi vodnimi površinami.")

col1, col2 = st.columns([1, 2])

with col1:
    mesto_vnos = st.text_input("Mesto", "Piran")
    drzava_vnos = st.text_input("Država", "Slovenija")
    zoom_vnos = st.slider("Zoom (metri od centra)", 500, 10000, 2500)
    tema_vnos = st.selectbox("Izberi slog", list(TEME.keys()))
    gumb = st.button("✨ GENERIRAJ POSTER")

with col2:
    if gumb:
        with st.spinner("Pridobivam geografske podatke in rišem morje..."):
            try:
                slika = ustvari_poster(mesto_vnos, drzava_vnos, zoom_vnos, tema_vnos)
                st.image(slika)
                st.download_button("📥 PRENESI VISOKO LOČLJIVOST (PNG)", slika, file_name=f"{mesto_vnos}_poster.png")
            except Exception as e:
                st.error(f"Napaka: {e}")

st.write("---")
st.caption("Podatki © OpenStreetMap prispevki. Izdelano za tvoj novi dom.")
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barva_ozadja)
    ax.set_facecolor(barva_ozadja)
    
    # Izris vode
    if not water.empty:
        water.plot(ax=ax, color=barva_vode, edgecolor='none', zorder=1)
    
    # Izris cest
    edges.plot(ax=ax, color=barva_cest, linewidth=0.8, alpha=0.9, zorder=2)
    
    # 5. Dodajanje besedila (PIRAN SLOVENIJA + Koordinate)
    plt.text(0.5, 0.12, 'P I R A N', transform=ax.transAxes, 
             fontsize=50, fontname='DejaVu Sans', fontweight='bold', 
             color=barva_cest, ha='center', va='center')
    
    plt.text(0.5, 0.08, 'S L O V E N I J A', transform=ax.transAxes, 
             fontsize=20, fontname='DejaVu Sans', color=barva_cest, 
             ha='center', va='center')
    
    plt.text(0.5, 0.04, '45.5285° N / 13.5684° E', transform=ax.transAxes, 
             fontsize=12, fontname='DejaVu Sans', color=barva_cest, 
             ha='center', va='center')
    
    # Odstranjevanje osi in robov
    ax.axis('off')
    plt.tight_layout()
    
    # Shrani sliko
    plt.savefig(izvoz_pot, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Plakat je shranjen kot: {izvoz_pot}")
    plt.show()

# Zaženi funkcijo
if __name__ == "__main__":
    ustvari_piran_poster()