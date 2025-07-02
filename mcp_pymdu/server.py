"""
FastMCP PyMDU Example
"""

import io
import os
import sys
from functools import wraps
from io import StringIO

import dotenv
import httpx
from geopandas import GeoDataFrame
from matplotlib import pyplot as plt
from mcp.server.fastmcp.utilities.types import Image
import math
from mcp.server.fastmcp import FastMCP, Context
import asyncio
from serpapi import GoogleSearch

dotenv.load_dotenv()

# Create server
mcp = FastMCP("pymdu-server", dependencies=["pyautogui", "Pillow", "plotly"])


def _plot_to_image() -> Image:
    """Sauvegarde la figure matplotlib actuelle dans un objet Image."""
    # Sauvegarder en mémoire
    buffer = io.BytesIO()
    plt.tight_layout(pad=0)
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    buffer.seek(0)
    return Image(data=buffer.getvalue(), format="png")


def _create_figure(width: int, height: int):
    """Crée une figure et des axes matplotlib avec une taille spécifiée."""
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    return fig, ax


async def search_url_lcz(city: str) -> str:
    """
    Recherche url dataset pour les locate climate zone

    Arguments :
    ----------
    city : str
        Nom de la ville à rechercher.
    Retour :
       url : str
        Url du zip pour le datasest des LCZ de la ville recherchée
    -------
    """
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        _query = {
            "type": "main",
            "page_size": 10,
            "page": 1,
            "q": city,
            "lang": "fr",
        }
        _header = {
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36",
        }

        response = await client.get(
            "https://www.data.gouv.fr/api/2/datasets/6641c562e5acdb35c0e6051d/resources",
            params=_query,
            headers=_header,
            timeout=30.0,
        )
    response.raise_for_status()
    data = response.json()
    return data["data"][0]["url"]


