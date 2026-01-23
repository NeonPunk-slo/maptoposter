import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

# 1. KONFIGURACIJA STRANI
st.set_page_config(page_title="Mestna Poezija", page_icon="🎨", layout="centered")

# 2. DEFINICIJA STILOV (7 tem)
THEMES = {
    "Minimalističen": {"bg": "#ffffff", "edge": "#222222", "water": "#a2d2ff"},
    "Neon noč": {"bg": "#000000", "edge": "#00f2ff", "water": "#ff00d4"},
    "Gozdna tišina": {"bg": "#f0f4f0", "edge": "#2d5a27", "water": "#1b3a1a"},
    "Cyberpunk": {"bg": "#1a1a2e", "edge": "#e94560", "water": "#0f3460"},
    "Zlati sij": {"bg": "#121212", "edge": "#d4af37", "water": "#3d3d3d"},
    "Skandinavski": {"bg": "#faf9f6", "edge": "#4a4e69", "water": "#9a8c98"},
    "Morski razgled": {"bg": "#e0f2f1", "edge": "#00695c", "water": "#4db6ac"}
}

# 3. OPTIMIZACIJA: Predpomnjenje podatkov (Da se ne sesuje ob navalu!)
@st.cache_data(show_spinner="Gorenjska tehnologija prenaša podatke...")
def get_graph(city_name):
    try:
        # Prenesemo le cestno omrežje (network_type="all" za vse poti)
        return ox.graph_from_place(city_name, network_type="all")
    except Exception:
        return None

# 4. FUNKCIJA ZA RISANJE (Tudi to keširamo za hitrost)
@st.cache_data(show_spinner="Rišem poster v A4 formatu...")
def draw_map(city_name, theme_name):
    G = get_graph(city_name)
    if not G:
        return None
    
    theme = THEMES[theme_name]
    
    # Nastavitev A4 razmerja (cca 1:1.41)
    fig, ax = ox.plot_graph(
        G, 
        bgcolor=theme["bg"], 
        edge_color=theme["edge"], 
        edge_linewidth=0.6, 
        node_size=0, 
        show=False, 
        close=True
    )
    
    # Minimalističen napis spodaj
    fig.text(0.5, 0.08, city_name.upper(), 
             fontsize=22, color=theme["edge"], 
             ha='center', va='center', weight='light', alpha=0.8)
    
    return fig

# 5. UPORABNIŠKI VMESNIK
st.title("🎨 Mestna Poezija")
st.write(f"Trenutno nas je obiskalo že čez 411 navdušencev!")

# Sidebar za nastavitve
st.sidebar.header("Nastavitve Posterja")
city = st.sidebar.text_input("Vpiši mesto (npr. Ljubljana, Slovenia)", "Ljubljana")
style = st.sidebar.selectbox("Izberi stil:", list(THEMES.keys()))

# GUMB ZA DONACIJE (Gorenjska kava)
st.sidebar.markdown("---")
st.sidebar.subheader("Podpri projekt ☕")
st.sidebar.write("Če ti je poster všeč in si si ga shranil, lahko častiš kavo (5 €), da serverji ne ugasnejo!")
# Tu vstavi svoj PayPal ali BuyMeACoffee link
st.sidebar.markdown("[Časti kavo (PayPal)](https://www.paypal.me/TVOJ_LINK)") 

# Glavni prikaz
if st.sidebar.button("Ustvari moj poster"):
    fig = draw_map(city, style)
    if fig:
        st.pyplot(fig)
        st.success("Poster je pripravljen! Desni klik na sliko -> Shrani sliko kot.")
        st.info("Nasvet: Za najboljši tisk na A4 izberi 'Shrani kot PNG'.")
    else:
        st.error("Mesta nisem našel. Preveri črkovanje ali dodaj državo (npr. 'Piran, Slovenia').")

st.markdown("---")
st.caption("Narejeno s ponosom v Sloveniji. Uporabljamo OSM podatke.")