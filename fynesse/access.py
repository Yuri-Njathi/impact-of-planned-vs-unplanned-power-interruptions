from .config import *
import osmnx as ox
import matplotlib.pyplot as plt
import math
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import geopandas as gpd
from io import StringIO


BASE_URL = "https://www.kplc.co.ke/customer-support"
SAVE_DIR = "kplc_pdfs"

os.makedirs(SAVE_DIR, exist_ok=True)
def epra_data():# -> Union[pd.DataFrame, Any]:
    '''returns epra_reliability_index_df '''
    return pd.read_csv('impact-of-planned-vs-unplanned-power-interruptions/data/formatted_epra_data.csv')
def census_kplc_data():    
    '''merged census_and_kplc_interruptions_data'''
    kplc_data = pd.read_csv('impact-of-planned-vs-unplanned-power-interruptions/data/census_and_kplc_interruptions_data.csv')
    kplc_data['electrified_households'] = round(kplc_data['Conventional Households']*kplc_data['Mains Electricity']/100.0).astype(int)
    return kplc_data
def kplc_data():# -> Union[pd.DataFrame, Any]:
    '''returns epra_reliability_index_df '''
    return pd.read_csv('impact-of-planned-vs-unplanned-power-interruptions/data/formatted_kplc_interruptions.csv')
    
