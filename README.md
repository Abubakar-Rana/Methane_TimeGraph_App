# Offline Methane Hotspots App

A simple desktop app to visualize methane hotspots in Lahore, Pakistan, with time series graphs and geospatial heatmaps overlaid on a base map.

## Prerequisites
- Python 3.7 or higher
- Google Earth Engine account (for data extraction only)

## Easy Setup Steps

### Step 1: Get the Code
1. Open your terminal or command prompt.
2. Clone the repository:
   ```
   git clone <your-repository-url>
   ```
3. Go into the project folder:
   ```
   cd offline-methane-exe
   ```

### Step 2: Install Requirements
1. Make sure you have Python installed (check with `python --version`).
2. Install the needed libraries:
   ```
   pip install -r requirements.txt
   ```
   This installs: pandas, matplotlib, mplcursors, rasterio, cartopy.

### Step 3: Get the Data
1. Open the notebook file `Methane_Hotspots.ipynb` in VS Code or Jupyter Notebook.
2. Run all the cells in the notebook (it will ask for Google Earth Engine login once).
3. Wait for it to download the data files (this takes a few minutes).
4. Check that `data/` folder has the files: `lahore_methane_timeseries.csv` and `methane_lahore_2023.tif`, etc.

### Step 4: Run the App
1. In your terminal, run:
   ```
   python methane_app.py
   ```
2. The app window will open with two tabs: Time Series and Methane Map.

## What the App Does
- **Time Series Tab**: Shows a graph of methane levels over time with filters for date range and methane concentration. Hover over points to see exact values.
- **Map Tab**: Pick a year and see a heatmap of methane concentrations in Lahore overlaid on a geographical base map (coastlines, borders, land/ocean). Adjust methane concentration range for visualization. Use the navigation toolbar to zoom in/out, pan, and explore the map dynamically.

## Data Structure
The `data/` folder serves as the offline database:
- `lahore_methane_timeseries.csv`: Daily methane time series data
- `methane_lahore_2023.tif`, `methane_lahore_2024.tif`, `methane_lahore_2025.tif`: Spatial GeoTIFFs for each year

## User Actions and Filters
- **Time Series Filters**: Date range (start/end), methane concentration range (min/max)
- **Map Filters**: Year selection, methane concentration range (min/max for color scale)
- All data is loaded from local files for offline operation

## Troubleshooting
- If `pip install` fails, try `python -m pip install -r requirements.txt`.
- If the app doesn't start, make sure all requirements are installed.
- For data issues, re-run the notebook.

Enjoy exploring methane data!