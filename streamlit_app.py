import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Nazaj na preverjeno estetiko)
THEMES = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#b3e5fc", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_clean_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° N / {abs(loc.longitude):.4f}° E"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # Pridobivanje podatkov o cestah
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # Pridobivanje VODE (razširjen filter, ki je prej deloval)
    try:
        voda = ox.features_from_address(kraj, tags={"natural": ["water", "coastline", "bay"], "water": True}, dist=razdalja)
    except:
        voda = None

    # Visoka figura (kot originalna poezija)
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # Najprej narišemo vodo
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Nato ceste
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.7, show=False, close=False)
    
    ax.axis('off')
    
    # Prostor za napise (brez čudnih pravokotnikov)
    plt.subplots_adjust(bottom=0.25)
    
    # VELIKI, ČISTI NAPISI (Nazaj na piran_sea_view_1.png stil)
    fig.text(0.5, 0.15, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.06, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- VMESNIK ---
st.set_page_config(page_title="Premium City Poster", layout="centered")
st.title("🎨 Premium City Poster Generator")

mesto = st.text_input("Vnesi mesto", "Piran")
drzava = st.text_input("Vnesi državo", "Slovenia")
razdalja = st.slider("Zoom (razdalja v metrih)", 1000, 10000, 3500)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Generiraj Poster"):
    with st.spinner("Ustvarjam poezijo..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster", data=slika_buf, file_name=f"{mesto}.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- TVOJ ORIGINALNI PAYPAL GUMB ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 18px;">Ti je generator prihranil denar? Časti me s kavo! ☕</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 14px 28px; border-radius: 30px; font-weight: bold; display: inline-block; font-family: Arial;">
                Donate (PayPal)
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)