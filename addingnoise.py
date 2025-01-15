import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Constants for energy calculations
SOLAR_PANEL_EFFICIENCY = 0.18
WIND_TURBINE_EFFICIENCY = 0.35
WIND_TURBINE_AREA = 100  # m² (swept area of wind turbine)
GRAVITY = 9.81  # m/s²
WATER_DENSITY = 1000  # kg/m³
HYDRO_TURBINE_EFFICIENCY = 0.8
HEAD_HEIGHT = 50  # m (height difference for hydro energy)

# Define factors and variations
def time_of_day_factor(hour):
    if 0 <= hour < 6:
        return 0.5
    elif 6 <= hour < 12:
        return 0.8
    elif 12 <= hour < 18:
        return 1.2
    elif 18 <= hour <= 23:
        return 1.0

def seasonal_factor(month):
    if month in [12, 1, 2]:
        return 1.1
    elif month in [3, 4, 5]:
        return 0.9
    elif month in [6, 7, 8]:
        return 1.3
    elif month in [9, 10, 11]:
        return 1.0

def weather_variation():
    return round(np.random.uniform(0.9, 1.1), 2)

# Function to calculate energy generation
def calculate_solar_energy(irradiance, is_sunny):
    return round(irradiance * SOLAR_PANEL_EFFICIENCY * is_sunny * (15 / 60), 2)

def calculate_wind_energy(wind_speed, air_density):
    power = 0.5 * air_density * WIND_TURBINE_AREA * (wind_speed ** 3)
    return round(power * WIND_TURBINE_EFFICIENCY * (15 / 60) / 1000, 2)  # kWh

def calculate_hydro_energy(precipitation, runoff_coefficient):
    runoff_volume = precipitation * runoff_coefficient  # Simplified runoff volume
    energy = runoff_volume * WATER_DENSITY * GRAVITY * HEAD_HEIGHT * HYDRO_TURBINE_EFFICIENCY
    return round(energy / (3.6e6), 2)  # Convert J to kWh

# Function to generate weather data
def generate_indian_weather_data(timestamp):
    def cloud_cover():
        return round(np.random.uniform(0, 100), 1)

    def solar_irradiance(cloud_coverage):
        base_irradiance = np.random.uniform(800, 1000)  # Max on clear days
        reduction_factor = (100 - cloud_coverage) / 100
        return round(base_irradiance * reduction_factor, 1)

    def air_density(temperature):
        base_density = 1.225  # kg/m³ at sea level
        return round(base_density - 0.003 * (temperature - 15), 3)

    def precipitation(month):
        return round(np.random.uniform(0, 10), 1)  # Randomized precipitation

    def runoff_coefficient(precipitation):
        return round(0.05 + 0.005 * precipitation, 2)

    month = timestamp.month
    if month in [12, 1, 2]:  # Winter
        temperature = round(np.random.uniform(10, 25), 1)
    elif month in [3, 4, 5]:  # Spring
        temperature = round(np.random.uniform(20, 35), 1)
    elif month in [6, 7, 8]:  # Summer
        temperature = round(np.random.uniform(25, 40), 1)
    elif month in [9, 10, 11]:  # Autumn
        temperature = round(np.random.uniform(15, 30), 1)

    humidity = round(np.random.uniform(30, 70), 1)
    wind_speed = round(np.random.uniform(1, 10), 1)
    is_sunny = np.random.choice([1, 0], p=[0.5, 0.5])  # Equal probability
    cloud_coverage = cloud_cover()
    solar_irradiance_value = solar_irradiance(cloud_coverage)
    air_density_value = air_density(temperature)
    precipitation_value = precipitation(month)
    runoff_value = runoff_coefficient(precipitation_value)

    return temperature, humidity, wind_speed, is_sunny, cloud_coverage, solar_irradiance_value, air_density_value, precipitation_value, runoff_value

# Generate data with solar, wind, and hydro energy
data = []
current_time = datetime(2020, 1, 1, 0, 0)
end_date = datetime(2025, 12, 31, 23, 45)
interval = timedelta(minutes=15)

# Initialize cumulative energy variables
cumulative_energy_consumed = 0
cumulative_solar_energy = 0
cumulative_wind_energy = 0
cumulative_hydro_energy = 0

# Define base energy consumption per interval
interval_consumption = 5  # kWh (example value for 15-minute interval)

# Noise parameters
noise_std_dev = 2 # Standard deviation of noise for daily totals initially was 0.1

while current_time <= end_date:
    (temperature, humidity, wind_speed, is_sunny, cloud_coverage, solar_irradiance_value,
     air_density_value, precipitation_value, runoff_value) = generate_indian_weather_data(current_time)
    
    # Energy consumed
    hour = current_time.hour
    tod_factor = time_of_day_factor(hour)
    season_factor = seasonal_factor(current_time.month)
    weather_factor = weather_variation()
    energy_consumed = round(interval_consumption * tod_factor * season_factor * weather_factor, 2)
    
    # Update cumulative energy consumed
    cumulative_energy_consumed += energy_consumed
    
    # Energy generation
    solar_energy = calculate_solar_energy(solar_irradiance_value, is_sunny)
    wind_energy = calculate_wind_energy(wind_speed, air_density_value)
    hydro_energy = calculate_hydro_energy(precipitation_value, runoff_value)
    
    # Update cumulative energy generation
    cumulative_solar_energy += solar_energy
    cumulative_wind_energy += wind_energy
    cumulative_hydro_energy += hydro_energy
    
    # Add noise to daily totals
    if current_time.hour == 23 and current_time.minute == 45:
        # Add random noise to cumulative daily energy values
        cumulative_energy_consumed += np.random.normal(0, noise_std_dev)
        cumulative_solar_energy += np.random.normal(0, noise_std_dev)
        cumulative_wind_energy += np.random.normal(0, noise_std_dev)
        cumulative_hydro_energy += np.random.normal(0, noise_std_dev)
    
    # Append data
    data.append([current_time,
                 cumulative_energy_consumed,
                 temperature,
                 humidity,
                 wind_speed,
                 is_sunny,
                 cloud_coverage,
                 solar_irradiance_value,
                 air_density_value,
                 precipitation_value,
                 runoff_value,
                 round(cumulative_solar_energy, 2),
                 round(cumulative_wind_energy, 2),
                 round(cumulative_hydro_energy, 2)
                 ])
    
    # Reset at the end of the day
    if current_time.hour == 23 and current_time.minute == 45:
        cumulative_energy_consumed = 0
        cumulative_solar_energy = 0
        cumulative_wind_energy = 0
        cumulative_hydro_energy = 0
    
    current_time += interval

# Create DataFrame
columns = [
    "timestamp", "energy_consumed_kWh", "temperature_C", "humidity_%", "wind_speed_mps",
    "is_sunny", "cloud_cover_%", "solar_irradiance_Wm2", "air_density_kgm3",
    "precipitation_mm", "runoff_coefficient", "solar_energy_kWh",
    "wind_energy_kWh", "hydro_energy_kWh"
]
df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv("energy_data_with_noise.csv", index=False)
