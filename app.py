import streamlit as st
import math
import matplotlib.pyplot as plt

# Constants
SOLAR_MAX_IRRADIANCE = 1000  # W/m² (peak sun hours)
AIR_DENSITY = 1.225  # kg/m³ (standard air density)

# Functions
def calculate_solar_energy(area, efficiency, cloud_cover, performance_ratio):
    irradiance = SOLAR_MAX_IRRADIANCE * (1 - cloud_cover / 100)
    energy = area * efficiency * irradiance * performance_ratio
    return energy

def calculate_wind_energy(blade_radius, wind_speed, turbine_efficiency, hours):
    swept_area = math.pi * blade_radius**2
    power = 0.5 * AIR_DENSITY * swept_area * (wind_speed**3) * turbine_efficiency
    energy = power * hours / 1000  # Convert Watts to kWh
    return energy

def calculate_flow_rate(precipitation, catchment_area, runoff_coefficient=0.8):
    catchment_area_m2 = catchment_area * 1e6
    precipitation_m = precipitation / 1000
    flow_volume_m3_per_hour = precipitation_m * catchment_area_m2 * runoff_coefficient
    flow_rate = flow_volume_m3_per_hour / 3600  # Convert to m³/s
    return flow_rate

def estimate_hydropower(flow_rate, head_height, efficiency=0.85):
    density_water = 1000  # kg/m³ (density of water)
    g = 9.81  # m/s² (acceleration due to gravity)
    power = density_water * g * flow_rate * head_height * efficiency  # Power in Watts
    return power / 1000  # Convert to kW

# Streamlit App
# Sidebar for navigation between apps
st.sidebar.image(r"jsw energy logo.png", use_container_width=True)
st.sidebar.title("Navigation")
app_options = ["Main Application", "App", "AppAPI","Data2"]
selected_app = st.sidebar.selectbox("Choose Application", app_options)
st.title("⚡ Energy Generation and Demand Calculator")

# Sidebar inputs
st.sidebar.header("⚙️ Input Parameters")
solar_area = st.sidebar.number_input("Solar Panel Area (m²)", value=50)
solar_efficiency = st.sidebar.slider("Solar Panel Efficiency (%)", 10, 25, 18) / 100
performance_ratio = st.sidebar.slider("Performance Ratio", 0.5, 1.0, 0.85)
cloud_cover = st.sidebar.slider("Cloud Cover (%)", 0, 100, 50)

blade_radius = st.sidebar.number_input("Wind Turbine Blade Radius (m)", value=5)
wind_speed = st.sidebar.slider("Wind Speed (m/s)", 1, 25, 10)
turbine_efficiency = st.sidebar.slider("Wind Turbine Efficiency (%)", 20, 40, 30) / 100

precipitation = st.sidebar.slider("Precipitation (mm/hour)", 1, 100, 50)
catchment_area = st.sidebar.number_input("Catchment Area (km²)", value=2)
head_height = st.sidebar.number_input("Head Height (m)", value=20)
runoff_coefficient = st.sidebar.slider("Runoff Coefficient", 0.6, 0.9, 0.85)

energy_demand = st.number_input("Energy Demand (kWh)", value=200)

# Calculations
solar_energy = calculate_solar_energy(solar_area, solar_efficiency, cloud_cover, performance_ratio)
wind_energy = calculate_wind_energy(blade_radius, wind_speed, turbine_efficiency, 24)
flow_rate = calculate_flow_rate(precipitation, catchment_area, runoff_coefficient)
hydropower = estimate_hydropower(flow_rate, head_height)

total_energy_generated = solar_energy + wind_energy + hydropower
need_to_generate = max(0, energy_demand - total_energy_generated)

# Results Display
st.subheader("🌞 Energy Generation Results")
st.markdown(f"""
- **Solar Energy:** `{solar_energy:.2f} kWh/day`
- **Wind Energy:** `{wind_energy:.2f} kWh/day`
- **Hydropower:** `{hydropower:.2f} kWh/day`
- **Total Energy Generated:** `{total_energy_generated:.2f} kWh/day`
- **Energy Demand:** `{energy_demand:.2f} kWh`
- **Need to Generate:** `{need_to_generate:.2f} kWh`
""")

# Pie Chart
st.subheader("🔋 Energy Generation Distribution")
labels = ["Solar Energy", "Wind Energy", "Hydropower", "Need to Generate"]
values = [solar_energy, wind_energy, hydropower, need_to_generate]
colors = ["gold", "skyblue", "lightgreen", "red"]

# Enhanced pie chart with dark background
fig, ax = plt.subplots(figsize=(8, 8))
fig.patch.set_facecolor('#000000')  # Dark background for the figure
ax.set_facecolor('#1e1e2f')  # Dark background for the plot area

wedges, texts, autotexts = ax.pie(
    values, 
    labels=labels, 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=colors, 
    explode=[0.1, 0.1, 0.1, 0.1],
    textprops={'color': 'white', 'fontsize': 12}
)

# Customize text appearance
for text in texts:
    text.set_color('white')  # Labels in white
for autotext in autotexts:
    autotext.set_color('#ffffff')  # Percentages in light blue

ax.set_title(
    "Energy Generation vs. Demand", 
    fontsize=16, 
    fontweight='bold', 
    color='white'
)

# Display the chart in Streamlit
st.pyplot(fig)
