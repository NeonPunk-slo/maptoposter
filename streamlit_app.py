import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Mestna Poezija", layout="wide")

# Črn stil strani
st.markdown("<style>.stApp {background-color: #000000; color: white;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Nastavitve")
    mesto = st.text_input("Kraj", "Ljubljana")
    razdalja = st.slider("Razdalja (metri)", 500, 5000, 1500)
    barva_cest = st.color_picker("Barva linij", "#00f2ff")
    st.write("---")
    st.markdown(f'<a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="width:100%; background-color:#ffc439; border-radius:10px; border:none; padding:10px; font-weight:bold;">💛 Podpri projekt</button></a>', unsafe_allow_html=True)

# Glavna funkcija za risanje (vektorska grafika)
def ustvari_poster(mesto, dist, color):
    try:
        # Pridobivanje grafov cest (to je tisto, kar je bilo "top")
        G = ox.graph_from_address(mesto, dist=dist, network_type="all", retain_all=True)
        
        fig, ax = plt.subplots(figsize=(10, 15), facecolor='black')
        ox.plot_graph(G, ax=ax, node_size=0, edge_color=color, edge_linewidth=0.8, show=False, close=False)
        
        # Estetski napisi
        plt.text(0.5, 0.05, mesto.upper(), transform=ax.transAxes, color=color, fontsize=40, ha='center', weight='bold', letterspacing=10)
        
        return fig
    except Exception as e:
        st.error(f"Napaka pri generiranju: {e}")
        return None

if st.button("🚀 GENERIRAJ VEKTORSKI POSTER"):
    with st.spinner("Rišem digitalne linije..."):
        fig = ustvari_poster(mesto, razdalja, barva_cest)
        if fig:
            st.pyplot(fig, clear_figure=True)