import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. DEFINICIJA VSEH 5 TEM
THEMES = {
    "Dark Mode (Classic)": {"bg": "#202124", "roads": "#FFFFFF", "text": "white"},
    "Sea View (Blue)": {"bg": "#001f3f", "roads": "#7FDBFF", "text": "#7FDBFF"},
    "Vintage Paper": {"bg": "#f4f1ea", "roads": "#5b5b5b", "text": "#333333"},
    "Neon Punk": {"bg": "#000000", "roads": "#ff00ff", "text": "#00ffff"},
    "Minimalist White": {"bg": "#ffffff", "roads": "#2c3e50", "text": "#2c3e50"}
}

# 2. FUNKCIJA ZA KOORDINATE
def get_coords(city, country):
    try:
        geolocator = Nominatim(user_agent="city_poster_pro_2026")
        loc = geolocator.geocode(f"{city}, {country}")
        if loc:
            return f"{abs(loc.latitude):.4f}° {'N' if loc.latitude >= 0 else 'S'} / {abs(loc.longitude):.4f}° {'E' if loc.longitude >= 0 else 'W'}"
        return "COORDINATES NOT FOUND"
    except:
        return ""

# 3. GENERIRANJE POSTERJA
def create_map_poster(city, country, dist, theme_name):
    place = f"{city}, {country}"
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    colors = THEMES[theme_name]
    
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color=colors["roads"], edge_linewidth=0.8,
        bgcolor=colors["bg"], show=False, close=False
    )
    
    # Razmik za napise spodaj
    plt.subplots_adjust(bottom=0.28)
    
    # Napis Mesta (VELIKE ČRKE)
    fig.text(0.5, 0.16, city.upper(), fontsize=32, color=colors["text"], 
             ha="center", fontweight="bold", family="sans-serif")
    
    # Napis Države
    fig.text(0.5, 0.11, country.upper(), fontsize=14, color=colors["text"], 
             ha="center", alpha=0.6, family="sans-serif")
    
    # KOORDINATE
    coords = get_coords(city, country)
    fig.text(0.5, 0.07, coords, fontsize=10, color=colors["text"], 
             ha="center", alpha=0.5, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=colors["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# 4. STREAMLIT VMESNIK
st.set_page_config(page_title="Premium City Poster", page_icon="🎨")
st.title("🎨 Premium City Poster Generator")
st.write("Ustvari unikatni umetniški zemljevid s koordinatami.")

city = st.text_input("Mesto", "Novo mesto")
country = st.text_input("Država", "Slovenia")
dist = st.slider("Zoom (razdalja v metrih)", 500, 5000, 2500)
selected_theme = st.selectbox("Izberi umetniški stil", list(THEMES.keys()))

if st.button("🚀 Generiraj Poster"):
    with st.spinner(f"Pripravljam {selected_theme} poster..."):
        try:
            img_buf = create_map_poster(city, country, dist, selected_theme)
            st.image(img_buf, use_container_width=True)
            
            st.download_button(
                label="Prenesi poster v visoki ločljivosti",
                data=img_buf,
                file_name=f"{city}_poster.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Napaka: {e}. Poskusi povečati zoom ali preveri ime mesta.")

# 5. PAYPAL DONACIJE
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 10px;">
        <p style="color: white; font-size: 18px;">Ti je generator prihranil 50€? Časti me s kavo! ☕</p>
        <a href="{paypal_url}" target="_blank">
            <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate">
        </a>
    </div>
''', unsafe_allow_html=True)