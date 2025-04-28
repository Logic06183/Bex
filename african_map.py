import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.font_manager as fm
import matplotlib.patheffects as path_effects
import os
import requests
import zipfile
import io
from matplotlib.ticker import NullFormatter
from matplotlib.colors import ListedColormap

# Create a data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Path to save the downloaded file
zip_path = os.path.join(data_dir, 'ne_110m_admin_0_countries.zip')
shapefile_path = os.path.join(data_dir, 'ne_110m_admin_0_countries.shp')

# Alternative URL from the official Natural Earth site
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

# Download and extract the data if the shapefile doesn't exist
if not os.path.exists(shapefile_path):
    print(f"Downloading Natural Earth data...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Extract the ZIP file
    with zipfile.ZipFile(io.BytesIO(response.content)) as zipf:
        zipf.extractall(data_dir)
    print("Download and extraction complete.")

# Read the Natural Earth dataset for countries
world = gpd.read_file(shapefile_path)

# Print column names to debug
print("Dataset columns:", world.columns.tolist())

# Get all African countries first
if 'CONTINENT' in world.columns:
    africa = world[world['CONTINENT'] == 'Africa']
elif 'continent' in world.columns:
    africa = world[world['continent'] == 'Africa']
elif 'REGION_UN' in world.columns:
    africa = world[world['REGION_UN'] == 'Africa']
else:
    # Manual selection of African countries by ISO code
    african_iso_codes = ['DZA', 'AGO', 'BEN', 'BWA', 'BFA', 'BDI', 'CMR', 'CPV', 'CAF', 'TCD', 'COM', 
                         'COG', 'COD', 'DJI', 'EGY', 'GNQ', 'ERI', 'ETH', 'GAB', 'GMB', 'GHA', 'GIN', 
                         'GNB', 'CIV', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG', 'MWI', 'MLI', 'MRT', 'MUS', 
                         'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'RWA', 'STP', 'SEN', 'SYC', 'SLE', 'SOM', 
                         'ZAF', 'SSD', 'SDN', 'SWZ', 'TZA', 'TGO', 'TUN', 'UGA', 'ZMB', 'ZWE']
    if 'ISO_A3' in world.columns:
        africa = world[world['ISO_A3'].isin(african_iso_codes)]
    else:
        print("No suitable column found to identify African countries. Using all countries instead.")
        africa = world.copy()
        
# Now filter for Sub-Saharan Africa by removing North African countries
# North African countries ISO codes
north_african_iso = ['DZA', 'EGY', 'LBY', 'MAR', 'TUN']

# Filter out North African countries
if 'ISO_A3' in africa.columns:
    subsaharan_africa = africa[~africa['ISO_A3'].isin(north_african_iso)]
else:
    # If ISO_A3 doesn't exist, try using country names
    north_african_names = ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Tunisia']
    subsaharan_africa = africa[~africa['NAME'].isin(north_african_names)]

# Use Sub-Saharan Africa for the map
africa = subsaharan_africa

# Print unique country names to find the exact names in the dataset
print("\nCountry names in the dataset:")
print(sorted(africa['NAME'].unique().tolist()))

# Create a list of countries to highlight - using exact names from the dataset
# The NAME field might have slightly different naming conventions like 'Dem. Rep. Congo' instead of 'Democratic Republic of the Congo'
highlighted_countries_standard = ['Democratic Republic of the Congo', 'Kenya', 'South Africa', 'Somalia']

# Check for each variant of the country names
highlighted_countries_variants = {
    'Democratic Republic of the Congo': ['Democratic Republic of the Congo', 'Dem. Rep. Congo', 'Congo, Dem. Rep.', 'DRC', 'Congo, the Democratic Republic of the', 'Congo (Democratic Republic of the)'],
    'Kenya': ['Kenya', 'Republic of Kenya'],
    'South Africa': ['South Africa', 'Republic of South Africa', 'S. Africa'],
    'Somalia': ['Somalia', 'Federal Republic of Somalia']
}

# Function to check if a country is one of our highlighted countries
def is_highlighted_country(name):
    for target_country, variants in highlighted_countries_variants.items():
        if name in variants:
            return True
    return False

# Create a new column to mark which countries should be highlighted
africa['highlight'] = africa['NAME'].apply(is_highlighted_country)

# Print highlighted countries to verify
highlighted = africa[africa['highlight']]
print("\nHighlighted countries found in dataset:")
print(highlighted[['NAME', 'ISO_A3']].to_string())

# If any of our target countries are missing, we'll try finding them by ISO code
found_countries = set(highlighted['NAME'])
expected_countries = set(highlighted_countries_standard)

# Backup method: lookup by ISO code if names don't match
iso_codes_to_highlight = {
    'ZAF': 'South Africa',
    'KEN': 'Kenya', 
    'COD': 'Democratic Republic of the Congo',
    'SOM': 'Somalia'
}

# Add highlighting by ISO code as a backup
if 'ISO_A3' in africa.columns:
    # Mark countries as highlighted if their ISO code matches our targets
    africa['iso_highlight'] = africa['ISO_A3'].apply(lambda x: x in iso_codes_to_highlight)
    
    # Combine both methods
    africa['highlight'] = africa['highlight'] | africa['iso_highlight']
    
    # Print final highlighted countries
    print("\nFinal highlighted countries:")
    print(africa[africa['highlight']][['NAME', 'ISO_A3']].to_string())

# Create a more visually appealing color scheme
# Main countries in deep blue, others in a soft beige to create better contrast
africa['color'] = africa['highlight'].map({True: '#3a86ff', False: '#fffcf2'})

# Create a stronger border for highlighted countries
africa['edge_width'] = africa['highlight'].map({True: 1.5, False: 0.5})
africa['edge_color'] = africa['highlight'].map({True: '#053861', False: '#495057'})

# Set up the figure with a specific background color for a modern look
fig, ax = plt.subplots(figsize=(14, 16), facecolor='#f8f9fa')
ax.set_facecolor('#f8f9fa')  # Light gray background for the map area

# Plot the Sub-Saharan African countries with improved styling
# First plot the non-highlighted countries
africa[~africa['highlight']].plot(
    ax=ax, 
    color=africa[~africa['highlight']]['color'], 
    edgecolor=africa[~africa['highlight']]['edge_color'],
    linewidth=africa[~africa['highlight']]['edge_width'],
    alpha=0.8
)

# Then plot the highlighted countries on top for emphasis
africa[africa['highlight']].plot(
    ax=ax, 
    color=africa[africa['highlight']]['color'], 
    edgecolor=africa[africa['highlight']]['edge_color'],
    linewidth=africa[africa['highlight']]['edge_width'],
    alpha=1.0
)

# Add a light blue ocean background
ax.set_facecolor('#e9f5fa')  # Light blue for ocean areas

# Add country labels with improved styling
for idx, row in africa.iterrows():
    # Get the centroid of each country polygon for label placement
    centroid = row['geometry'].centroid
    
    # Different styling for highlighted vs. regular countries
    if row['highlight']:
        # Highlighted countries: white text with shadow effect and larger font
        fontcolor = 'white'
        fontsize = 10
        fontweight = 'bold'
    else:
        # Regular countries: dark gray text, smaller
        fontcolor = '#343a40'
        fontsize = 7
        fontweight = 'normal'
    
    # Add the country name as a text label
    ax.text(
        centroid.x, centroid.y, 
        row['NAME'], 
        fontsize=fontsize,
        color=fontcolor, 
        ha='center', 
        va='center', 
        fontweight=fontweight,
        path_effects=[path_effects.withStroke(linewidth=2, foreground='#33333322')]
    )

# Create a more elegant legend with custom styling
highlighted_patch = mpatches.Patch(color='#3a86ff', label='DRC, Kenya, South Africa, Somalia')
regular_patch = mpatches.Patch(color='#fffcf2', label='Other Sub-Saharan Countries')

legend = plt.legend(
    handles=[highlighted_patch, regular_patch], 
    loc='lower right',
    frameon=True,
    framealpha=0.9,
    edgecolor='#dddddd',
    facecolor='white',
    title='Country Classification'
)
legend.get_title().set_fontweight('bold')

# No title for academic report

# Remove axis
ax.set_axis_off()

# Display the map focused specifically on Sub-Saharan Africa (adjusted bounds)
ax.set_xlim(-18, 52)      # Longitude limits
ax.set_ylim(-35, 15)      # Latitude limits

# Add a subtle grid for reference
ax.grid(linestyle='--', alpha=0.3, color='gray')

# Add a scale bar (approximation for this projection)
scale_bar_length = 1000  # km
scale_x_start = 30
scale_y = -33
ax.plot([scale_x_start, scale_x_start + 10], [scale_y, scale_y], 'k-', linewidth=2)
ax.text(scale_x_start + 5, scale_y - 1, f'{scale_bar_length} km (approx.)', ha='center', fontsize=8)

# Add a border around the map
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('#cccccc')
    spine.set_linewidth(0.5)

plt.tight_layout()

# Display the map
plt.show()

# Save the map to a file with high resolution (academic style)
plt.savefig('subsaharan_africa_academic_map.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
