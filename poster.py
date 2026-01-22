import matplotlib.pyplot as plt
import osmnx as ox
from pathlib import Path

# Nastavitev mape za shranjevanje
output_dir = Path("posters")
output_dir.mkdir(exist_ok=True)

# Vseh 6 tem s popravljenim kontrastom (Reddit Feedback Edition)
THEMES = {
    "sea_view": {"bg": "#f0f4f7", "water": "#0077be", "hway": "#004466", "prim": "#444444", "other": "#999999", "txt": "#004466"},
    "gold": {"bg": "#0b0d0f", "water": "#1a1c1e", "hway": "#ffcc33", "prim": "#ffffff", "other": "#555555", "txt": "#ffcc33"},
    "cyberpunk": {"bg": "#050a1a", "water": "#112244", "hway": "#ff00ff", "prim": "#00ffff", "other": "#4d4d4d", "txt": "#ffcc00"},
    "forest": {"bg": "#020a02", "water": "#0a2212", "hway": "#2ecc71", "prim": "#ffffff", "other": "#445544", "txt": "#2ecc71"},
    "blueprint": {"bg": "#102a43", "water": "#0c1b2d", "hway": "#48bb78", "prim": "#38a169", "other": "#ffffff", "txt": "#ffffff"},
    "ink": {"bg": "#ffffff", "water": "#e0e0e0", "hway": "#000000", "prim": "#333333", "other": "#999999", "txt": "#000000"}
}

def create_all_posters():
    print("\n" + "="*40)
    print("   GENERATOR VSEH 6 TEM (Full Power)")
    print("="*40)
    
    city = input("Vnesi mesto (npr. Novo mesto): ")
    country = input("Vnesi državo (npr. Slovenia): ")
    try:
        dist = int(input("Vnesi razdaljo (npr. 2500): "))
    except:
        dist = 2500

    place = f"{city}, {country}"
    print(f"\n>>> Pridobivam podatke za {place}...")
    
    try:
        # Pridobivanje podatkov o mestu in koordinat
        gdf = ox.geocode_to_gdf(place)
        lat, lon = gdf.iloc[0]['lat'], gdf.iloc[0]['lon']
        coords = f"{abs(lat):.4f}° {'N' if lat>0 else 'S'} / {abs(lon):.4f}° {'E' if lon>0 else 'W'}"
        graph = ox.graph_from_address(place, dist=dist, network_type="all")
        
        try:
            water = ox.features_from_address(place, tags={"natural": ["water", "coastline", "bay"], "waterway": True}, dist=dist)
        except:
            water = None

        # Zanka, ki gre skozi vseh 6 tem
        for name, colors in THEMES.items():
            print(f"    -> Delam temo: {name.upper()}")
            
            # Priprava figure s prostorom za napise spodaj
            fig, ax = plt.subplots(figsize=(12, 16), facecolor=colors["bg"])
            plt.subplots_adjust(bottom=0.2, top=0.95, left=0.05, right=0.95)
            ax.set_facecolor(colors["bg"])

            # 1. Izris vode
            if water is not None and not water.empty:
                water.plot(ax=ax, color=colors["water"], zorder=1)

            # 2. Priprava debeline cest glede na tip
            c_list, w_list = [], []
            for _, _, d in graph.edges(data=True):
                h = str(d.get('highway', ''))
                if 'motorway' in h or 'trunk' in h:
                    c_list.append(colors["hway"]); w_list.append(2.5)
                elif 'primary' in h or 'secondary' in h:
                    c_list.append(colors["prim"]); w_list.append(1.5)
                else:
                    c_list.append(colors["other"]); w_list.append(0.8)
            
            # 3. Izris cestnega omrežja
            ox.plot_graph(graph, ax=ax, node_size=0, edge_color=c_list, edge_linewidth=w_list, show=False, close=False)
            ax.axis('off')
            
            # 4. Dodajanje napisov (spaced city name)
            spaced_city = "  ".join(list(city.upper()))
            plt.text(0.5, 0.12, spaced_city, transform=fig.transFigure, ha='center', fontsize=45, color=colors["txt"], fontweight='bold')
            plt.text(0.5, 0.08, country.upper(), transform=fig.transFigure, ha='center', fontsize=20, color=colors["txt"])
            plt.text(0.5, 0.05, coords, transform=fig.transFigure, ha='center', fontsize=12, color=colors["txt"], alpha=0.6)
            
            # 5. Shranjevanje in nujno čiščenje spomina
            filename = f"{city.lower().replace(' ', '_')}_{name}.png"
            plt.savefig(output_dir / filename, dpi=300, facecolor=colors["bg"])
            
            plt.clf() # Izbriše trenutno vsebino figure
            plt.close(fig) # Popolnoma zapre figuro
            
        print(f"\n>>> USPEŠNO! Preveri mapo 'posters'.")
        
    except Exception as e:
        print(f"\nNAPAKA: {e}")

if __name__ == "__main__":
    create_all_posters()