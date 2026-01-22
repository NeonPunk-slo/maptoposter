import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="City Poster Generator", layout="centered")

# Teme, ki jih že poznaš
THEMES = {
    "Sea View": {"bg": "#f0f4f7", "water": "#0077be", "hway": "#004466", "other": "#999999", "txt": "#004466"},
    "Gold Luxury": {"bg": "#0b0d0f", "water": "#1a1c1e", "hway": "#ffcc33", "other": "#555555", "txt": "#ffcc33"},
    "Cyberpunk": {"bg": "#050a1a", "water": "#112244", "hway": "#ff00ff", "other": "#4d4d4d", "txt": "#ffcc00"},
    "Forest": {"bg": "#020a02", "water": "#0a2212", "hway": "#2ecc71", "other": "#445544", "txt": "#2ecc71"}
}

st.title("🎨 Generator mestnih posterjev")
st.write("Vnesi podatke in si prenesi svoj umetniški zemljevid.")

# Vnosni podatki na strani
city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Razdalja v metrih (zoom)", 500, 5000, 2500)
theme_name = st.selectbox("Izberi stil", list(THEMES.keys()))

if st.button("🚀 Ustvari poster"):
    colors = THEMES[theme_name]
    place = f"{city}, {country}"
st.write("---")
st.subheader("☕ Podpri projekt")
st.write("Če ti je generator všeč, lahko podpreš moj trud z majhno donacijo. Vsak evro pomaga pri razvoju novih stilov in vzdrževanju strani!")

# Tvoja uradna PayPal povezava
paypal_url = "https://www.paypal.me/NeonPunkSlo"

st.markdown(f'''
    <a href="{paypal_url}" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate with PayPal">
    </a>
''', unsafe_allow_html=True)

st.caption("Hvala za tvojo podporo! 🚀")
    
    with st.spinner("Pridobivam podatke iz zemljevidov... Počakaj trenutek."):
        try:
            # Pridobivanje podatkov
            graph = ox.graph_from_address(place, dist=dist, network_type="all")
            
            # Izris
            fig, ax = plt.subplots(figsize=(10, 14), facecolor=colors["bg"])
            ax.set_facecolor(colors["bg"])
            
            c_list = [colors["hway"] if 'motorway' in str(d.get('highway', '')) else colors["other"] for _, _, d in graph.edges(data=True)]
            ox.plot_graph(graph, ax=ax, node_size=0, edge_color=c_list, edge_linewidth=0.8, show=False, close=False)
            
            # Napis
            plt.text(0.5, 0.1, city.upper(), transform=fig.transFigure, ha='center', fontsize=40, color=colors["txt"], fontweight='bold')
            st.pyplot(fig)
            
            # Priprava za prenos
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300)
            st.download_button(label="📥 Prenesi sliko", data=buf.getvalue(), file_name=f"{city}_poster.png", mime="image/png")
            
        except Exception as e:
            st.error(f"Prišlo je do napake: {e}")

st.divider()
st.caption("Projekt ustvarjen za Reddit skupnost. 50€ pa roka! 😉")