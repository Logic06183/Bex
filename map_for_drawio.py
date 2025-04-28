import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import requests
import zipfile
import io

# Create a data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Path to save the downloaded file
shapefile_path = os.path.join(data_dir, 'ne_110m_admin_0_countries.shp')

# Check if the shapefile already exists (reuse if available)
if not os.path.exists(shapefile_path):
    # URL from the official Natural Earth site
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    
    print(f"Downloading Natural Earth data...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Extract the ZIP file
    with zipfile.ZipFile(io.BytesIO(response.content)) as zipf:
        zipf.extractall(data_dir)
    print("Download and extraction complete.")

# Read the Natural Earth dataset for countries
world = gpd.read_file(shapefile_path)

# Get all African countries
if 'CONTINENT' in world.columns:
    africa = world[world['CONTINENT'] == 'Africa']
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
        africa = world.copy()  # Fallback just in case

# Filter for Sub-Saharan Africa by removing North African countries
north_african_iso = ['DZA', 'EGY', 'LBY', 'MAR', 'TUN']
if 'ISO_A3' in africa.columns:
    subsaharan_africa = africa[~africa['ISO_A3'].isin(north_african_iso)]
else:
    north_african_names = ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Tunisia']
    subsaharan_africa = africa[~africa['NAME'].isin(north_african_names)]

# Use Sub-Saharan Africa for the map
africa = subsaharan_africa

# Create the figure with a clean white background
fig, ax = plt.subplots(figsize=(14, 16), facecolor='white')
ax.set_facecolor('white')

# Plot all countries with a uniform color for Draw.io base map
africa.plot(
    ax=ax, 
    color='#f2f2f2',      # Light gray for all countries 
    edgecolor='#999999',  # Medium gray borders
    linewidth=0.5         # Thin borders
)

# Remove axis and grid
ax.set_axis_off()

# Focus on Sub-Saharan Africa
ax.set_xlim(-18, 52)
ax.set_ylim(-35, 15)

# Save a clean map for Draw.io
plt.savefig('subsaharan_africa_base.png', dpi=300, bbox_inches='tight', transparent=True)
print("Base map saved as 'subsaharan_africa_base.png'")

# Create a second map that highlights our countries of interest
# Focus countries
focus_countries = {
    'COD': 'Democratic Republic of the Congo', 
    'KEN': 'Kenya',
    'ZAF': 'South Africa',
    'SOM': 'Somalia'
}

# Create a new column to identify focus countries
africa['focus'] = africa['ISO_A3'].apply(lambda x: x in focus_countries.keys())

# Different shades of blue for each country
colors = {
    'COD': '#1e3799',  # DRC - Deep blue
    'SOM': '#3867d6',  # Somalia - Medium blue
    'KEN': '#4b7bec',  # Kenya - Bright blue
    'ZAF': '#0abde3',  # South Africa - Light blue
    'other': '#f2f2f2'  # Other countries - Light gray
}

# Create a color column
africa['color'] = africa['ISO_A3'].apply(lambda x: colors.get(x, colors['other']))

# Create a new figure
fig2, ax2 = plt.subplots(figsize=(14, 16), facecolor='white')

# Plot background countries
africa[~africa['focus']].plot(
    ax=ax2,
    color=colors['other'],
    edgecolor='#999999',
    linewidth=0.5
)

# Plot each focus country separately with its unique color
for iso, country in focus_countries.items():
    country_data = africa[africa['ISO_A3'] == iso]
    if not country_data.empty:
        country_data.plot(
            ax=ax2,
            color=colors[iso],
            edgecolor='#333333',
            linewidth=1.0
        )
        
        # Add country label at centroid
        centroid = country_data.iloc[0]['geometry'].centroid
        ax2.text(
            centroid.x, centroid.y,
            country_data.iloc[0]['NAME'],
            fontsize=10,
            ha='center',
            va='center',
            color='black',
            fontweight='bold'
        )

# Remove axis
ax2.set_axis_off()

# Focus on Sub-Saharan Africa
ax2.set_xlim(-18, 52)
ax2.set_ylim(-35, 15)

# Create a legend
patches = [mpatches.Patch(color=colors[iso], label=country) for iso, country in focus_countries.items()]
legend = plt.legend(
    handles=patches,
    loc='lower right',
    frameon=True,
    framealpha=0.9,
    title='Countries of Interest'
)

# Save highlighted map
plt.savefig('subsaharan_africa_highlighted.png', dpi=300, bbox_inches='tight')
print("Highlighted map saved as 'subsaharan_africa_highlighted.png'")

# Now create a DrawIO XML file that incorporates the map and adds the migration arrows
def create_drawio_file():
    """Creates a basic Draw.io file with the map as background and migration arrows"""
    
    drawio_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-04-28T12:00:00.000Z" agent="Mozilla/5.0" version="15.8.3" etag="abc123" type="device">
  <diagram id="migration-map" name="Migration Map">
    <mxGraphModel dx="1422" dy="1598" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="1654" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Background Map Image -->
        <mxCell id="2" value="" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;verticalAlign=top;aspect=fixed;imageAspect=0;image=subsaharan_africa_highlighted.png;" vertex="1" parent="1">
          <mxGeometry x="50" y="50" width="1000" height="1000" as="geometry" />
        </mxCell>
        
        <!-- Migration Arrows -->
        <!-- DRC to Kenya -->
        <mxCell id="3" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;startArrow=none;startFill=0;endArrow=classic;endFill=1;strokeWidth=3;strokeColor=#1e3799;curved=1;" edge="1" parent="1" source="drc_center" target="kenya_center">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- DRC to South Africa -->
        <mxCell id="4" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;startArrow=none;startFill=0;endArrow=classic;endFill=1;strokeWidth=3;strokeColor=#1e3799;curved=1;" edge="1" parent="1" source="drc_center" target="sa_center">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Somalia to Kenya -->
        <mxCell id="5" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.5;entryX=1;entryY=0.5;startArrow=none;startFill=0;endArrow=classic;endFill=1;strokeWidth=3;strokeColor=#3867d6;curved=1;" edge="1" parent="1" source="somalia_center" target="kenya_center">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Somalia to South Africa -->
        <mxCell id="6" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;startArrow=none;startFill=0;endArrow=classic;endFill=1;strokeWidth=3;strokeColor=#3867d6;curved=1;" edge="1" parent="1" source="somalia_center" target="sa_center">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <!-- Hidden reference points for countries -->
        <mxCell id="drc_center" value="" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=none;strokeColor=none;" vertex="1" parent="1">
          <mxGeometry x="400" y="370" width="10" height="10" as="geometry" />
        </mxCell>
        
        <mxCell id="kenya_center" value="" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=none;strokeColor=none;" vertex="1" parent="1">
          <mxGeometry x="580" y="380" width="10" height="10" as="geometry" />
        </mxCell>
        
        <mxCell id="somalia_center" value="" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=none;strokeColor=none;" vertex="1" parent="1">
          <mxGeometry x="650" y="350" width="10" height="10" as="geometry" />
        </mxCell>
        
        <mxCell id="sa_center" value="" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=none;strokeColor=none;" vertex="1" parent="1">
          <mxGeometry x="530" y="650" width="10" height="10" as="geometry" />
        </mxCell>
        
        <!-- Legend -->
        <mxCell id="7" value="Migration Flows" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="800" y="600" width="100" height="20" as="geometry" />
        </mxCell>
        
        <mxCell id="8" value="" style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#1e3799;" edge="1" parent="1">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="800" y="640" as="sourcePoint" />
            <mxPoint x="850" y="640" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        
        <mxCell id="9" value="DRC Migration" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
          <mxGeometry x="860" y="630" width="100" height="20" as="geometry" />
        </mxCell>
        
        <mxCell id="10" value="" style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#3867d6;" edge="1" parent="1">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="800" y="670" as="sourcePoint" />
            <mxPoint x="850" y="670" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        
        <mxCell id="11" value="Somalia Migration" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
          <mxGeometry x="860" y="660" width="120" height="20" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    # Write the XML file
    with open('migration_flows.drawio', 'w') as f:
        f.write(drawio_xml)
    
    print("Draw.io file created as 'migration_flows.drawio'")

# Create the Draw.io file
create_drawio_file()
