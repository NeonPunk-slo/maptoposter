import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Z osveženimi barvnimi paletami za ceste)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#2C3E50", "glavne": "#5D6D7E", "ostalo": "#ABB2B9"},
    "Klasičen temen": {"bg": "#202124", "water": "#3d424d", "text": "white", "ac": "#FFFFFF", "glavne": "#D5D8DC", "ostalo": "#7F8C8D"},
    "Starinski papir": {"bg": "#f4f1ea", "water": "#a5c3cf", "text": "#333333", "ac": "#1A1A1A", "glavne": "#4D4D4D", "ostalo": "#808080"},
    "Neon Punk": {"bg": "#000000", "water": "#2d2d2d", "text": "#00ffff", "ac": "#ff00ff", "glavne": "#ff77ff", "ostalo": "#444444"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#2c3e50", "ac": "#000000", "glavne": "#555555", "ostalo": "#AAAAAA"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_premium_color_v1")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "45.5283° S / 13.5677° V"
    except:
        return "45.5283° S / 13.5677° V"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # LOGIKA ZA BARVE IN DEBELINE CEST
    road_colors = []
    road_widths = []
    
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        
        if h_type in ["motorway", "trunk"]:
            road_colors.append(barve["ac"])    # Barva za avtoceste
            road_widths.append(3.0)
        elif h_type in ["primary", "secondary"]:
            road_colors.append(barve["glavne"]) # Barva za glavne ceste
            road_widths.append(1.8)
        elif h_type in ["tertiary", "residential"]:
            road_colors.append(barve["ostalo"]) # Barva za občinske ceste
            road_widths.append(0.8)
        else:
            road_colors.append(barve["ostalo"]) # Ostale poti
            road_widths.append(0.4)

    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Uporaba različnih barv (edge_color=road_colors)
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
    
    ax.axis('off')
    plt.subplots_adjust(bottom=0.25)
    
    fig.text(0.5, 0.16, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.11, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.07, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.3)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- SLOVENSKI VMESNIK ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.markdown("<h1 style='text-align: center;'>Mestna Poezija</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Premium zemljevidi s pravilno hierarhijo cest</p>", unsafe_allow_html=True)

mesto = st.text_input("Ime kraja", "Piran")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Povečava - Zoom (v metrih)", min_value=500, max_value=25000, value=3500, step=100)
izbrana_tema = st.selectbox("Izberi umetniški slog", list(TEME.keys()))

if st.button("✨ Ustvari umetniško delo"):
    with st.spinner("Rišem ceste in določam barve..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}_poezija.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- PAYPAL ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 16px; color: #888;">Ti je rezultat všeč? Podpri razvoj aplikacije.</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block;">
                PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)