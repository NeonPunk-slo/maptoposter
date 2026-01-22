import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from shapely.geometry import box

# 1. TEME (Prilagojene za trik z morjem)
THEMES = {
    "Morski razgled (Moder)": {"sea": "#0077BE", "land": "#F1F4F7", "roads": "#757575", "text": "#063951"},
    "Klasičen temen": {"sea": "#121212", "land": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Starinski papir": {"sea": "#c0d6de", "land": "#f4f1ea", "roads": "#5b5b5b", "text": "#333333"},
    "Neon Punk": {"sea": "#1a0033", "land": "#000000", "roads": "#ff00ff", "text": "#00ffff"},
    "Minimalističen bel": {"sea": "#e3f2fd", "land": "#ffffff", "roads": "#2c3e50", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_final_v3")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° {'N' if loc.latitude >= 0 else 'S'} / {abs(loc.longitude):.4f}° {'E' if loc.longitude >= 0 else 'W'}"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # Pridobivanje podatkov
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # Pridobivanje kopnega (da lahko pobarvava morje v ozadju)
    try:
        kopno = ox.features_from_address(kraj, tags={"boundary": "administrative", "landuse": True}, dist=razdalja)
    except:
        kopno = None

    # Ustvarjanje figure - OZADJE JE BARVA MORJA
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["sea"])
    ax.set_facecolor(barve["sea"])
    
    # Narišemo bel/siv pravokotnik za kopno (če ga OSM ne najde, uporabimo graf)
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.7, show=False, close=False)
    
    # Nastavitev belega pasu spodaj
    plt.subplots_adjust(bottom=0.25)
    
    # DODAJANJE BELEGA OKVIRJA SPODAJ ZA NAPISE
    rect = plt.Rectangle((0, -0.3), 1, 0.3, transform=fig.transFigure, color=barve["land"], zorder=-1)
    fig.patches.append(rect)
    
    # NAPISI (Fiksne pozicije)
    fig.text(0.5, 0.14, mesto.upper(), fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.09, drzava.upper(), fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.05, koordinate, fontsize=16, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["sea"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT ---
st.set_page_config(page_title="Premium City Poster", layout="centered")
st.title("🎨 Premium Generator Mestnih Posterjev")

mesto = st.text_input("Ime mesta", "Piran")
drzava = st.text_input("Država", "Slovenia")
razdalja = st.slider("Povečava (metri)", 500, 10000, 4000)
izbrana_tema = st.selectbox("Izberi stil", list(THEMES.keys()))

if st.button("🚀 Generiraj končno verzijo"):
    with st.spinner("Ustvarjam poster z morjem in koordinatami..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster", data=slika_buf, file_name=f"{mesto}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# PayPal
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''<div style="text-align:center"><a href="{paypal_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#ffc439;color:black;padding:12px 24px;border-radius:30px;font-weight:bold;display:inline-block;">Podpri projekt (PayPal)</div></a></div>''', unsafe_allow_html=True)