def get_code_county_maps():
    # '''
    # return county_to_code dictionary and code_to_county
    # '''
    # #data obtained from wikipedia
    # data = """
    # Code	County	Former Province	Area(km2)	Population(2009 Census)	Population (2019 Census)	Capital	Postal Abbreviations
    
    # 001	 Mombasa	Coast	212.5	939,370	1,208,333	Mombasa	MSA
    # 002	 Kwale	Coast	8,270.3	649,931	866,820	Kwale	KWL
    # 003	 Kilifi	Coast	12,245.9	1,109,735	1,453,787	Kilifi	KLF
    # 004	 Tana River	Coast	35,375.8	240,075	315,943	Hola	TRV
    # 005	 Lamu	Coast	6,497.7	101,539	143,920	Lamu	LMU
    # 006	 Taita–Taveta	Coast	17,083.9	284,657	340,671	Mwatate	TVT
    # 007	 Garissa	North Eastern	45,720.2	623,060	841,353	Garissa	GRS
    # 008	 Wajir	North Eastern	55,840.6	661,941	781,263	Wajir	WJR
    # 009	 Mandera	North Eastern	25,797.7	1,025,756	867,457	Mandera	MDR
    # 010	 Marsabit	Eastern	66,923.1	291,166	459,785	Marsabit	MRS
    # 11	 Isiolo	Eastern	25,336.1	143,294	268,002	Isiolo	ISL
    # 12	 Meru	Eastern	7,003.1	1,356,301	1,545,714	Meru	MRU
    # 13	 Tharaka-Nithi	Eastern	2,609.5	365,330	393,177	Kathwana	TNT
    # 14	 Embu	Eastern	2,555.9	516,212	608,599	Embu	EMB
    # 15	 Kitui	Eastern	24,385.1	1,012,709	1,136,187	Kitui	KTU
    # 16	 Machakos	Eastern	5,952.9	1,098,584	1,421,932	Machakos	MCK
    # 17	 Makueni	Eastern	8,008.9	884,527	987,653	Wote	MKN
    # 18	 Nyandarua	Central	3,107.7	596,268	638,289	Ol Kalou	NDR
    # 19	 Nyeri	Central	2,361.0	693,558	759,164	Nyeri	NYR
    # 20	 Kirinyaga	Central	1,205.4	528,054	610,411	Kerugoya	KRG
    # 21	 Murang'a	Central	2,325.8	942,581	1,056,640	Murang'a	MRG
    # 22	 Kiambu	Central	2,449.2	1,623,282	2,417,735	Kiambu	KMB
    # 23	 Turkana	Rift Valley	98,597.8	1,100,399	1,504,976	Lodwar	TRK
    # 24	 West Pokot	Rift Valley	8,418.2	512,690	621,241	Kapenguria	WPK
    # 25	 Samburu	Rift Valley	20,182.5	223,947	310,327	Maralal	SBR
    # 26	 Trans-Nzoia	Rift Valley	2,469.9	818,757	990,341	Kitale	TNZ
    # 27	 Uasin Gishu	Rift Valley	2,955.3	894,179	1,163,186	Eldoret	UGS
    # 28	 Elgeyo-Marakwet	Rift Valley	3,049.7	369,998	454,480	Iten	EMK
    # 29	 Nandi	Rift Valley	2,884.5	752,965	885,711	Kapsabet	NDI
    # 30	 Baringo	Rift Valley	11,075.3	555,561	666,763	Kabarnet	BRG
    # 31	 Laikipia	Rift Valley	8,696.1	399,227	518,560	Rumuruti	LKP
    # 32	 Nakuru	Rift Valley	7,509.5	1,603,325	2,162,202	Nakuru[8][9]	NKR
    # 33	 Narok	Rift Valley	17,921.2	850,920	1,157,873	Narok	NRK
    # 34	 Kajiado	Rift Valley	21,292.7	687,312	1,117,840	Kajiado	KJD
    # 35	 Kericho	Rift Valley	2,454.5	752,396	901,777	Kericho	KRC
    # 36	 Bomet	Rift Valley	1,997.9	730,129	875,689	Bomet	BMT
    # 37	 Kakamega	Western	3,033.8	1,660,651	1,867,579	Kakamega	KKG
    # 38	 Vihiga	Western	531.3	554,622	590,013	Mbale	VHG
    # 39	 Bungoma	Western	2,206.9	1,375,063	1,670,570	Bungoma	BGM
    # 40	 Busia	Western	1,628.4	743,946	893,681	Busia	BSA
    # 41	 Siaya	Nyanza	2,496.1	842,304	993,183	Siaya	SYA
    # 42	 Kisumu	Nyanza	2,009.5	968,909	1,155,574	Kisumu	KSM
    # 43	 Homa Bay	Nyanza	3,154.7	963,794	1,131,950	Homa Bay	HBY
    # 44	 Migori	Nyanza	2,586.4	917,170	1,116,436	Migori	MGR
    # 45	 Kisii	Nyanza	1,317.9	1,152,282	1,266,860	Kisii	KSI
    # 46	 Nyamira	Nyanza	912.5	598,252	605,576	Nyamira	NMR
    # 47	 Nairobi	Nairobi	694.9	3,138,369	4,397,073	Nairobi	NBI
    # 581,309.0	38,610,997	47,564,296	Nairobi	
    # """
    
    # # Read into DataFrame
    # df_code = pd.read_csv(StringIO(data), sep="\t")
    
    # # Keep only valid rows (drop the summary row at the bottom)
    # df_code = df_code[df_code["Code"].apply(lambda x: str(x).isdigit())]
    
    # df_code["County"] = df_code["County"].str.lower()
    # # Make dictionary {County:Code}, keeping leading zeros
    # county_to_code = dict(zip(df_code["County"].str.strip(),df_code["Code"].astype(str).str.zfill(3)))
    # code_to_county = dict(zip(df_code["Code"].astype(str).str.zfill(3),df_code["County"].str.strip()))
    code_to_county = {'001': 'mombasa', '002': 'kwale', '003': 'kilifi', '004': 'tana river', '005': 'lamu', '006': 'taita taveta', '007': 'garissa', '008': 'wajir', '009': 'mandera', '010': 'marsabit', '011': 'isiolo', '012': 'meru', '013': 'tharaka-nithi', '014': 'embu', '015': 'kitui', '016': 'machakos', '017': 'makueni', '018': 'nyandarua', '019': 'nyeri', '020': 'kirinyaga', '021': "murang'a", '022': 'kiambu', '023': 'turkana', '024': 'west pokot', '025': 'samburu', '026': 'trans nzoia', '027': 'uasin gishu', '028': 'elgeyo-marakwet', '029': 'nandi', '030': 'baringo', '031': 'laikipia', '032': 'nakuru', '033': 'narok', '034': 'kajiado', '035': 'kericho', '036': 'bomet', '037': 'kakamega', '038': 'vihiga', '039': 'bungoma', '040': 'busia', '041': 'siaya', '042': 'kisumu', '043': 'homa bay', '044': 'migori', '045': 'kisii', '046': 'nyamira', '047': 'nairobi'} 
    county_to_code = {'mombasa': '001', 'kwale': '002', 'kilifi': '003', 'tana river': '004', 'lamu': '005', 'taita taveta': '006', 'garissa': '007', 'wajir': '008', 'mandera': '009', 'marsabit': '010', 'isiolo': '011', 'meru': '012', 'tharaka-nithi': '013', 'embu': '014', 'kitui': '015', 'machakos': '016', 'makueni': '017', 'nyandarua': '018', 'nyeri': '019', 'kirinyaga': '020', "murang'a": '021', 'kiambu': '022', 'turkana': '023', 'west pokot': '024', 'samburu': '025', 'trans nzoia': '026', 'uasin gishu': '027', 'elgeyo-marakwet': '028', 'nandi': '029', 'baringo': '030', 'laikipia': '031', 'nakuru': '032', 'narok': '033', 'kajiado': '034', 'kericho': '035', 'bomet': '036', 'kakamega': '037', 'vihiga': '038', 'bungoma': '039', 'busia': '040', 'siaya': '041', 'kisumu': '042', 'homa bay': '043', 'migori': '044', 'kisii': '045', 'nyamira': '046', 'nairobi': '047'}
    return county_to_code, code_to_county

def get_kenyan_map():
    counties_gdf = gpd.read_file("/kaggle/input/kenya-map-data/kenya_admin_levels.geojson")
    country_gdf = gpd.read_file("/kaggle/input/kenya-map-data/kenya_admin.gpkg", layer="country")
    #Get Kenya polygon
    kenya_poly = gdf.iloc[0].geometry

    if "ISO3166-2" in gdf_counties.columns:
        gdf_counties = gdf_counties[gdf_counties["ISO3166-2"].str.startswith("KE-", na=False)]
    
    # clean up labels
    
    # Use name:en (English) if available, else fall back to name or official_name.
    
    if "name:en" in gdf_counties.columns:
        gdf_counties["label"] = (
            gdf_counties["name:en"]
            .fillna(gdf_counties["name"])
            .fillna(gdf_counties["official_name"])
        )
    else:
        gdf_counties["label"] = gdf_counties["name"]
    
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
    