def capture_stdout(func):
    """
    Décorateur pour capturer et supprimer la sortie standard (stdout) d'une fonction.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Capturer stdout pour éviter les interférences avec MCP
        old_stdout = sys.stdout
        sys.stdout = (
            StringIO()
        )  # Rediriger vers un buffer vide pour supprimer la sortie
        try:
            # Exécuter la fonction originale
            return func(*args, **kwargs)
        finally:
            # Restaurer stdout
            sys.stdout = old_stdout

    return wrapper


@mcp.tool()
async def get_bbox_area(
    lat: float, lon: float, bbox_area: int, ctx: Context
) -> list[float]:
    """
    Calcule la bounding-box carrée d'aire centrée sur (lat, lon).

    Arguments :
    ----------
    lat : float
        Latitude du point central en degrés décimaux.
    lon : float
        Longitude du point central en degrés décimaux.
    bbox_area : int
        Area bbox en km2.

    Retour :
    -------
    (min_lat, min_lon, max_lat, max_lon) : tuple de floats
        Coordonnées de la boîte : latitude minimale, longitude minimale,
        latitude maximale, longitude maximale.
    """
    await ctx.info(f"Processing {bbox_area}")
    # Rayon moyen de la Terre en km
    R = 6371.0

    # Demi-longueur de côté du carré en km (1 km² => côté = 1 km)
    half_side = bbox_area / 2  # km

    # Conversion de la latitude et longitude du centre en radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calcul des décalages en radians
    # Δφ = half_side / R
    delta_lat = half_side / R
    # Δλ = half_side / (R * cosφ)
    delta_lon = half_side / (R * math.cos(lat_rad))

    # Calcul des bornes en radians
    min_lat_rad = lat_rad - delta_lat
    max_lat_rad = lat_rad + delta_lat
    min_lon_rad = lon_rad - delta_lon
    max_lon_rad = lon_rad + delta_lon

    # Conversion en degrés
    min_lat = math.degrees(min_lat_rad)
    max_lat = math.degrees(max_lat_rad)
    min_lon = math.degrees(min_lon_rad)
    max_lon = math.degrees(max_lon_rad)

    return [min_lon, min_lat, max_lon, max_lat]


@capture_stdout
@mcp.tool()
def pymdu_building_to_image(
    bbox=None,
    width: int = 800,
    height: int = 600,
) -> str:
    """Convert a GeoDataFrame to an image visualization"""
    # Importer seulement quand nécessaire
    if bbox is None:
        bbox = [-1.152704, 46.181627, -1.139893, 46.18699]
    from pymdu.geometric import Building

    fig, ax = _create_figure(width, height)

    buildings = Building()
    buildings.bbox = bbox
    buildings = buildings.run()
    buildings_gdf = buildings.to_gdf()
    buildings_gdf.plot(
        ax=ax,
        edgecolor="black",
        column="hauteur",
        legend=True,
        legend_kwds={"label": "Hauteur", "orientation": "vertical"},
    )

    # Supprimer les axes pour une image plus propre
    ax.set_axis_off()

    return _plot_to_image_interactive(gdf=buildings_gdf)


def _plot_to_image_interactive(
    gdf: GeoDataFrame, column: str = None, color_map: dict = None, labels: dict = None
) -> str:
    """
    Convertit un GeoDataFrame en une carte interactive à l'aide de Plotly.
    Retourne le graphique sous forme de chaîne de caractères HTML.
    """
    # Importer seulement quand nécessaire
    import plotly.express as px

    # Plotly a besoin que le GDF soit dans le système de coordonnées WGS84 (EPSG:4326)
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Calculer le centre pour la vue initiale
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

    # Créer la carte choroplèthe sur un fond de carte Mapbox
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=column,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style="carto-positron",
        zoom=13,
        opacity=0.7,
        color_discrete_map=color_map,
        labels=labels,
        # hover_data={column: True},
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()
    # Renvoyer la figure sous forme de chaîne HTML pour l'intégration
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


@capture_stdout
@mcp.tool()
async def pymdu_lcz_to_image(
    bbox: list = [-1.152704, 46.181627, -1.139893, 46.18699],
    width: int = 800,
    height: int = 600,
    city: str = "la-rochelle",
) -> str:
    """Convert a GeoDataFrame to an image visualization"""
    # Importer seulement quand nécessaire
    from pymdu.geometric import Lcz

    fig, ax = _create_figure(width, height)

    lcz = Lcz()
    lcz.bbox = bbox
    zipfile_url: str = await search_url_lcz(city=city)

    lcz_gdf = lcz.run(zipfile_url=zipfile_url).to_gdf()
    table_color = lcz.table_color
    lcz_gdf.plot(ax=ax, edgecolor=None, color=lcz_gdf["color"])
    # patches = [
    #     mpatches.Patch(color=info[1], label=info[0]) for info in table_color.values()
    # ]
    # plt.legend(
    #     handles=patches,
    #     loc="upper right",
    #     title="LCZ Legend",
    #     bbox_to_anchor=(1.1, 1.0),
    # )
    # patches = [
    #     mpatches.Patch(color=info[1], label=info[0]) for info in table_color.values()
    # ]
    # plt.legend(
    #     handles=patches,
    #     loc="upper right",
    #     title="LCZ Legend",
    #     bbox_to_anchor=(1.1, 1.0),
    # )

    # Supprimer les axes pour une image plus propre
    ax.set_axis_off()

    color_map = {info[1]: info[0] for info in table_color.values()}
    lcz_gdf["categorie"] = lcz_gdf["color"].map(color_map)
    # Préparer le dictionnaire de couleurs pour Plotly {nom: couleur}
    category_to_color_map = {info[0]: info[1] for info in table_color.values()}
    labels = {"categorie": "Zone Climatique Locale (LCZ)"}
    return _plot_to_image_interactive(
        gdf=lcz_gdf, column="categorie", color_map=category_to_color_map, labels=labels
    )


@mcp.tool()
def take_screenshot() -> Image:
    """
    Take a screenshot of the user's screen and return it as an image. Use
    this tool anytime the user wants you to look at something they're doing.
    """
    import pyautogui

    buffer = io.BytesIO()

    # if the file exceeds ~1MB, it will be rejected by Claude
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    return Image(data=buffer.getvalue(), format="jpeg")


async def run_search(params):
    """Run SerpAPI search asynchronously"""
    try:

        result = await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def search_google(query: str):
    """
    Search on web with google
    """
    # Prepare search parameters
    params = {
        "api_key": os.environ.get("API_KEY"),
        "q": query,
        "hl": "fr",
        "gl": "fr",
        # "engine": "google",
    }

    search_results = await run_search(params)
    return search_results


if __name__ == "__main__":
    # import asyncio

    # Initialize and run the server
    # pymdu_lcz_to_image()
    mcp.run(transport="streamable-http")
    # mcp.run(transport="stdio")
    # async def _run():
    #     return await pymdu_lcz_to_image()
    #
    # asyncio.run(_run())
