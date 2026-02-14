import pandas as pd
import numpy as np
from datetime import datetime

# Generate sample daily methane data for Lahore, Pakistan (2023-2025)
# Typical CH4 values around 1800-2000 ppb, with some variation

start_date = '2023-01-01'
end_date = '2025-12-31'

dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Simulate methane values with seasonal variation and noise
# Base level around 1850 ppb, with annual cycle and random noise
base = 1850
annual_amplitude = 50
noise_std = 20

methane_values = []
for date in dates:
    day_of_year = date.dayofyear
    seasonal = annual_amplitude * np.sin(2 * np.pi * day_of_year / 365)
    noise = np.random.normal(0, noise_std)
    value = base + seasonal + noise
    methane_values.append(max(1700, min(2100, value)))  # clamp to reasonable range

# Create DataFrame
df = pd.DataFrame({
    'date': dates,
    'methane_ppb': methane_values
})

# Save to CSV in data directory
df.to_csv('data/lahore_methane_timeseries.csv', index=False)

print("Sample methane data saved to data/lahore_methane_timeseries.csv")
print(f"Generated {len(df)} daily records from {start_date} to {end_date}")