import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Slovenskimi imeni in opisi)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "water": "#a5c3cf", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "water": "#2d2d2d", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#b3e5fc", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_premium_slo")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            # Format: 45.5285° S / 13.5684° V (Uporabimo S za Sever in V za Vzhod)
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "45.5283° S / 13.5677° V"
    except:
        return "45.5283° S / 13.5677° V"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    # Pridobivanje cest
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # Hierarhija cest (Debelina po pomembnosti)
    sirine = []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if h_type in ["motorway", "trunk"]:
            sirine.append(2.8) # Avtoceste
        elif h_type in ["primary", "secondary"]:
            sirine.append(1.6) # Glavne ceste
        elif h_type in ["tertiary", "residential"]:
            sirine.append(0.8) # Stanovanjske ulice
        else:
            sirine.append(0.3) # Poti

    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=sirine, show=False, close=False)
    
    ax.axis('off')
    plt.subplots_adjust(bottom=0.25)
    
    # Napisi (Ime mesta, država in koordinate)
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
st.markdown("<p style='text-align: center; color: #888;'>Ustvari svoj unikatni minimalistični zemljevid</p>", unsafe_allow_html=True)

st.write("")

# Polja za vnos v slovenščini
mesto = st.text_input("Ime kraja", "Piran")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Povečava - Zoom (v metrih)", min_value=500, max_value=25000, value=3500, step=100)
izbrana_tema = st.selectbox("Izberi umetniški slog", list(TEME.keys()))

if st.button("✨ Ustvari umetniško delo"):
    with st.spinner("Pripravljam tvoj poster... prosim počakaj."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}_poezija.png", mime="image/png")
        except Exception as e:
            st.error(f"Prišlo je do napake: {e}")

# --- PAYPAL ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 16px; color: #888;">Ti je rezultat všeč? Podpri razvoj aplikacije.</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block; font-family: Arial;">
                PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)