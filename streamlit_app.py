import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME
THEMES = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "water": "#a5c3cf", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "water": "#2d2d2d", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#b3e5fc", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_premium_v4")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            lat_dir = "N" if loc.latitude >= 0 else "S"
            lon_dir = "E" if loc.longitude >= 0 else "W"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
        return "45.5283° N / 13.5677° E"
    except:
        return "45.5283° N / 13.5677° E"

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # Pridobivanje podatkov o cestah
    G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # LOGIKA ZA DEBELINO CEST (Hierarhija)
    # Avtoceste (motorway) bodo najdebelejše, pešpoti najtanjše
    widths = []
    for u, v, k, data in G.edges(data=True, keys=True):
        h_type = data.get("highway", "unclassified")
        if h_type in ["motorway", "trunk"]:
            widths.append(2.5) # Avtoceste in hitre ceste
        elif h_type in ["primary", "secondary"]:
            widths.append(1.5) # Glavne državne ceste
        elif h_type in ["tertiary", "residential"]:
            widths.append(0.8) # Občinske in stanovanjske ceste
        else:
            widths.append(0.3) # Poti, kolesarske steze, ostalo

    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Izris cest z uporabo naših širin (linewidth=widths)
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=widths, show=False, close=False)
    
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

# --- VMESNIK ---
st.set_page_config(page_title="Premium City Poster Generator", layout="centered")
st.title("🎨 Premium City Poster Generator")

mesto = st.text_input("Vnesi ime mesta", "Piran")
drzava = st.text_input("Vnesi državo", "Slovenia")
razdalja = st.number_input("Vnesi mero zooma (v metrih)", min_value=500, max_value=25000, value=3500, step=100)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari premium poster"):
    with st.spinner("Rišem ceste po pomembnosti..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}_premium.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- PAYPAL ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 18px;">Podpri razvoj s kavo! ☕</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 14px 28px; border-radius: 30px; font-weight: bold; display: inline-block;">
                Donate via PayPal
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)