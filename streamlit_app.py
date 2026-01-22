import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt

# 1. DEFINICIJA TEM (Vse na enem mestu)
THEMES = {
    "Dark Mode (Classic)": {"bg": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Sea View (Blue)": {"bg": "#001f3f", "roads": "#7FDBFF", "text": "#7FDBFF"},
    "Vintage Paper": {"bg": "#f4f1ea", "roads": "#5b5b5b", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "text": "#00ffff"},
    "Minimalist White": {"bg": "#ffffff", "roads": "#2c3e50", "text": "#2c3e50"}
}

def create_map_poster(city, country, dist, theme):
    place = f"{city}, {country}"
    # Pridobivanje podatkov o cestah
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    
    colors = THEMES[theme]
    
    # Risanje grafa
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color=colors["roads"], edge_linewidth=0.8,
        bgcolor=colors["bg"], show=False, close=False
    )
    
    # Prilagoditev za velike napise
    plt.subplots_adjust(bottom=0.25)
    
    # Glavni napis (VELIKE ČRKE)
    fig.text(0.5, 0.15, city.upper(), fontsize=35, color=colors["text"], 
             ha="center", fontweight="bold", family="sans-serif")
    
    # Napis države
    fig.text(0.5, 0.08, country.upper(), fontsize=15, color=colors["text"], 
             ha="center", alpha=0.6, family="sans-serif")

    # Shranjevanje
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=colors["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# 2. STREAMLIT VMESNIK
st.title("🎨 Premium City Poster Generator")
st.write("Izberi svoj stil in ustvari poster, ki bi ga v trgovini plačal 50€.")

city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Zoom (razdalja v metrih)", 500, 5000, 2500)

# Izbira teme
selected_theme = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Generiraj Premium Poster"):
    with st.spinner(f"Ustvarjam {selected_theme} poster..."):
        try:
            img_buf = create_map_poster(city, country, dist, selected_theme)
            st.image(img_buf, use_container_width=True)
            
            st.download_button(
                label="Prenesi sliko visoke ločljivosti",
                data=img_buf,
                file_name=f"{city}_{selected_theme}.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Prišlo je do napake. Poskusi povečati razdaljo. Opis: {e}")

# 3. PAYPAL DONACIJE
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 10px;">
        <p style="color: white; font-size: 18px;">Ti je generator prihranil denar? Časti me s kavo! ☕</p>
        <a href="{paypal_url}" target="_blank">
            <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate">
        </a>
    </div>
''', unsafe_allow_html=True)