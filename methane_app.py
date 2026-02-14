import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import mplcursors
import rasterio
from rasterio.plot import show
import cartopy.crs as ccrs
import cartopy.feature as cfeature

print("Starting methane app...")

# Load data from CSV
def load_data():
    # Handle PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        data_dir = sys._MEIPASS
    else:
        # Running in normal Python
        data_dir = os.path.dirname(__file__)
    
    csv_path = os.path.join(data_dir, 'data', 'lahore_methane_timeseries.csv')
    print(f"Looking for data at: {csv_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    print(f"Loaded {len(df)} data points")
    return df

class MethaneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Methane Hotspots Time Graph - Lahore, Pakistan")
        self.root.geometry("1000x700")

        # Load data
        try:
            self.df = load_data()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()
            return

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Time Series Tab
        self.ts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ts_frame, text="Time Series")

        # Map Tab
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Methane Map")

        # Setup tabs
        self.setup_time_series_tab()
        self.setup_map_tab()

    def setup_time_series_tab(self):
        # Frame for controls
        control_frame = ttk.Frame(self.ts_frame)
        control_frame.pack(pady=10)

        # Date range selection
        ttk.Label(control_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.start_date = tk.StringVar(value=self.df['date'].min().strftime('%Y-%m-%d'))
        ttk.Entry(control_frame, textvariable=self.start_date).grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="End Date:").grid(row=0, column=2, padx=5)
        self.end_date = tk.StringVar(value=self.df['date'].max().strftime('%Y-%m-%d'))
        ttk.Entry(control_frame, textvariable=self.end_date).grid(row=0, column=3, padx=5)

        # Methane range filter
        ttk.Label(control_frame, text="Min CH₄ (ppb):").grid(row=1, column=0, padx=5)
        self.ts_min_ch4 = tk.StringVar(value=str(self.df['methane_ppb'].min()))
        ttk.Entry(control_frame, textvariable=self.ts_min_ch4).grid(row=1, column=1, padx=5)

        ttk.Label(control_frame, text="Max CH₄ (ppb):").grid(row=1, column=2, padx=5)
        self.ts_max_ch4 = tk.StringVar(value=str(self.df['methane_ppb'].max()))
        ttk.Entry(control_frame, textvariable=self.ts_max_ch4).grid(row=1, column=3, padx=5)

        # Update button
        ttk.Button(control_frame, text="Update Graph", command=self.update_graph).grid(row=1, column=4, padx=10)

        # Create figure and canvas
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.ts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial plot
        self.update_graph()

    def update_graph(self):
        try:
            start = pd.to_datetime(self.start_date.get())
            end = pd.to_datetime(self.end_date.get())
            min_ch4 = float(self.ts_min_ch4.get())
            max_ch4 = float(self.ts_max_ch4.get())
            filtered_df = self.df[(self.df['date'] >= start) & (self.df['date'] <= end) & 
                                  (self.df['methane_ppb'] >= min_ch4) & (self.df['methane_ppb'] <= max_ch4)]

            self.ax.clear()
            line, = self.ax.plot(filtered_df['date'], filtered_df['methane_ppb'], marker='o', linewidth=2, color='red')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('CH₄ (ppb)')
            self.ax.set_title('Methane Concentration Time Series - Lahore, Pakistan')
            self.ax.grid(True)
            self.figure.autofmt_xdate()
            self.canvas.draw()

            # Add hover cursor
            cursor = mplcursors.cursor(line, hover=True)
            @cursor.connect("add")
            def on_add(sel):
                # Find the closest data point
                x_val = sel.target[0]
                y_val = sel.target[1]
                # Find index
                idx = (filtered_df['methane_ppb'] - y_val).abs().idxmin()
                date_str = filtered_df.loc[idx, 'date'].strftime('%Y-%m-%d')
                methane_val = filtered_df.loc[idx, 'methane_ppb']
                sel.annotation.set_text(f'Date: {date_str}\nMethane: {methane_val:.2f} ppb')

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input or error: {str(e)}")

    def setup_map_tab(self):
        # Frame for controls
        control_frame = ttk.Frame(self.map_frame)
        control_frame.pack(pady=10)

        # Year selection
        ttk.Label(control_frame, text="Select Year:").grid(row=0, column=0, padx=5)
        self.year_var = tk.StringVar(value="2023")
        year_combo = ttk.Combobox(control_frame, textvariable=self.year_var, values=["2023", "2024", "2025"])
        year_combo.grid(row=0, column=1, padx=5)
        year_combo.bind("<<ComboboxSelected>>", self.update_map)

        # Methane range
        ttk.Label(control_frame, text="Min CH₄ (ppb):").grid(row=1, column=0, padx=5)
        self.min_ch4 = tk.StringVar(value="1800")
        ttk.Entry(control_frame, textvariable=self.min_ch4).grid(row=1, column=1, padx=5)

        ttk.Label(control_frame, text="Max CH₄ (ppb):").grid(row=1, column=2, padx=5)
        self.max_ch4 = tk.StringVar(value="1950")
        ttk.Entry(control_frame, textvariable=self.max_ch4).grid(row=1, column=3, padx=5)

        # Update button
        ttk.Button(control_frame, text="Update Map", command=self.update_map).grid(row=1, column=4, padx=10)

        # Create figure with cartopy projection
        self.map_fig = plt.figure(figsize=(8, 6))
        self.map_ax = self.map_fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self.map_canvas = FigureCanvasTkAgg(self.map_fig, master=self.map_frame)
        self.map_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar for zoom/pan
        self.map_toolbar = NavigationToolbar2Tk(self.map_canvas, self.map_frame)
        self.map_toolbar.update()
        self.map_toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize colorbar
        self.cbar = None

        # Initial map
        self.update_map()

    def update_map(self, event=None):
        year = self.year_var.get()
        tif_path = os.path.join('data', f'methane_lahore_{year}.tif')
        
        # Handle PyInstaller
        if getattr(sys, 'frozen', False):
            tif_path = os.path.join(sys._MEIPASS, tif_path)
        
        try:
            vmin = float(self.min_ch4.get())
            vmax = float(self.max_ch4.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid methane range values")
            return
        
        if os.path.exists(tif_path):
            self.map_fig.clear()
            self.map_ax = self.map_fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            
            # Add base map features
            self.map_ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
            self.map_ax.add_feature(cfeature.BORDERS, linewidth=0.5)
            self.map_ax.add_feature(cfeature.LAND, facecolor='lightgray')
            self.map_ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
            self.map_ax.add_feature(cfeature.LAKES, facecolor='lightblue')
            self.map_ax.add_feature(cfeature.RIVERS, linewidth=0.5)
            
            with rasterio.open(tif_path) as src:
                data = src.read(1)
                bounds = src.bounds
                extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)
                im = self.map_ax.imshow(data, extent=extent, cmap='RdYlGn_r', vmin=vmin, vmax=vmax, origin='upper', transform=ccrs.PlateCarree())
                self.map_ax.set_title(f'Methane Heatmap - Lahore, {year}')
                self.map_ax.set_xlabel('Longitude')
                self.map_ax.set_ylabel('Latitude')
                # Add gridlines for navigation
                self.map_ax.gridlines(draw_labels=True, alpha=0.5)
                self.cbar = self.map_fig.colorbar(im, ax=self.map_ax, shrink=0.8, label='CH₄ (ppb)')
            self.map_canvas.draw()
        else:
            self.map_fig.clear()
            self.map_ax = self.map_fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            # Add base map features even for no data
            self.map_ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
            self.map_ax.add_feature(cfeature.BORDERS, linewidth=0.5)
            self.map_ax.add_feature(cfeature.LAND, facecolor='lightgray')
            self.map_ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
            self.map_ax.add_feature(cfeature.LAKES, facecolor='lightblue')
            self.map_ax.add_feature(cfeature.RIVERS, linewidth=0.5)
            self.map_ax.gridlines(draw_labels=True, alpha=0.5)
            self.map_ax.text(0.5, 0.5, f'Heatmap data for {year} not available.\nRun the notebook to extract data.',
                           ha='center', va='center', transform=self.map_ax.transAxes)
            self.map_ax.set_title(f'Methane Heatmap - Lahore, {year}')
            self.map_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = MethaneApp(root)
    root.mainloop()