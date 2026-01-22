import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Prazno ozadje, voda je ločen element)
THEMES = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "water": "#a5c3cf", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "water": "#00ffff", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#e3f2fd", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_v3_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° {'N' if loc.latitude >= 0 else 'S'} / {abs(loc.longitude):.4f}° {'E' if loc.longitude >= 0 else 'W'}"
        return "KOORDINATE NISO NAJDENE"
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # Pridobivanje podatkov
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # BOLJŠI FILTER ZA VODO (Vključuje morje in obale)
    try:
        voda = ox.features_from_address(kraj, tags={
            "natural": ["water", "coastline", "beach"], 
            "place": ["sea", "ocean"],
            "waterway": True,
            "bay": True
        }, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # Najprej narišemo vodo
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Nato ceste
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.8, show=False, close=False)
    
    ax.axis('off')
    
    # FIKSEN BEL PAS SPODAJ
    plt.subplots_adjust(bottom=0.25)
    
    # NAPISI (Z ročno nastavljenimi višinami, da ne uidejo)
    fig.text(0.5, 0.15, mesto.upper(), fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.10, drzava.upper(), fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.06, koordinate, fontsize=16, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- VMESNIK ---
st.title("🎨 Končni Generator Posterjev")
mesto = st.text_input("Mesto", "Piran")
drzava = st.text_input("Država", "Slovenia")
razdalja = st.slider("Povečava (Zoom)", 1000, 10000, 5000) # Večji zoom pomaga najti morje
izbrana_tema = st.selectbox("Stil", list(THEMES.keys()))

if st.button("🚀 Ustvari čist poster"):
    with st.spinner("Popravljam morje in koordinate..."):
        try:
            img = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(img, use_container_width=True)
            st.download_button("Prenesi PNG", img, file_name=f"{mesto}.png")
        except Exception as e:
            st.error(f"Napaka: {e}")