from .config import *
import osmnx as ox
import matplotlib.pyplot as plt
import math
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd 

BASE_URL = "https://www.kplc.co.ke/customer-support"
SAVE_DIR = "kplc_pdfs"

os.makedirs(SAVE_DIR, exist_ok=True)
def data():# -> Union[pd.DataFrame, Any]:
    '''returns epra_reliability_index_df and merged census_and_kplc_interruptions_data'''
    return [pd.read_csv('https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/data/formatted_epra_data.csv'),pd.read_csv('https://github.com/Yuri-Njathi/impact-of-planned-vs-unplanned-power-interruptions/blob/main/data/census_and_kplc_interruptions_data.csv')]

def get_osm_datapoints(latitude, longitude, box_size_km=2, poi_tags=None):
    """
    Function for getting OSM data

    Parameters
    ----------
    place_name : str
        Name of the place (used for boundary + plot title).
    latitude, longitude : float
        Central coordinates.
    box_size_km : float
        Size of the bounding box in kilometers (default 2 km).
    poi_tags : dict, optional
        Tags dict for POIs (e.g. {"amenity": ["school", "restaurant"]}).
    
    Returns
    -------
    bbox : tuple
        Bounding box (west, south, east, north).
    nodes : GeoDataFrame
        OSM nodes.
    edges : GeoDataFrame
        OSM edges.
    buildings : GeoDataFrame
        OSM buildings.
    pois : GeoDataFrame or None
        OSM points of interest (if poi_tags provided), else None.
    """
    
    # Convert km to degrees
    lat_offset = (box_size_km / 2) / 111
    lon_offset = (box_size_km / 2) / (111 * math.cos(math.radians(latitude)))

    north = latitude + lat_offset
    south = latitude - lat_offset
    east = longitude + lon_offset
    west = longitude - lon_offset
    bbox = (west, south, east, north)

    # Road graph
    graph = ox.graph_from_bbox(bbox, network_type="all")
    nodes, edges = ox.graph_to_gdfs(graph)

    # Buildings & POIs
    buildings = ox.features_from_bbox(bbox, tags={"building": True})
    pois = None
    if poi_tags:
        pois = ox.features_from_bbox(bbox, tags=poi_tags)
    
    # Ensure correct geometry column
    nodes = nodes.set_geometry("geometry")
    edges = edges.set_geometry("geometry")
    buildings = buildings.set_geometry("geometry")
    
    if pois is not None:
        pois = pois.set_geometry("geometry")
    
    return bbox, nodes, edges, buildings, pois

def plot_city_map(place_name, latitude, longitude, box_size_km=2, poi_tags=None):
    """
    Plot a simple city map with area boundary, buildings, roads, nodes, and optional POIs.

    Parameters
    ----------
    place_name : str
        Name of the place (used for boundary + plot title).
    latitude, longitude : float
        Central coordinates.
    box_size_km : float
        Size of the bounding box in kilometers (default 2 km).
    poi_tags : dict, optional
        Tags dict for POIs (e.g. {"amenity": ["school", "restaurant"]}).
    """

    bbox, nodes, edges, buildings, pois = get_osm_datapoints(latitude, longitude, box_size_km, poi_tags)
    west, south, east, north = bbox

    # Area boundary
    area = ox.geocode_to_gdf(place_name).to_crs(epsg=4326)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 6))
    area.plot(ax=ax, color="tan", alpha=0.5)
    if not buildings.empty:
        buildings.plot(ax=ax, facecolor="gray", edgecolor="gray", linewidth=0.5)
    edges.plot(ax=ax, color="black", linewidth=1, alpha=0.3, column=None)
    nodes.plot(ax=ax, color="black", markersize=1, alpha=0.3, column=None)
    if pois is not None and not pois.empty:
        pois.plot(ax=ax, color="green", markersize=5, alpha=1, column=None)
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_title(place_name, fontsize=14)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


