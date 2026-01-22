import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Pravilne barve za AC, vodo in napise)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#8B4513", "glavne": "#2F4F4F", "ostalo": "#A9A9A9"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00FFFF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_koncna_verzija")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "46.0569° S / 14.5058° V"
    except:
        return "46.0569° S / 14.5058° V"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Pridobivanje podatkov
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True, "waterway": "river"}, dist=razdalja)
    except:
        voda = None

    # Hierarhija cest (Barva in debelina)
    road_colors, road_widths = [], []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if h_type in ["motorway", "trunk", "motorway_link"]:
            road_colors.append(barve["ac"]); road_widths.append(4.0)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]); road_widths.append(2.0)
        else:
            road_colors.append(barve["ostalo"]); road_widths.append(0.6)

    # Izris posterja
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    ax.axis('off')
    
    # Razporeditev elementov na sliki
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.22)
    
    # Fiksni napisi (Mesto, Država, Koordinate)
    fig.text(0.5, 0.14, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koordinata_str = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.06, koordinata_str, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    # Shranjevanje celotne slike brez rezanja (fiksira koordinate)
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- SLOVENSKI VMESNIK ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎨 Mestna Poezija</h1>", unsafe_allow_html=True)

with st.container():
    mesto = st.text_input("Ime kraja", "Ljubljana")
    drzava = st.text_input("Država", "Slovenija")
    razdalja = st.number_input("Zoom (v metrih)", min_value=500, max_value=30000, value=5000)
    izbrana_tema = st.selectbox("Umetniški slog", list(TEME.keys()))

if st.button("✨ Ustvari poster"):
    with st.spinner("Ustvarjam umetniško delo s koordinatami in morjem..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}_poezija.png")
        except Exception as e:
            st.error(f"Prišlo je do napake: {e}")

# --- GUMB ZA DONACIJE ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center; padding: 20px;">
        <p style="font-size: 16px; color: #888; margin-bottom: 15px;">Ti je aplikacija všeč? Podpri razvoj "Mestne Poezije" s kavo!</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 14px 28px; border-radius: 30px; font-weight: bold; display: inline-block; font-family: Arial, sans-serif; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
                💛 PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)