import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. TEME (Natančne barve za Piran in reke)
THEMES = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "roads": "#757575", "water": "#0077BE", "text": "#063951"},
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "water": "#3d424d", "text": "white"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "water": "#b3e5fc", "text": "#2c3e50"}
}

def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_final_v6")
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
    
    # Pridobivanje vode (Morje + Reke)
    try:
        voda = ox.features_from_address(kraj, tags={"natural": "water", "waterway": True, "place": "sea"}, dist=razdalja)
    except:
        voda = None

    fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
    ax.set_facecolor(barve["bg"])
    
    # Risanje vode (slana in sladka)
    if voda is not None and not voda.empty:
        voda.plot(ax=ax, color=barve["water"], zorder=1)
    
    # Risanje cest
    ox.plot_graph(graf, ax=ax, node_size=0, edge_color=barve["roads"], edge_linewidth=0.8, show=False, close=False)
    
    ax.axis('off')
    plt.subplots_adjust(bottom=0.2)
    
    # Dodajanje belega pasu spodaj za napise
    rect = plt.Rectangle((0, 0), 1, 0.22, transform=fig.transFigure, facecolor=barve["bg"], zorder=0)
    fig.patches.append(rect)
    
    # NAPISI (Slovenski, veliki in centrirani)
    fig.text(0.5, 0.14, mesto.upper(), fontsize=55, color=barve["text"], ha="center", fontweight="bold")
    fig.text(0.5, 0.09, drzava.upper(), fontsize=22, color=barve["text"], ha="center", alpha=0.8)
    
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.05, koordinate, fontsize=16, color=barve["text"], ha="center", alpha=0.6, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight', pad_inches=0.5)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- STREAMLIT VMESNIK ---
st.set_page_config(page_title="Premium City Poster", layout="centered")
st.title("🎨 Generator mestnih posterjev")

mesto = st.text_input("Vnesi ime mesta", "Piran")
drzava = st.text_input("Vnesi državo", "Slovenija")
razdalja = st.slider("Zoom (v metrih)", 1000, 8000, 3000)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari poster"):
    with st.spinner("Pripravljam tvoj unikatni zemljevid..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            # SLOVENSKI GUMB ZA PRENOS
            st.download_button(label="📥 Prenesi poster (PNG)", data=slika_buf, file_name=f"{mesto}.png", mime="image/png")
        except Exception as e:
            st.error(f"Napaka: {e}")

# --- TVOJ ORIGINALNI DONACIJSKI GUMB ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="font-size: 16px;">Ti je generator všeč? Podpri razvoj!</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block; font-family: Arial;">
                Donate
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)