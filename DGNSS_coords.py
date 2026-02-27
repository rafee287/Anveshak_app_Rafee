import pandas as pd

# 1. Load the data from CSV file
# Ensure your CSV file is named 'rover_data.csv' or change the path below
file_path = 'dgps_rover_data.csv'
df = pd.read_csv(file_path)

# 2. Set the Accurate Known Starting Position (Base Station)
# Replace these with the actual "Ground Truth" coordinates of your base station
base_lat_known = 12.990123
base_lon_known = 80.223452

# 3. Calculate Error at the Base for each point
# Error = Measured - Known (Calculating how much the satellite shifted)
df['Lat_Error'] = df['Base Latitude (Measured)'] - base_lat_known
df['Lon_Error'] = df['Base Longitude (Measured)'] - base_lon_known

# 4. Subtract Error from Rover measured positions
# Corrected = Measured - Error
df['Corrected_Lat'] = df['Rover Latitude (Measured)'] - df['Lat_Error']
df['Corrected_Lon'] = df['Rover Longitude (Measured)'] - df['Lon_Error']

# 5. Append results to the same CSV file
# This keeps your original data and adds the corrected columns at the end
df.to_csv(file_path, index=False)

print(f"Correction complete. Results appended to {file_path}")

# Optional: View the final 5 accurate points
print("\nFinal Corrected Points:")
print(df[['Corrected_Lat', 'Corrected_Lon']])