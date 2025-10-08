from typing import Any, Union, Tuple, Dict, Optional, cast
import matplotlib.pyplot as plt
import seaborn as sns
import math
import osmnx as ox
import pandas as pd
import logging
import yaml
import os
import geopandas as gpd
import osmnx as ox

from .config import *
from . import access

# Set up logging
logger = logging.getLogger(__name__)

"""These are the types of import we might expect in this file
import pandas
import bokeh
import seaborn
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""

"""Place commands in this file to assess the data you have downloaded.
How are missing values encoded, how are outliers encoded? What do columns represent,
makes rure they are correctly labeled. How is the data indexed. Crete visualisation
routines to assess the data (e.g. in bokeh). Ensure that date formats are correct
and correctly timezoned."""
def plot_series(s,x,y,title,ylabel,xlabel):    
    # Plot
    plt.figure(figsize=(12,6))
    sns.barplot(
        data=s,#mean_electricity,
        x=x,
        y=y,#"Mains Electricity",
        palette="viridis"
    )
    plt.xticks(rotation=45, ha='right')
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.show()

def plot_interruptions_by_day_of_month(interruptions_per_day,duration_by_day):
    # A figure with two vertical subplots 
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # --- First subplot: Number of Interruptions ---
    sns.barplot(data=interruptions_per_day, x='day_of_month', y='interruptions', palette='viridis', ax=axes[0])
    axes[0].set_title("Number of Interruptions by Day of Month")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Number of Interruptions")
    axes[0].tick_params(axis='x', rotation=0)
    
    # --- Second subplot: Total Duration ---
    sns.barplot(data=duration_by_day, x='day_of_month', y='duration_hours', palette='viridis', ax=axes[1])
    axes[1].set_title("Total Interruption Duration by Day of Month")
    axes[1].set_xlabel("Day of Month")
    axes[1].set_ylabel("Total Duration (hours)")
    axes[1].tick_params(axis='x', rotation=0)
    
    # Adjust layout for better spacing
    plt.tight_layout()
    plt.show()


def plot_indices_with_duration_of_interruption(duration_of_interruptions_per_month,counties_merged):
    plt.figure(figsize=(12,6))
    sns.set_style("white")
    
    # Main axis (barplot)
    fig, ax1 = plt.subplots(figsize=(12,6))
    sns.barplot(
        data=duration_of_interruptions_per_month,
        x="month_year", y="total_duration",
        palette="viridis", ax=ax1
    )
    ax1.set_ylabel("Total Duration (hours)", fontsize=12)
    ax1.set_xlabel("Month-Year", fontsize=12)
    
    # Secondary axis for SAIDI
    ax2 = ax1.twinx()
    sns.lineplot(data=counties_merged, x="month_year", y="SAIDI",marker="o", color="red", ax=ax2, label="SAIDI",legend=False)
    ax2.set_ylabel("SAIDI-SAIFI-CAIDI", fontsize=12)
    ax2.set_ylim(0, 12)
    
    # Third axis (shift outward for SAIFI)
    ax3 = ax1.twinx()
    #ax3.spines["right"].set_position(("outward", 50))  # shift right
    sns.lineplot(data=counties_merged, x="month_year", y="SAIFI",marker="o", color="orange", ax=ax3, label="SAIFI",legend=False)
    ax3.set_ylabel("", fontsize=12)
    ax3.set_ylim(0, 12)
    
    # Fourth axis (shift outward for CAIDI)
    ax4 = ax1.twinx()
    #ax4.spines["right"].set_position(("outward", 100))  # shift further right
    sns.lineplot(data=counties_merged, x="month_year", y="CAIDI",marker="o", color="blue", ax=ax4, label="CAIDI",legend=False)
    ax4.set_ylabel("", fontsize=12)
    ax4.set_ylim(0, 12)
    
    # Title
    ax1.set_title("Total Planned Interruption Duration, SAIDI, SAIFI and CAIDI by Month", fontsize=14)
    
    # Rotate x labels
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
    
    # Combine legends
    lines, labels = [], []
    for ax in [ax2, ax3, ax4]:
        line, label = ax.get_legend_handles_labels()
        lines += line
        labels += label
    ax1.legend(lines, labels, loc="upper left")
    
    plt.tight_layout()
    plt.show()

def get_kenyan_map_with_series(df,gdf_counties, gdf, kenya_poly,title="Interruptions per County",col="num_instances"):
    # counties = gpd.clip(gdf_counties, kenya_poly)
    # # Load CSV of counties
    # counties_csv = pd.read_csv("/kaggle/input/kenya-census-data/kenya_census_data.csv")
    # # Ensure county names are clean on both sides
    df["county"] = df["county"].str.strip().str.title()
    # counties_csv.drop(columns = ['geometry'],inplace=True)
    # Merge CSV with OSMnx data
    counties_merged = gdf_counties.merge(df, left_on="name", right_on="county", how="outer")
    
    ax = counties_merged.plot(column=col, legend=True,cmap="RdYlBu")
    plt.title(title, fontsize=16)
    #plt.axis("off")  # optional, to hide axes
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    plt.show()

def get_kenyan_map_with_electricity(gdf_counties, gdf, kenya_poly):
    counties = gpd.clip(gdf_counties, kenya_poly)
    # Load CSV of counties
    counties_csv = pd.read_csv("/kaggle/input/kenya-census-data/kenya_census_data.csv")
    # Ensure county names are clean on both sides
    counties["name"] = counties["name"].str.strip().str.title()
    counties_csv.drop(columns = ['geometry'],inplace=True)
    # Merge CSV with OSMnx data
    counties_merged = gdf_counties.merge(counties_csv, left_on="name", right_on="County", how="outer")
    
    ax = counties_merged.plot(column="Mains Electricity", legend=True,cmap="RdYlBu")
    plt.title("Electricity Use by Kenyan Counties", fontsize=16)
    #plt.axis("off")  # optional, to hide axes
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    plt.show()

import geopandas as gpd
import osmnx as ox

def get_kenyan_maps():
    '''
    returns county_maps, entire_country_map and country_polygon
    '''
    success = False
    
    try:
        #try presaved locations
        gdf_counties = gpd.read_file("/kaggle/input/kenya-map-data/kenya_admin_levels.geojson")
        gdf = gpd.read_file("/kaggle/input/kenya-map-data/kenya_admin.gpkg", layer="country")
        #Get Kenya polygon
        kenya_poly = gdf.iloc[0].geometry

        success = True
    except:
        try:
            # 1. National boundary
            gdf = ox.geocode_to_gdf("Kenya")  
            #Get Kenya polygon
            kenya_poly = gdf.iloc[0].geometry
            tags = {"boundary": "administrative"}
            # 2. Counties (admin_level=4)
            gdf_counties = ox.features_from_polygon(kenya_poly, tags) #ox.features_from_place("Kenya", {"admin_level": "4"}) 
            

            success = True
        except:
            pass
    
    if success:
        print("Obtaining Maps succeeded")
    else:
        print("All methods for obtaining maps failed.")
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
        return gdf_counties, gdf, kenya_poly


def data() -> Union[pd.DataFrame, Any]:
    """
    Load the data from access and ensure missing values are correctly encoded as well as
    indices correct, column names informative, date and times correctly formatted.
    Return a structured data structure such as a data frame.

    IMPLEMENTATION GUIDE FOR STUDENTS:
    ==================================

    1. REPLACE THIS FUNCTION WITH YOUR DATA ASSESSMENT CODE:
       - Load data using the access module
       - Check for missing values and handle them appropriately
       - Validate data types and formats
       - Clean and prepare data for analysis

    2. ADD ERROR HANDLING:
       - Handle cases where access.data() returns None
       - Check for data quality issues
       - Validate data structure and content

    3. ADD BASIC LOGGING:
       - Log data quality issues found
       - Log cleaning operations performed
       - Log final data summary

    4. EXAMPLE IMPLEMENTATION:
       df = access.data()
       if df is None:
           print("Error: No data available from access module")
           return None

       print(f"Assessing data quality for {len(df)} rows...")
       # Your data assessment code here
       return df
    """
    logger.info("Starting data assessment")

    # Load data from access module
    df = access.data()

    # Check if data was loaded successfully
    if df is None:
        logger.error("No data available from access module")
        print("Error: Could not load data from access module")
        return None

    logger.info(f"Assessing data quality for {len(df)} rows, {len(df.columns)} columns")

    try:
        # STUDENT IMPLEMENTATION: Add your data assessment code here

        # Example: Check for missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            logger.info(f"Found missing values: {missing_counts.to_dict()}")
            print(f"Missing values found: {missing_counts.sum()} total")

        # Example: Check data types
        logger.info(f"Data types: {df.dtypes.to_dict()}")

        # Example: Basic data cleaning (students should customize this)
        # Remove completely empty rows
        df_cleaned = df.dropna(how="all")
        if len(df_cleaned) < len(df):
            logger.info(f"Removed {len(df) - len(df_cleaned)} completely empty rows")

        logger.info(f"Data assessment completed. Final shape: {df_cleaned.shape}")
        return df_cleaned

    except Exception as e:
        logger.error(f"Error during data assessment: {e}")
        print(f"Error assessing data: {e}")
        return None

def epra_data():# -> Union[pd.DataFrame, Any]:
    '''returns epra_reliability_index_df '''
    return pd.read_csv('impact-of-planned-vs-unplanned-power-interruptions/data/formatted_epra_data.csv')
def census_kplc_data():    
    '''merged census_and_kplc_interruptions_data'''
    kplc_data = pd.read_csv('impact-of-planned-vs-unplanned-power-interruptions/data/census_and_kplc_interruptions_data.csv')
    kplc_data['electrified_households'] = round(kplc_data['Conventional Households']*kplc_data['Mains Electricity']/100.0).astype(int)
    return kplc_data
    
def query(data: Union[pd.DataFrame, Any]) -> str:
    """Request user input for some aspect of the data."""
    raise NotImplementedError


def view(data: Union[pd.DataFrame, Any]) -> None:
    """Provide a view of the data that allows the user to verify some aspect of its quality."""
    raise NotImplementedError


def labelled(data: Union[pd.DataFrame, Any]) -> Union[pd.DataFrame, Any]:
    """Provide a labelled set of data ready for supervised learning."""
    raise NotImplementedError


def get_box(
    latitude: float, longitude: float, box_size_km: Union[float, int] = 2
) -> Tuple[float, float, float, float]:
    """
    args:
        latitude in degrees
        longitude in degrees

    returns:
        bounding box coordinates (west, south, east, north) in degrees
    """
    lat_degree_km = 111.0
    lon_degree_km = 111.0 * math.cos(math.radians(latitude))
    box_height_deg = box_size_km / lat_degree_km
    box_width_deg = box_size_km / lon_degree_km
    north = latitude + box_height_deg / 2
    south = latitude - box_height_deg / 2
    east = longitude + box_width_deg / 2
    west = longitude - box_width_deg / 2
    bbox = (west, south, east, north)
    return bbox


def load_default_tags() -> Dict[str, Union[bool, str, list[str]]]:
    # Open the Defaults YAML file and load it
    defaults_file_path = os.path.join(os.path.dirname(__file__), "defaults.yml")
    print(defaults_file_path)
    with open(defaults_file_path, "r") as file:
        config = yaml.safe_load(file)

    # Access the DEFAULT_TAGS
    default_tags = cast(Dict[str, Union[bool, str, list[str]]], config["DEFAULT_TAGS"])
    return default_tags


def plot_city_map(
    place_name: str,
    latitude: float,
    longitude: float,
    box_size_km: Union[float, int] = 2,
    poi_tags: Optional[Dict[str, Union[bool, str, list[str]]]] = None,
) -> None:
    """
    show a matplotlib plot of features around place_name centered at (latitude, longitude), \
        with bounding box dimensions box_size_km*box_size_km
    args:
        place_name:str eg 'Nyeri, Kenya'
        latitude: latitude of place_name in degrees
        box_size_km: int/float:
        poi_tags: features to plot in the map
    returns: None
    """
    if not poi_tags:
        poi_tags = load_default_tags()
    # placestub = place_name.lower().replace(" ", "-").replace(",", "")
    bbox = get_box(latitude, longitude, box_size_km=box_size_km)
    west, south, east, north = bbox
    pois = ox.features_from_bbox(bbox, poi_tags)

    # Get graph from location
    graph = ox.graph_from_bbox(bbox)
    # City area
    area = ox.geocode_to_gdf(place_name)
    # Street network
    nodes, edges = ox.graph_to_gdfs(graph)
    # Buildings
    buildings = ox.features_from_bbox(bbox, tags={"building": True})

    fig, ax = plt.subplots(figsize=(6, 6))
    area.plot(ax=ax, color="tan", alpha=0.5)
    buildings.plot(ax=ax, facecolor="gray", edgecolor="gray")
    edges.plot(ax=ax, linewidth=1, edgecolor="black", alpha=0.3)
    nodes.plot(ax=ax, color="black", markersize=1, alpha=0.3)
    pois.plot(ax=ax, color="green", markersize=5, alpha=1)
    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_title(place_name, fontsize=14)
    plt.show()
