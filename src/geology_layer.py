"""
Sub-Surface Geological Proxy Layer: Sausar Group (Gondite Mineralized Belt)
Extracted from GSI Quadrangle Map Literature (55 O, 55 K, 64 C) for Nagpur-Bhandara-Balaghat.
Provides geological formation membership and boundary distance features as a proxy for ore-bearing host rock.
"""

import numpy as np
import pandas as pd

# Sausar Group Gondite Mineralized Belt Polygon Boundary Coordinates (WGS84 [lon, lat])
# ENE-WSW trending metamorphic fold belt housing pyrolusite/braunite gondite deposits
SAUSAR_GONDITE_POLYGON_COORDS = [
    [79.20, 21.32],
    [79.30, 21.42],
    [79.50, 21.55],
    [79.75, 21.65],
    [80.05, 21.78],
    [80.30, 21.92],
    [80.52, 22.02],
    [80.55, 21.80],
    [80.35, 21.65],
    [80.10, 21.50],
    [79.80, 21.35],
    [79.55, 21.22],
    [79.35, 21.12],
    [79.20, 21.32]
]

def is_point_in_polygon(lon, lat, polygon=SAUSAR_GONDITE_POLYGON_COORDS):
    """Ray-casting algorithm to test if (lon, lat) is inside polygon."""
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if lat > min(p1y, p2y):
            if lat <= max(p1y, p2y):
                if lon <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lon <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def min_distance_to_polygon_km(lon, lat, polygon=SAUSAR_GONDITE_POLYGON_COORDS):
    """Compute approximate minimum distance in km from (lon, lat) to polygon edges."""
    pts = np.array(polygon)
    # Convert lat/lon differences to approx km (1 deg lat ~ 111 km, 1 deg lon ~ 103 km at 21.5 N)
    d_lon = (pts[:, 0] - lon) * 103.0
    d_lat = (pts[:, 1] - lat) * 111.0
    dist_km = np.min(np.sqrt(d_lon**2 + d_lat**2))
    return float(dist_km)

def add_geology_features(df):
    """
    Add sub-surface proxy geological features to a DataFrame with 'lat' and 'lon' columns.
    Features added:
    - in_gondite_formation: 1 if inside Sausar Group Gondite belt, 0 otherwise
    - dist_to_gondite_km: distance in km to nearest Gondite formation boundary
    """
    df_out = df.copy()
    in_poly = []
    dist_km = []
    
    for idx, row in df_out.iterrows():
        inside = 1 if is_point_in_polygon(row["lon"], row["lat"]) else 0
        d_km = min_distance_to_polygon_km(row["lon"], row["lat"])
        in_poly.append(inside)
        dist_km.append(d_km)
        
    df_out["in_gondite_formation"] = in_poly
    df_out["dist_to_gondite_km"] = dist_km
    return df_out

def get_gondite_polygon_dict():
    """Return dict suitable for Plotly Scattermapbox polygon overlay."""
    lons = [p[0] for p in SAUSAR_GONDITE_POLYGON_COORDS]
    lats = [p[1] for p in SAUSAR_GONDITE_POLYGON_COORDS]
    return {"lons": lons, "lats": lats}
