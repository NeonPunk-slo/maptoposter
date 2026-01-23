import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mestna Poezija", layout="wide")

# Skrijemo Streamlit menije za "Premium" občutek
st.markdown("<style>.stApp {background-color: #000000;} header {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 style='color: #00f2ff;'>NASTAVITVE</h1>", unsafe_allow_html=True)
    kraj = st.text_input("Vnesi kraj", "Ljubljana")
    razdalja = st.slider("Velikost območja (m)", 500, 3000, 1500)
    barva = st.color_picker("Barva cest", "#00f2ff")
    
    st.write("---")
    st.markdown(f'<a href="https://www.paypal.me/NeonPunkSlo" target="_blank"><button style="width:100%; background-color:#ffc439; border:none; padding:10px; border-radius:10px; font-weight:bold;">💛 Podpri projekt</button></a>', unsafe_allow_html=True)

# Funkcija za generiranje vektorske slike (Ljubljana_poezija stil)
def narisi_mapo(lokacija, dist, color):
    try:
        # Pridobivanje podatkov o cestah
        G = ox.graph_from_address(lokacija, dist=dist, network_type="all")
        
        fig, ax = plt.subplots(figsize=(12, 16), facecolor='black')
        ox.plot_graph(G, ax=ax, node_size=0, edge_color=color, edge_linewidth=0.7, show=False, close=False)
        
        # Spodnji napis v stilu tvoje slike
        plt.text(0.5, 0.08, lokacija.upper(), transform=ax.transAxes, color=color, 
                 fontsize=50, ha='center', fontweight='bold', letterspacing=8)
        plt.text(0.5, 0.04, "SLOVENIJA", transform=ax.transAxes, color=color, 
                 fontsize=20, ha='center', letterspacing=15)
        
        return fig
    except Exception as e:
        st.error(f"Strežnik je preobremenjen. Poskusi z manjšo razdaljo (m).")
        return None

# Prikaz gumba in generiranje
if st.button("✨ USTVARI VEKTORSKI POSTER"):
    with st.spinner("Rišem digitalne poti..."):
        fig = narisi_mapo(kraj, razdalja, barva)
        if fig:
            st.pyplot(fig, clear_figure=True)