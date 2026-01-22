import streamlit as st
import io
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

def get_coordinates(city, country):
    try:
        geolocator = Nominatim(user_agent="city_poster_generator")
        location = geolocator.geocode(f"{city}, {country}")
        if location:
            # Formatiranje v stopinje, minute, sekunde (ali decimalno)
            return f"{abs(location.latitude):.4f}° {'N' if location.latitude >= 0 else 'S'} / {abs(location.longitude):.4f}° {'E' if location.longitude >= 0 else 'W'}"
        return ""
    except:
        return ""

def create_map_poster(city, country, dist, theme):
    place = f"{city}, {country}"
    graph = ox.graph_from_address(place, dist=dist, network_type="all")
    colors = THEMES[theme]
    
    fig, ax = ox.plot_graph(
        graph, node_size=0, edge_color=colors["roads"], edge_linewidth=0.8,
        bgcolor=colors["bg"], show=False, close=False
    )
    
    # Prilagoditev za napise
    plt.subplots_adjust(bottom=0.28)
    
    # Mesto
    fig.text(0.5, 0.16, city.upper(), fontsize=32, color=colors["text"], 
             ha="center", fontweight="bold", family="sans-serif")
    
    # Država
    fig.text(0.5, 0.11, country.upper(), fontsize=14, color=colors["text"], 
             ha="center", alpha=0.6, family="sans-serif")
    
    # KOORDINATE (Nova vrstica)
    coords_text = get_coordinates(city, country)
    fig.text(0.5, 0.07, coords_text, fontsize=10, color=colors["text"], 
             ha="center", alpha=0.5, family="monospace")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=colors["bg"], dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# --- Preostanek Streamlit kode ostane enak kot prej ---