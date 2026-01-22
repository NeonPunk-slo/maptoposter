import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Z ločenimi barvami za morje in kopno)
THEMES = {
    "Morski razgled (Moder)": {"sea": "#0077BE", "land": "#F1F4F7", "roads": "#757575", "text": "#063951"},
    "Klasičen temen": {"sea": "#1a1a1b", "land": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Minimalističen bel": {"sea": "#e3f2fd", "land": "#ffffff", "roads": "#2c3e50", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_2026_v7")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° N / {abs(loc.longitude):.4f}° E"
        return ""
    except:
        return ""

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = THEMES[ime_teme]
    
    # 1. Pridobivanje cest
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    
    # 2. Pridobivanje kopna (uporabimo meje mesta, da vemo, kje je zemlja)
    try:
        # Iščemo administrativno območje, ki nam služi kot maska za kopno
        kopno = ox.features_from_address(kraj, tags={"boundary": "administrative", "admin_level": ["8", "9"]}, dist=razdalja)
    except:
        kopno = None

    # Ustvarjanje figure - CELOTNO OZADJE JE MODRO MORJE
    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["sea"])
    ax.set_facecolor(barve["sea"])
    
    # Najprej narišemo kopno (belo/sivo) čez modro morje
    if kopno is not None and not kopno.empty:
        kopno.plot(ax=ax, color=barve["land"], zorder=1)
    
    # Nato narišemo ceste
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.8, show=False, close=False)
    
    ax.axis('off')
    
    # BELI PAS SPODAJ (Fiksen prostor za napise)
    plt.subplots_adjust(bottom=0.22)
    rect = plt.Rectangle((0, 0), 1, 0.22, transform=fig.transFigure, facecolor="#F1F4F7", zorder=10)
    fig.patches.append(rect)
    
    # NAPISI IN KOORDINATE
    fig.text(0.5, 0.14, mesto.upper(), fontsize=55, color=barve["text"], ha="center", fontweight="bold", zorder=11)
    fig.text(0.5, 0.09, drzava.upper(), fontsize=22, color=barve["text"], ha="center", alpha=0.8, zorder=11)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.05, koordinate, fontsize=16, color=barve["text"], ha="center", alpha=0.6, family="monospace", zorder=11)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["sea"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT ---
st.set_page_config(page_title="Premium City Poster", layout="centered")
st.title("🎨 Generator mestnih posterjev")

mesto = st.text_input("Vnesi ime mesta", "Piran")
drzava = st.text_input("Vnesi državo", "Slovenija")
razdalja = st.slider("Zoom (v metrih)", 1000, 8000, 4000)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari poster"):
    with st.spinner("Generiram morje in kopno..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- PAYPAL GUMB ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p>Ti je generator všeč? Podpri razvoj! ☕</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block; font-family: Arial;">
                Donate
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)