def get_pdf_links(page):
    url = f"{BASE_URL}?page={page}#powerschedule"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".pdf") and "storage" in href:
            pdf_links.append(href)
    return pdf_links

def download_pdf(url, save_dir=SAVE_DIR):
    filename = url.split("/")[-1]
    filepath = os.path.join(save_dir, filename)
    if not os.path.exists(filepath):  # avoid duplicates
        print(f"Downloading: {filename}")
        r = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(r.content)


def clean_date(x: str) -> str:
    x = x.strip()

    # Remove trailing 'to'
    x = re.sub(r"\s*to$", "", x, flags=re.IGNORECASE)

    # Normalize spaces
    x = re.sub(r"\s+", " ", x)

    # Remove colons after weekday names
    x = re.sub(r"([A-Za-z]+):", r"\1", x)

    # Fix spaces inside weekday names (Tu esday -> Tuesday, Wednesda y -> Wednesday)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for wd in weekdays:
        x = re.sub(r"(?i)" + r"\s*".join(list(wd)), wd, x)

    # ✅ Insert missing space between weekday and date
    x = re.sub(r"(?i)(" + "|".join(weekdays) + r")(\d{1,2}\.\d{1,2}\.\d{4})", r"\1 \2", x)

    # Fix spaces around dots in dates
    x = re.sub(r"\s*\.\s*", ".", x)

    # Fix digits split by spaces
    x = re.sub(r"(\d)\s+(\d)", r"\1\2", x)

    # Fix zero months like "16.00.2025" → assume "01"
    x = re.sub(r"\.00\.", ".01.", x)

    # Pad single-digit months/days with 0
    x = re.sub(r"\.(\d)\.", r".0\1.", x)

    # If multiple dates ("... & ...") → keep only first
    if "&" in x:
        x = x.split("&")[0].strip()

    # Remove trailing dot
    x = x.rstrip(".")

    return x.strip()
def clean_time_string(s):
    if pd.isna(s):
        return s
    
    s = s.strip()

    # Normalize dash
    s = re.sub(r"[–—-]", "-", s)

    # Remove extra spaces around dots
    s = re.sub(r"\s*\.\s*", ".", s)

    # Fix AM/PM variants (remove periods fully)
    s = re.sub(r"\bA\.?M\.?\b", "AM", s, flags=re.IGNORECASE)
    s = re.sub(r"\bP\.?M\.?\b", "PM", s, flags=re.IGNORECASE)

    # Sometimes "AM." or "PM." may remain → remove trailing dot
    s = re.sub(r"(AM|PM)\.", r"\1", s)

    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s)

    return s.strip()

def clean_time(x: str) -> str:
    if pd.isna(x):
        return x
    
    x = x.strip()  # remove leading/trailing spaces
    x = x.replace(":", ".")  # normalize ":" and "." as separators
    
    # remove stray characters like ': ' before time
    x = re.sub(r"^[^0-9]+", "", x)
    
    # fix spaces in digits like "9.0 0" -> "9.00"
    x = re.sub(r"(\d)\s+(\d)", r"\1\2", x)
    
    # normalize A.M./P.M. variations -> AM/PM
    x = re.sub(r"\.?[Aa]\.?[Mm]\.?", "AM", x)
    x = re.sub(r"\.?[Pp]\.?[Mm]\.?", "PM", x)
    
    # ensure single space before AM/PM
    x = re.sub(r"\s*(AM|PM)$", r" \1", x)
    
    # normalize HH.MM to HH:MM
    x = re.sub(r"(\d{1,2})\.(\d{1,2})", r"\1:\2", x)
    
    # pad minutes (e.g., 9:0 -> 9:00, 9:5 -> 9:05)
    x = re.sub(r":(\d)(\s*[AP]M)", r":0\1\2", x)
    
    # pad hour if single digit (e.g., 9:30 -> 09:30)
    if re.match(r"^\d:", x):
        x = "0" + x
    
