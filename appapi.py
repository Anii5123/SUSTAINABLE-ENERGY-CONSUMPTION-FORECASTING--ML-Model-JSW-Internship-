import streamlit as st
import requests
import math
import matplotlib.pyplot as plt
import os

# Sidebar for navigation between apps
# Sidebar for navigation between apps
st.sidebar.image(r"jsw energy logo.png", use_container_width=True)
st.sidebar.title("Navigation")
app_options = ["Main Application", "App", "AppAPI","Data2"]
selected_app = st.sidebar.selectbox("Choose Application", app_options)


# Constants
SOLAR_MAX_IRRADIANCE = 5  # kWh/m²/day (approx. for sunny areas in India)
AIR_DENSITY = 1.225  # kg/m³ (at sea level)
WATER_DENSITY = 1000  # kg/m³ (density of water)
GRAVITY = 9.81  # m/s² (acceleration due to gravity)
# API setup
API_KEY = "5a5dc4c0a633d9df1f1fd24f47b52ea0"
LOCATION = "Pen,IN"  # Replace with your city
URL = f"http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={API_KEY}"
# Fetch data from API
response = requests.get(URL)
weather_data = response.json()
# Check if the request was successful
if response.status_code == 200:
    st.title("🌤️ Weather & Renewable Energy Dashboard")
    st.success("Weather data fetched successfully!")
else:
    st.error("Failed to fetch weather data. Please check the API key or city name.")
    st.stop()
# Extract required values
cloud_cover = weather_data["clouds"]["all"]  # Cloud cover (%)
# Parameters for Solar, Wind, and Hydro Energy
solar_area = 5000  # m² (panel area)
solar_efficiency = 0.18  # 18%
performance_ratio = 0.85  # System efficiency
# Solar Energy Calculation
def calculate_solar_energy(area, efficiency, cloud_cover, performance_ratio):
    irradiance = SOLAR_MAX_IRRADIANCE * (1 - cloud_cover / 100)
    energy = area * efficiency * irradiance * performance_ratio
    return energy
solar_energy = calculate_solar_energy(solar_area, solar_efficiency, cloud_cover, performance_ratio)
# Wind Energy Calculation
def calculate_wind_energy(blade_radius, wind_speed, turbine_efficiency, hours):
    swept_area = math.pi * blade_radius**2
    power = 0.5 * AIR_DENSITY * swept_area * (wind_speed**3) * turbine_efficiency
    energy = power * hours / 1000  # Convert Watts to kWh
    return energy
wind_speed = weather_data["wind"]["speed"]  # Wind speed (m/s)
blade_radius = 45  # meters (turbine blade length)
turbine_efficiency = 0.3  # 30%
hours = 24  # Time in hours
wind_energy = calculate_wind_energy(blade_radius, wind_speed, turbine_efficiency, hours)
# Hydropower Calculation
def estimate_hydropower(flow_rate, head_height, efficiency=0.85):
    power = WATER_DENSITY * GRAVITY * flow_rate * head_height * efficiency  # Power in Watts
    return power / 1000  # Convert to kW
def calculate_flow_rate(precipitation, catchment_area, runoff_coefficient=0.8):
    catchment_area_m2 = catchment_area * 1e6
    precipitation_m = precipitation / 1000
    flow_volume_m3_per_hour = precipitation_m * catchment_area_m2 * runoff_coefficient
    return flow_volume_m3_per_hour / 3600  # Convert to m³/s
precipitation = 50  # mm/hour
catchment_area = 2  # km²
head_height = 20  # meters
runoff_coefficient = 0.85
flow_rate = calculate_flow_rate(precipitation, catchment_area, runoff_coefficient)
hydropower = estimate_hydropower(flow_rate, head_height)
# Styling the outputs
st.markdown("### 🌥️ **Weather Data**")
st.markdown(f"- **Cloud Cover**: **{cloud_cover}%**")
st.markdown(f"- **Wind Speed**: **{wind_speed} m/s**")
st.markdown(f"- **Precipitation**: **{precipitation} mm/hour**")
st.markdown("### 🔋 **Energy Generation**")
st.markdown(f"- **Solar Energy Generated**: **{solar_energy:.2f} kWh/day**")
st.markdown(f"- **Wind Energy Generated**: **{wind_energy:.2f} kWh/day**")
st.markdown(f"- **Hydropower Generated**: **{hydropower:.2f} kW**")
# User input for energy demand
st.markdown("### ⚡ **Energy Demand**")
energy_demand = st.number_input("Enter the energy demand (in kWh):", min_value=0.0, value=0.0)
total_energy_generated = solar_energy + wind_energy + hydropower
need_to_generate = max(0, energy_demand - total_energy_generated)
st.markdown(f"- **Total Energy Generated**: **{total_energy_generated:.2f} kWh/day**")
st.markdown(f"- **Energy Demand**: **{energy_demand:.2f} kWh/day**")
st.markdown(f"- **Remaining to Generate**: **{need_to_generate:.2f} kWh/day**")
# Create pie chart data
labels = ['Solar Energy', 'Wind Energy', 'Hydropower', 'Need to Generate']
values = [solar_energy, wind_energy, hydropower, need_to_generate]
colors = ['gold', 'skyblue', 'lightgreen', 'red']
explode = [0.1, 0.1, 0.1, 0.1]
# Enhanced pie chart with dark background
st.markdown("### 📊 **Energy Distribution**")
fig, ax = plt.subplots(figsize=(8, 8))
fig.patch.set_facecolor('#000000')  # Dark background for the figure
ax.set_facecolor('#1e1e2f')  # Dark background for the plot area
# Plot the pie chart
wedges, texts, autotexts = ax.pie(
    values, 
    labels=labels, 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=colors, 
    explode=explode,
    textprops={'color': 'white', 'fontsize': 12}
)
# Customize the appearance
for text in texts:
    text.set_color('white')  # Labels in white
for autotext in autotexts:
    autotext.set_color('#ffffff')  # Percentages in light blue for contrast
ax.set_title(
    'Energy Generation vs. Demand', 
    fontsize=16, 
    fontweight='bold', 
    color='white'
)
# Display the chart in Streamlit
st.pyplot(fig)


# Add a button to navigate to the selected application
if st.sidebar.button("Go to Selected App"):
    if selected_app == "Main Application":
        os.system("streamlit run main.py")  # Redirect to main.py
    elif selected_app == "App":
        os.system("streamlit run app.py")  # Redirect to app.py
    elif selected_app == "AppAPI":
        os.system("streamlit run appapi.py")

