import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. DEFINICIJA VSEH 5 TEM (Z dodano barvo za vodo)
THEMES = {
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#2c2e33", "text": "white"},
    "Morski razgled (Moder)": {"bg": "#001f3f", "roads": "#7FDBFF", "water": "#003366", "text": "#7FDBFF"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "water": "#c0d6de", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "water": "#1a0033", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#e3f2fd", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_pro_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° {'S' if loc.latitude >= 0 else 'J'} / {abs(loc.longitude):.4f}° {'V' if loc.longitude >= 0 else 'Z'}"
        return "KOORDINAT NI MOGOČE NAJTI"
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # 1. Pridobivanje cest
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # 2. Pridobivanje vodnih površin (ocean, reke, jezera)
    try:
        voda = ox.features_from_address(kraj, tags={"natural": "water", "waterway": True}, dist=razdalja)
    except:
        voda = None

    # Risanje
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # Najprej narišemo vodo, če obstaja
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Nato narišemo ceste
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.8, show=False, close=False)
    
    plt.subplots_adjust(bottom=0.28)
    
    # Napisi
    fig.text(0.5, 0.16, mesto.upper(), fontsize=32, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.11, drzava.upper(), fontsize=14, color=barve["text"], ha="center", alpha=0.6)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.07, koordinate, fontsize=10, color=barve["text"], ha="center", alpha=0.5, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# --- Streamlit vmesnik ostane enak ---
st.set_page_config(page_title="Premium Posterji Mest", page_icon="🎨")
st.title("🎨 Premium Generator Mestnih Posterjev")

mesto = st.text_input("Vnesi ime mesta", "Novo mesto")
drzava = st.text_input("Vnesi državo", "Slovenija")
razdalja = st.slider("Povečava (metri)", 500, 5000, 2500)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari svoj poster"):
    with st.spinner("Pridobivam podatke (tudi vodo)..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster", data=slika_buf, file_name=f"{mesto}.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# PayPal
st.write("---")
paypal_povezava = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''<div style="text-align: center;"><a href="{paypal_povezava}" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif"></a></div>''', unsafe_allow_html=True)