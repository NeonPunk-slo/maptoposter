import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# 1. DEFINICIJA TEM (Z močnim kontrastom za avtoceste)
TEME = {
    "Morski razgled (Moder)": {"bg": "#F1F4F7", "water": "#0077BE", "text": "#063951", "ac": "#E67E22", "glavne": "#063951", "ostalo": "#BDC3C7"},
    "Klasičen temen": {"bg": "#1A1A1B", "water": "#2C3E50", "text": "#FFFFFF", "ac": "#00FFFF", "glavne": "#FFFFFF", "ostalo": "#444444"},
    "Minimalističen bel": {"bg": "#ffffff", "water": "#b3e5fc", "text": "#000000", "ac": "#000000", "glavne": "#95A5A6", "ostalo": "#ECF0F1"},
    "Neon Punk": {"bg": "#000000", "water": "#1A1A1A", "text": "#00FFFF", "ac": "#FFFF00", "glavne": "#FF00FF", "ostalo": "#333333"}
}

def dobi_koordinate_varno(mesto, drzava):
    try:
        geolocator = Nominatim(user_agent="mestna_poezija_2026_final_fix")
        loc = geolocator.geocode(f"{mesto}, {drzava}", timeout=10)
        if loc:
            lat_dir = "S" if loc.latitude >= 0 else "J"
            lon_dir = "V" if loc.longitude >= 0 else "Z"
            return f"{abs(loc.latitude):.4f}° {lat_dir} / {abs(loc.longitude):.4f}° {lon_dir}"
    except:
        pass
    return "46.0500° S / 14.5069° V" # Backup koordinate

def ustvari_poster(mesto, drzava, razdalja, ime_teme):
    kraj = f"{mesto}, {drzava}"
    barve = TEME[ime_teme]
    
    try:
        # Pridobivanje cestnega omrežja
        G = ox.graph_from_address(kraj, dist=razdalja, network_type="all")
        
        # Varno pridobivanje vode (morje, reke, zalivi)
        try:
            voda = ox.features_from_address(kraj, 
                                            tags={"natural": ["water", "coastline", "bay"], 
                                                  "water": True, 
                                                  "waterway": "river"}, 
                                            dist=razdalja)
        except:
            voda = None

        # Logika barv in debelin za "kontra" efekt
        road_colors, road_widths = [], []
        for u, v, k, data in G.edges(data=True, keys=True):
            h_type = data.get("highway", "unclassified")
            if h_type in ["motorway", "trunk", "motorway_link"]:
                road_colors.append(barve["ac"])
                road_widths.append(4.0)
            elif h_type in ["primary", "secondary", "primary_link"]:
                road_colors.append(barve["glavne"])
                road_widths.append(2.0)
            else:
                road_colors.append(barve["ostalo"])
                road_widths.append(0.6)

        # Kreiranje slike (format 12x16 za poster)
        fig, ax = plt.subplots(figsize=(12, 16), facecolor=barve["bg"])
        ax.set_facecolor(barve["bg"])
        
        # Izris vode pod cestami
        if voda is not None and not voda.empty:
            voda.plot(ax=ax, color=barve["water"], zorder=1)
        
        # Izris cest
        ox.plot_graph(G, ax=ax, node_size=0, edge_color=road_colors, edge_linewidth=road_widths, show=False, close=False)
        ax.axis('off')
        
        # Prilagoditev prostora za napise (fiksno, da se ne odrežejo)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.22)
        
        # Besedila na dnu
        fig.text(0.5, 0.14, mesto.upper(), fontsize=65, color=barve["text"], ha="center", fontweight="bold")
        fig.text(0.5, 0.10, drzava.upper(), fontsize=25, color=barve["text"], ha="center", alpha=0.8)
        
        koordinate = dobi_koordinate_varno(mesto, drzava)
        fig.text(0.5, 0.06, koordinate, fontsize=18, color=barve["text"], ha="center", alpha=0.6, family="monospace")

        buf = io.BytesIO()
        # Shranjevanje brez bbox_inches='tight', da koordinate ostanejo vidne
        fig.savefig(buf, format="png", facecolor=barve["bg"], dpi=150)
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        st.error(f"Napaka pri generiranju: {e}")
        return None

# --- STREAMLIT VMESNIK ---
st.set_page_config(page_title="Mestna Poezija", layout="centered")
st.title("🎨 Mestna Poezija")

mesto = st.text_input("Ime kraja", "Ljubljana")
drzava = st.text_input("Država", "Slovenija")
razdalja = st.number_input("Zoom (v metrih)", min_value=500, max_value=25000, value=5000)
izbrana_tema = st.selectbox("Izberi umetniški slog", list(TEME.keys()))

if st.button("✨ Ustvari umetniško delo"):
    with st.spinner("Rišem ceste in koordinate..."):
        rezultat = ustvari_poster(mesto, drzava, razdalja, izbrana_tema)
        if rezultat:
            # Uporabljamo fiksno širino za boljšo stabilnost v brskalniku
            st.image(rezultat, width=700)
            st.download_button(label="📥 Prenesi poster (PNG)", data=rezultat, file_name=f"{mesto}_poezija.png")

# --- DONACIJE ---
st.write("---")
paypal_url = "https://www.paypal.me/NeonPunkSlo"
st.markdown(f'''
    <div style="text-align: center;">
        <p style="color: #888;">Ti je rezultat všeč? Podpri razvoj aplikacije.</p>
        <a href="{paypal_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffc439; color: black; padding: 12px 24px; border-radius: 25px; font-weight: bold; display: inline-block;">
                💛 PayPal Donacija
            </div>
        </a>
    </div>
''', unsafe_allow_html=True)