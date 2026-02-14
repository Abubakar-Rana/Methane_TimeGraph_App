import pystac_client
import requests
from shapely.geometry import box
import geopandas as gpd
import os
from datetime import datetime

# Define Lahore bbox
lahore_bbox = (74.1, 31.3, 74.5, 31.7)

# STAC API for Copernicus Dataspace
stac_url = "https://catalogue.dataspace.copernicus.eu/stac"

# Connect to STAC
client = pystac_client.Client.open(stac_url)

# List collections
collections = list(client.get_collections())
print("Available collections:")
for coll in collections:
    print(f" - {coll.id}")

# CH4 collection
ch4_collection_id = "sentinel-5p-l2-ch4-offl"

print(f"Using collection: {ch4_collection_id}")

# Query items with bbox and datetime
search = client.search(
    collections=[ch4_collection_id],
    bbox=lahore_bbox,
    datetime="2023-01-01T00:00:00Z/2025-12-31T23:59:59Z",
    limit=20  # Small limit for test
)

items = list(search.items())
print(f"Found {len(items)} items")

# Create data/spatial directory
os.makedirs('data/spatial', exist_ok=True)

# Download items
for item in items[:5]:  # Limit to 5 for test
    print(f"Item: {item.id}")
    print(f"Assets: {list(item.assets.keys())}")
    asset = item.assets.get('data') or item.assets.get('product')  # Try different keys
    if asset:
        href = asset.href
        filename = os.path.join('data/spatial', os.path.basename(href))
        print(f"Downloading {href} to {filename}")
        try:
            response = requests.get(href, timeout=60)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Failed to download {href}: {e}")
    else:
        print("No suitable asset found")

print("Download complete")