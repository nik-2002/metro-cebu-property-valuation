import os
import glob
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsSymbol,
    QgsSingleSymbolRenderer,
    QgsPalLayerSettings,
    QgsTextFormat,
    QgsVectorLayerSimpleLabeling
)

def add_google_maps():
    google_maps_url = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26x%3D%25x%26y%3D%25y%26z%3D%25z&zmax=19&zmin=0"
    layer = QgsRasterLayer(google_maps_url, "Google Maps", "wms")
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer, False)
        # Add to the bottom of the layer tree
        root = QgsProject.instance().layerTreeRoot()
        root.insertLayer(-1, layer)
        print("Google Maps layer added successfully.")
    else:
        print("Failed to add Google Maps layer.")

def add_csv_layer(file_path, layer_name, shape_name, color_hex, label_field=None):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    uri = f"file://{file_path}?type=csv&xField=longitude&yField=latitude&crs=epsg:4326"
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    
    if not layer.isValid():
        print(f"Failed to load layer: {layer_name}")
        return

    # Set Symbol
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    
    # Try setting shape (marker type)
    if "marker" in symbol.symbolLayer(0).layerType().lower():
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setShape(shape_name)
        symbol_layer.setSize(4)
        symbol_layer.setColor(QColor(color_hex))
        symbol_layer.setStrokeColor(QColor("black"))
    
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)

    # Set Labels if requested
    if label_field:
        settings = QgsPalLayerSettings()
        settings.fieldName = label_field
        settings.isExpression = False
        settings.placement = QgsPalLayerSettings.AroundPoint
        settings.enabled = True
        
        text_format = QgsTextFormat()
        text_format.setFontTitle("Arial")
        text_format.setSize(10)
        settings.setFormat(text_format)
        
        labeling = QgsVectorLayerSimpleLabeling(settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)

    QgsProject.instance().addMapLayer(layer)
    print(f"Successfully added layer: {layer_name}")

def main():
    from PyQt5.QtGui import QColor

    # Base Path
    base_dir = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis/thesis_main/Scripts/Geocoding"

    # 1. Add Google Maps Layer
    add_google_maps()

    # 2. Add Leechiu Properties
    add_csv_layer(
        os.path.join(base_dir, "geocoded_leechiu_properties_final.csv"),
        "Leechiu Properties",
        "circle",
        "#1f78b4"  # Blue
    )

    # 3. Add Lifenavi Properties (combine batches or just load available)
    lifenavi_files = glob.glob(os.path.join(base_dir, "geocoded_lifenavi_batch_*.csv"))
    for i, file_path in enumerate(lifenavi_files, 1):
        add_csv_layer(
            file_path,
            f"Lifenavi Properties (Batch {i})",
            "circle",
            "#33a02c"  # Green
        )
    
    # Add initial just in case
    initial_path = os.path.join(base_dir, "geocoded_lifenavi_properties_initial.csv")
    if os.path.exists(initial_path):
             add_csv_layer(
            initial_path,
            "Lifenavi Properties (Initial)",
            "circle",
            "#33a02c"  # Green
        )

    # 4. Add BDO Properties
    add_csv_layer(
        os.path.join(base_dir, "geocoded_bdo_properties_cebu.csv"),
        "BDO Foreclosed Properties",
        "triangle",
        "#e31a1c",  # Red
        label_field="Project Name"
    )

main()
