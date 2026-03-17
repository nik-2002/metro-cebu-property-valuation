from qgis.core import *
import os
import sys

# Supply path to qgis install location
QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Write your code here to load some layers, use processing
# algorithms, etc.

project = QgsProject.instance()

# Google Maps Layer
urlWithParams = 'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%25x%26y%3D%25y%26z%3D%25z&zmax=19&zmin=0'
rlayer = QgsRasterLayer(urlWithParams, 'Google Maps', 'wms')

if rlayer.isValid():
    project.addMapLayer(rlayer)
    print("Google Maps layer added!")
else:
    print("Failed to add Google Maps layer")

def add_csv_layer(file_path, layer_name, shape_name, color_name, label_field=None):
    uri = f"file://{file_path}?type=csv&xField=longitude&yField=latitude&crs=epsg:4326"
    vlayer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    if not vlayer.isValid():
        print(f"Layer failed to load! {layer_name}")
        return

    # Basic symbol configuration
    # (Since we are running headless, full rendering setup might be skipped depending on the QGIS MCP server support, 
    # but we can set the symbol properties in the project)
    
    symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
    
    registry = QgsSymbolLayerRegistry()
    # "SimpleMarker" is the default for point geometries
    
    if symbol:
        symbol_layer = symbol.symbolLayer(0)
        if symbol_layer.layerType() == "SimpleMarker":
            symbol_layer.setShape(QgsSimpleMarkerSymbolLayerBase.decodeShape(shape_name))
            symbol_layer.setColor(QColor(color_name))
            symbol_layer.setSize(4.0)

    # Apply the symbol
    renderer = QgsSingleSymbolRenderer(symbol)
    vlayer.setRenderer(renderer)

    project.addMapLayer(vlayer)
    print(f"Added vector layer: {layer_name}")


base_dir = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis/thesis_main/Scripts/Geocoding"

add_csv_layer(os.path.join(base_dir, "geocoded_bdo_properties_cebu.csv"), "BDO Foreclosed", "triangle", "red", "Project Name")
add_csv_layer(os.path.join(base_dir, "geocoded_leechiu_properties_final.csv"), "Leechiu Properties", "circle", "blue")
add_csv_layer(os.path.join(base_dir, "geocoded_lifenavi_batch_1.csv"), "Lifenavi Properties (1)", "circle", "green")
add_csv_layer(os.path.join(base_dir, "geocoded_lifenavi_batch_2.csv"), "Lifenavi Properties (2)", "circle", "green")
add_csv_layer(os.path.join(base_dir, "geocoded_lifenavi_batch_3.csv"), "Lifenavi Properties (3)", "circle", "green")
add_csv_layer(os.path.join(base_dir, "geocoded_lifenavi_batch_4.csv"), "Lifenavi Properties (4)", "circle", "green")


# Save project
project.write('thesis_property_map.qgz')
print("Project saved to thesis_property_map.qgz")

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
