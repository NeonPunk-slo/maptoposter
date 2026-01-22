import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Vse nazaj na svojem mestu)
THEMES = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "water": "#a5c3cf", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "water": "#2d2d2d", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#b3e5fc", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_v2026_final")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° N / {abs(loc.longitude):.4f}° E"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # Pridobivanje cest
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # Pridobivanje vode
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.7, show=False, close=False)
    
    ax.axis('off')
    plt.subplots_adjust(bottom=0.25)
    
    # Napisi v izbranem stilu
    fig.text(0.5, 0.15, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.06, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT ---
st.set_page_config(page_title="Premium City Poster Generator", layout="centered")
st.title("🎨 Premium City Poster Generator")

mesto = st.text_input("Vnesi ime mesta", "Piran")
drzava = st.text_input("Vnesi državo", "Slovenia")
razdalja = st.slider("Povečava (Zoom v metrih)", 1000, 10000, 3500)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari svoj poster"):
    with st.spinner("Pripravljam poezijo..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster", data=slika_buf, file_name=f"{mesto}.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka pri generiranju: {e}")

# --- PAYPAL GUMB ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 18px;">Časti me s kavo, če ti je poster všeč! ☕</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 14px 28px; border-radius: 30px; font-weight: bold; display: inline-block; font-family: Arial;">
                Donate (PayPal)
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)