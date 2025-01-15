import requests
import pandas as pd
import streamlit as st
import time
import math
from datetime import datetime, timedelta




# Constants
API_KEY = "5a5dc4c0a633d9df1f1fd24f47b52ea0"
LOCATION = "Pen,IN"  # Replace with your city
URL = f"http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={API_KEY}"

# Constants for energy calculations
SOLAR_MAX_IRRADIANCE = 5  # kWh/m²/day
AIR_DENSITY = 1.225  # kg/m³
WATER_DENSITY = 1000  # kg/m³
GRAVITY = 9.81  # m/s²

# Function to fetch weather data
def fetch_weather_data():
    response = requests.get(URL)
    if response.status_code == 200:
        weather_data = response.json()
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cloud_cover": weather_data["clouds"]["all"],
            "wind_speed": weather_data["wind"]["speed"],
            "precipitation": 70, #weather_data.get("rain", {}).get("1h", 0),
            "temperature": weather_data["main"]["temp"] - 273.15  # Convert Kelvin to Celsius
        }
    else:
        st.error("Failed to fetch weather data. Please check the API key or city name.")
        return None

# Energy calculations
def calculate_solar_energy(area, efficiency, cloud_cover, performance_ratio):
    irradiance = SOLAR_MAX_IRRADIANCE * (1 - cloud_cover / 100)
    energy = area * efficiency * irradiance * performance_ratio
    return energy

def calculate_wind_energy(blade_radius, wind_speed, turbine_efficiency, hours):
    swept_area = math.pi * blade_radius**2
    power = 0.5 * AIR_DENSITY * swept_area * (wind_speed**3) * turbine_efficiency
    energy = power * hours / 1000  # Convert Watts to kWh
    return energy

def estimate_hydropower(flow_rate, head_height, efficiency=0.85):
    power = WATER_DENSITY * GRAVITY * flow_rate * head_height * efficiency  # Power in Watts
    return power / 1000  # Convert to kW

def calculate_flow_rate(precipitation, catchment_area, runoff_coefficient=0.8):
    catchment_area_m2 = catchment_area * 1e6  # km² to m²
    precipitation_m = precipitation / 1000  # mm to m
    flow_volume_m3_per_hour = precipitation_m * catchment_area_m2 * runoff_coefficient
    return flow_volume_m3_per_hour / 3600  # Convert to m³/s

# Initialize an empty DataFrame for storing weather and energy data
if "weather_df" not in st.session_state:
    st.session_state.weather_df = pd.DataFrame(columns=["Timestamp", "Cloud Cover (%)", "Wind Speed (m/s)", 
                                                       "Precipitation (mm)", "Temperature (°C)", 
                                                       "Solar Energy (kWh)", "Wind Energy (kWh)", 
                                                       "Hydropower (kW)", "Energy Demand (kWh)", 
                                                       "Net Energy (kWh)"])

# Initialize last update timestamp if not already
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()  # Start the first update

# Streamlit application layout
st.set_page_config(
    page_title="Weather and Energy Data Fetcher",
    page_icon="🌤️",
    layout="wide"
)

# st.sidebar.image(r"C:\Users\Anii\OneDrive\Desktop\JSW\JSW-Project\jsw energy logo.png", use_container_width=True)

# Sidebar for navigation between apps
st.sidebar.image(r"jsw energy logo.png", use_container_width=True)
st.sidebar.title("Navigation")
app_options = ["Main Application", "App", "AppAPI","Data2"]
selected_app = st.sidebar.selectbox("Choose Application", app_options)

def display_links():
    st.markdown("""
        <a href="http://localhost:8501" target="" style="display:inline-block; margin-right: 10px;">Go to Manual Input</a>
        <a href="http://localhost:8502" target="" style="display:inline-block; margin-right: 10px;">Go to API data</a>
        <a href="http://localhost:8503" target="" style="display:inline-block;">Go to Prediction Model</a>
    """, unsafe_allow_html=True)
    
# display_links()

st.title("Weather and Energy Data Fetcher")
st.write("This app fetches weather and energy data every 5 seconds.")

# Energy parameters
solar_area = 5000  # m²
solar_efficiency = 0.18  # 18%
performance_ratio = 0.85  # System efficiency
blade_radius = 45  # meters
turbine_efficiency = 0.3  # 30%
catchment_area = 2  # km²
head_height = 20  # meters
runoff_coefficient = 0.85  # Adjust based on terrain

# Energy demand input field
energy_demand_input = st.number_input("Enter Energy Demand (kWh):", value=0, step=1)

if energy_demand_input < 0:
    st.error("Energy demand cannot be negative. Please enter a positive value.")
    st.session_state.energy_demand = 0  # Reset to 0 or a default positive value
else:
    st.session_state.energy_demand = energy_demand_input

# Store the energy demand input to session state
if "energy_demand" not in st.session_state:
    st.session_state.energy_demand = energy_demand_input
else:
    st.session_state.energy_demand = energy_demand_input

# Function to compute energy demand
def calculate_energy_demand(temperature, wind_speed, input_demand):
    return input_demand  # Directly use the input value for energy demand

# Function to perform the fetch and update
def update_data():
    new_data = fetch_weather_data()
    if new_data:
        # Energy Generation Calculations
        solar_energy = calculate_solar_energy(solar_area, solar_efficiency, 
                                               new_data["cloud_cover"], performance_ratio)
        wind_energy = calculate_wind_energy(blade_radius, new_data["wind_speed"], 
                                             turbine_efficiency, 24)  # 24 hours
        flow_rate = calculate_flow_rate(new_data["precipitation"], catchment_area, runoff_coefficient)
        hydropower = estimate_hydropower(flow_rate, head_height)

        # Energy demand is now taken from session state (user input)
        energy_demand = calculate_energy_demand(new_data["temperature"], new_data["wind_speed"], st.session_state.energy_demand)

        # Net energy calculation
        total_energy_generated = solar_energy + wind_energy + hydropower
        net_energy = total_energy_generated - energy_demand

        # Create new row of data
        weather_row = {
            "Timestamp": new_data["timestamp"],
            "Cloud Cover (%)": new_data["cloud_cover"],
            "Wind Speed (m/s)": new_data["wind_speed"],
            "Precipitation (mm)": new_data["precipitation"],
            "Temperature (°C)": new_data["temperature"],
            "Solar Energy (kWh)": solar_energy,
            "Wind Energy (kWh)": wind_energy,
            "Hydropower (kW)": hydropower,
            "Energy Demand (kWh)": energy_demand,
            "Net Energy (kWh)": net_energy
        }

        # Append the new row to the existing DataFrame
        st.session_state.weather_df = pd.concat([st.session_state.weather_df, pd.DataFrame([weather_row])], ignore_index=True)

        # Display the updated DataFrame
        st.write(st.session_state.weather_df)

        # Create a CSV download link with a unique key
        csv = st.session_state.weather_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='weather_energy_data.csv',
            mime='text/csv',
            key=f'download_csv_button_{new_data["timestamp"]}'  # Unique key based on timestamp
        )

# Calculate the time difference in seconds
time_diff = datetime.now() - st.session_state.last_update

# Display the live countdown
counter_placeholder = st.empty()
while time_diff.total_seconds() < 5:
    counter_placeholder.markdown(f"Waiting for the next update. Time remaining: {5 - time_diff.total_seconds():.0f} seconds...")
    time.sleep(1)  # Delay for 1 second to update the counter
    time_diff = datetime.now() - st.session_state.last_update  # Update the time difference

# Once the countdown ends, update the data
update_data()
st.session_state.last_update = datetime.now()  # Update the last update time
