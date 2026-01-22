import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. DEFINICIJA VSEH 5 TEM
THEMES = {
    "Klasičen temen": {"bg": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Morski razgled (Moder)": {"bg": "#001f3f", "roads": "#7FDBFF", "text": "#7FDBFF"},
    "Starinski papir": {"bg": "#f4f1ea", "roads": "#5b5b5b", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "text": "#00ffff"},
    "Minimalističen bel": {"bg": "#ffffff", "roads": "#2c3e50", "text": "#2c3e50"}
}

# 2. FUNKCIJA ZA KOORDINATE
def dobi_koordinate(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="city_poster_pro_2026")
        loc = geolocator.geocode(f"{mesto}, {drzava}")
        if loc:
            return f"{abs(loc.latitude):.4f}° {'S' if loc.latitude >= 0 else 'J'} / {abs(loc.longitude):.4f}° {'V' if loc.longitude >= 0 else 'Z'}"
        return "KOORDINAT NI MOGOČE NAJTI"
    except:
        return ""

# 3. GENERIRANJE POSTERJA
def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    graf = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
    barve = THEMES[ime_teme]
    
    fig, ax = ox.plot_graph(
        graf, node_size=0, edge_color=barve["roads"], edge_linewidth=0.8,
        bgcolor=barve["bg"], show=False, close=False
    )
    
    plt.subplots_adjust(bottom=0.28)
    
    # Napis Mesta
    fig.text(0.5, 0.16, mesto.upper(), fontsize=32, color=barve["text"], 
             ha="center", fontweight="bold", family="sans-serif")
    
    # Napis Države
    fig.text(0.5, 0.11, drzava.upper(), fontsize=14, color=barve["text"], 
             ha="center", alpha=0.6, family="sans-serif")
    
    # KOORDINATE
    koordinate = dobi_koordinate(mesto, drzava)
    fig.text(0.5, 0.07, koordinate, fontsize=10, color=barve["text"], 
             ha="center", alpha=0.5, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# 4. STREAMLIT VMESNIK (V slovenščini)
st.set_page_config(page_title="Premium Posterji Mest", page_icon="🎨")
st.title("🎨 Premium Generator Mestnih Posterjev")
st.write("Ustvari svoj unikatni umetniški zemljevid s točnimi koordinatami.")

mesto = st.text_input("Vnesi ime mesta", "Novo mesto")
drzava = st.text_input("Vnesi državo", "Slovenija")
razdalja = st.slider("Povečava (razdalja v metrih od centra)", 500, 5000, 2500)
izbrana_tema = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Ustvari svoj poster"):
    with st.spinner(f"Pripravljam tvoj {izbrana_tema} poster..."):
        try:
            slika_buf = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
            st.image(slika_buf, use_container_width=True)
            
            st.download_button(
                label="📥 Prenesi poster v visoki ločljivosti",
                data=slika_buf,
                file_name=f"{mesto}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Prišlo je do napake: {e}. Poskusi povečati razdaljo ali preveri ime mesta.")

# 5. PAYPAL DONACIJE
st.write("---")
paypal_povezava = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 10px;">
        <p style="color: white; font-size: 18px;">Ti je generator prihranil 50 €? Časti me s kavo! ☕</p>
        <a href="{paypal_povezava}" target="_blank">
            <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Doniraj">
        </a>
    </div>
''', unsafe_allow_html=True)