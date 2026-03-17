project = QgsProject.instance()

def add_google_maps():
    google_maps_url = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%25x%26y%3D%25y%26z%3D%25z&zmax=19&zmin=0"
    layer = QgsRasterLayer(google_maps_url, "Google Maps", "wms")
    if layer.isValid():
        project.addMapLayer(layer, False)
        root = project.layerTreeRoot()
        root.insertLayer(-1, layer)
        return "Google Maps added"
    return "Failed Google Maps"

def add_csv_layer(file_path, layer_name, shape_name, color_name):
    uri = f"file://{file_path}?type=csv&xField=longitude&yField=latitude&crs=epsg:4326"
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    if not layer.isValid():
        return f"Failed {layer_name}"

    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    if symbol:
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setShape(QgsSimpleMarkerSymbolLayerBase.decodeShape(shape_name))
        symbol_layer.setColor(QColor(color_name))
        symbol_layer.setSize(4.0)
        if shape_name == "triangle":
            symbol_layer.setStrokeColor(QColor("black"))
            
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)
    
    project.addMapLayer(layer)
    return f"Added {layer_name}"

results = []
# Remove existing OSM layers (optional, assuming user wants Google Maps instead)
for layer in list(project.mapLayers().values()):
    if 'OSM' in layer.name() or 'OpenStreetMap' in layer.name():
        project.removeMapLayer(layer.id())
        results.append(f"Removed {layer.name()}")

results.append(add_google_maps())

base_dir = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis/thesis_main/Scripts/Geocoding"

results.append(add_csv_layer(f"{base_dir}/geocoded_bdo_properties_cebu.csv", "BDO Foreclosed", "triangle", "red"))
results.append(add_csv_layer(f"{base_dir}/geocoded_leechiu_properties_final.csv", "Leechiu Properties", "circle", "blue"))

import glob
lifenavi_files = glob.glob(f"{base_dir}/geocoded_lifenavi_batch_*.csv")
for i, f in enumerate(lifenavi_files, 1):
    results.append(add_csv_layer(f, f"Lifenavi Properties ({i})", "circle", "green"))
    
print("\n".join(results))
