import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

# 1. To mora biti prva vrstica, da Streamlit ne javlja napake
st.set_page_config(page_title="Mestna Poezija", layout="centered")

# 2. TVOJI STILI (Dodani tistim originalnim)
THEMES = {
    "Minimalističen": {"bg": "#ffffff", "edge": "#222222"},
    "Neon noč": {"bg": "#000000", "edge": "#00f2ff"},
    "Gozdna tišina": {"bg": "#f0f4f0", "edge": "#2d5a27"},
    "Cyberpunk": {"bg": "#1a1a2e", "edge": "#e94560"},
    "Zlati sij": {"bg": "#121212", "edge": "#d4af37"},
    "Skandinavski": {"bg": "#faf9f6", "edge": "#4a4e69"},
    "Morski razgled": {"bg": "#e0f2f1", "edge": "#00695c"}
}

# 3. DODATEK: Caching (Da preprečimo "bel zaslon" ob navalu)
@st.cache_data(show_spinner="Pripravljam podatke iz arhiva...")
def dobi_podatke(mesto):
    try:
        # network_type='all' je tisto, kar si imel prej (vse poti)
        return ox.graph_from_place(mesto, network_type="all")
    except:
        return None

# 4. GLAVNI DEL (Kot prej, le lepše zapakirano)
st.title("🎨 Mestna Poezija")
st.write("Vpiši svoje mesto in ustvari brezplačen poster.")

mesto = st.text_input("Ime mesta (npr. Maribor, Slovenia)", "Ljubljana")
izbran_stil = st.selectbox("Izberi barvno shemo:", list(THEMES.keys()))

if st.button("Zgeneriraj"):
    with st.spinner("Ustvarjam umetnino..."):
        G = dobi_podatke(mesto)
        
        if G:
            stil = THEMES[izbran_stil]
            # Tvoja originalna plot funkcija
            fig, ax = ox.plot_graph(
                G, 
                bgcolor=stil["bg"], 
                edge_color=stil["edge"], 
                edge_linewidth=0.5, 
                node_size=0, 
                show=False, 
                close=True
            )
            
            # Prikaz slike
            st.pyplot(fig)
            st.success("Tukaj je tvoj poster! Desni klik na sliko za shranjevanje.")
        else:
            st.error("Mesta ni bilo mogoče najti. Poskusi dodati državo.")

# 5. DODATEK: Donacije (Gorenjska kava)
st.sidebar.markdown("---")
st.sidebar.subheader("Ti je projekt všeč? ☕")
st.sidebar.write("Več kot 400 ljudi je danes že ustvarilo svoj poster!")
st.sidebar.markdown("[Časti kavo (5 €) prek PayPala](https://paypal.me/tvoj_link)")