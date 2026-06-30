"""
build_qgis_project.py
=====================
Builds a QGIS project (.qgz) containing the three thesis maps as print layouts
(study area, listings, amenities), with all layers styled exactly like the
rendered PNGs and a CartoDB basemap. Each layout's map extent defaults to the
FULL six-LGU extent (nothing cropped) so the author can open the project in the
QGIS GUI, pan/zoom each map to taste, and export.

Open in QGIS: File > Open > scripts/qgis_project/metro_cebu_maps.qgz, then
Project > Layouts to pick a layout; select the map item and use the
"Move item content" tool to pan/zoom; Layout > Export as Image.

Run via the QGIS-bundled Python with the QGIS environment set.
"""

import os
import json
from collections import Counter

from qgis.core import (
    QgsApplication, QgsProject, QgsVectorLayer, QgsRasterLayer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsMarkerSymbol,
    QgsFillSymbol, QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsLayoutItemScaleBar, QgsLayoutItemPicture,
    QgsPrintLayout, QgsLayoutSize, QgsLayoutPoint, QgsUnitTypes, QgsRectangle,
)
from qgis.PyQt.QtGui import QColor, QFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "public", "data"))
PROJDIR = os.path.join(HERE, "qgis_project")
QGZ = os.path.join(PROJDIR, "metro_cebu_maps.qgz")

WEBMERC = "EPSG:3857"
BASE_URL = ("type=xyz&url=https://basemaps.cartocdn.com/light_all/"
            "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=20&zmin=0")

STRATA = [("Condominium", "Condominium", "#1f6fb2"), ("Houses", "Houses", "#e07b39"),
          ("Vacant Lot", "Vacant Lot", "#3a9a5c")]
AMENITY = [
    ("Education", "Education", "#1f77b4"), ("Grocery", "Grocery", "#ff7f0e"),
    ("Health", "Health", "#2ca02c"), ("Hospitals", "Hospitals", "#d62728"),
    ("Recreation", "Recreation", "#9467bd"), ("Retail", "Retail density", "#8c564b"),
    ("Security", "Security", "#e377c2"), ("Tourism", "Tourism", "#17becf"),
]
LGU_COLORS = {
    "Cebu City": "#9ecae1", "Mandaue City": "#bcbddc", "Lapu-Lapu City": "#fdae6b",
    "Talisay City": "#fff2ae", "Minglanilla": "#fbb4ae", "Consolacion": "#b3de69",
}


def points_geojson(src_name, out_name, prop_key):
    src = json.load(open(os.path.join(DATA, src_name)))
    feats = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
        "properties": {prop_key: r[prop_key]},
    } for r in src]
    path = os.path.join(PROJDIR, out_name)
    json.dump({"type": "FeatureCollection",
               "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
               "features": feats}, open(path, "w"))
    return path, Counter(r[prop_key] for r in src), len(feats)


def lgu_labels(layer, size):
    pal = QgsPalLayerSettings(); pal.fieldName = "lgu"; pal.enabled = True
    fmt = QgsTextFormat(); f = QFont("Helvetica", size); f.setBold(True)
    fmt.setFont(f); fmt.setSize(size); fmt.setColor(QColor("#222b33"))
    buf = QgsTextBufferSettings(); buf.setEnabled(True); buf.setSize(1.1)
    buf.setColor(QColor("white")); fmt.setBuffer(buf); pal.setFormat(fmt)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(pal)); layer.setLabelsEnabled(True)


def categorized(layer, field, entries, size, opacity, counts=None):
    cats = []
    for value, label, hexcol in entries:
        sym = QgsMarkerSymbol.createSimple({
            "name": "circle", "size": str(size), "color": hexcol,
            "outline_color": "white", "outline_width": "0.15"})
        sym.setOpacity(opacity)
        txt = f"{label} (n={counts.get(value, 0):,})" if counts else label
        cats.append(QgsRendererCategory(value, sym, txt))
    layer.setRenderer(QgsCategorizedSymbolRenderer(field, cats))


def north_svg():
    for root in QgsApplication.svgPaths():
        cand = os.path.join(root, "arrows", "NorthArrow_02.svg")
        if os.path.exists(cand):
            return cand
    return None


def add_layout(project, name, title_text, sub_text, layers, extent,
               legend_layer=None, legend_title=""):
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(name)
    PW, PH = 290, 250
    layout.pageCollection().pages()[0].setPageSize(
        QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))

    m = QgsLayoutItemMap(layout)
    m.attemptMove(QgsLayoutPoint(10, 24, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(PW - 20, PH - 34, QgsUnitTypes.LayoutMillimeters))
    m.setExtent(extent)
    m.setLayers(layers)
    m.setBackgroundColor(QColor("white"))
    m.setFrameEnabled(True); m.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(m)

    title = QgsLayoutItemLabel(layout); title.setText(title_text)
    tf = QFont("Helvetica", 20); tf.setBold(True); title.setFont(tf)
    title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(PW - 20, 11, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title)

    sub = QgsLayoutItemLabel(layout); sub.setText(sub_text)
    sf = QFont("Helvetica", 11); sub.setFont(sf); sub.setFontColor(QColor("#555555"))
    sub.attemptMove(QgsLayoutPoint(10, 16, QgsUnitTypes.LayoutMillimeters))
    sub.attemptResize(QgsLayoutSize(PW - 20, 7, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub)

    if legend_layer is not None:
        legend = QgsLayoutItemLegend(layout); legend.setTitle(legend_title)
        legend.setAutoUpdateModel(False)
        grp = legend.model().rootGroup(); grp.clear()
        node = grp.addLayer(legend_layer); node.setName("")
        legend.model().refreshLayerLegend(node)
        legend.setLegendFilterByMapEnabled(False)
        legend.attemptMove(QgsLayoutPoint(PW - 68, 30, QgsUnitTypes.LayoutMillimeters))
        legend.setBackgroundEnabled(True); legend.setBackgroundColor(QColor(255, 255, 255, 235))
        legend.setFrameEnabled(True); legend.setFrameStrokeColor(QColor("#9aa6b2"))
        layout.addLayoutItem(legend)

    sb = QgsLayoutItemScaleBar(layout); sb.setStyle("Single Box")
    sb.setLinkedMap(m); sb.setUnits(QgsUnitTypes.DistanceKilometers)
    sb.setUnitsPerSegment(2); sb.setNumberOfSegments(3); sb.setNumberOfSegmentsLeft(0)
    sb.setUnitLabel("km"); sb.setFont(QFont("Helvetica", 9))
    sb.setBackgroundEnabled(True); sb.setBackgroundColor(QColor(255, 255, 255, 220))
    sb.update()
    sb.attemptMove(QgsLayoutPoint(15, PH - 30, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sb)

    svg = north_svg()
    if svg:
        na = QgsLayoutItemPicture(layout); na.setPicturePath(svg)
        na.attemptMove(QgsLayoutPoint(PW - 26, PH - 32, QgsUnitTypes.LayoutMillimeters))
        na.attemptResize(QgsLayoutSize(14, 14, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(na)

    project.layoutManager().addLayout(layout)


def main():
    os.makedirs(PROJDIR, exist_ok=True)
    qgs = QgsApplication([], False); qgs.initQgis()
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem(WEBMERC))

    listings_path, strata_counts, n_listings = points_geojson(
        "listings.json", "listings_points.geojson", "stratum")
    amenity_path, amenity_counts, n_amenity = points_geojson(
        "pois.json", "amenity_points.geojson", "category")

    basemap = QgsRasterLayer(BASE_URL, "Carto Light", "wms")

    lgu_path = os.path.join(DATA, "lgu_boundaries.geojson")
    lgu_fill = QgsVectorLayer(lgu_path, "LGU (filled)", "ogr")
    lgu_line = QgsVectorLayer(lgu_path, "LGU (outline)", "ogr")
    listings = QgsVectorLayer(listings_path, "Listings", "ogr")
    amenities = QgsVectorLayer(amenity_path, "Amenities", "ogr")

    # styles
    fillcats = []
    for name, hexcol in LGU_COLORS.items():
        s = QgsFillSymbol.createSimple({"color": hexcol, "outline_color": "#4a5a68",
                                        "outline_width": "0.5"})
        s.setOpacity(0.55)
        fillcats.append(QgsRendererCategory(name, s, name))
    lgu_fill.setRenderer(QgsCategorizedSymbolRenderer("lgu", fillcats))
    lgu_fill.triggerRepaint()
    lgu_line.renderer().setSymbol(QgsFillSymbol.createSimple(
        {"color": "0,0,0,0", "outline_color": "#5a6b7b", "outline_width": "0.5"}))
    lgu_labels(lgu_fill, 13); lgu_labels(lgu_line, 11)
    categorized(listings, "stratum", STRATA, 1.8, 0.85)
    categorized(amenities, "category", AMENITY, 1.4, 0.80, amenity_counts)

    for lyr in (basemap, lgu_fill, lgu_line, listings, amenities):
        project.addMapLayer(lyr)

    # default extent = full LGU extent + margin (all six LGUs visible)
    full = QgsCoordinateTransform(lgu_fill.crs(), QgsCoordinateReferenceSystem(WEBMERC),
                                  project).transformBoundingBox(lgu_fill.extent())
    mx, my = full.width() * 0.04, full.height() * 0.06
    ext = QgsRectangle(full.xMinimum() - mx, full.yMinimum() - my,
                       full.xMaximum() + mx, full.yMaximum() + my)

    add_layout(project, "Map 1 - Study Area", "Metro Cebu Study Area",
               "The six local government units in the modeling scope",
               [lgu_fill, basemap], ext)
    add_layout(project, "Map 2 - Listings", "Open-Market Residential Listings Across Metro Cebu",
               f"{n_listings:,} modeled listings from three online portals, by deployed property stratum",
               [listings, lgu_line, basemap], ext,
               legend_layer=listings, legend_title="Property stratum")
    add_layout(project, "Map 3 - Amenities", "Curated Amenity Points Across Metro Cebu",
               f"{n_amenity:,} points across the eight MCRAI accessibility categories",
               [amenities, lgu_line, basemap], ext,
               legend_layer=amenities, legend_title="MCRAI amenity category")

    # the legend hidden-title trick blanks the node name; restore panel names
    listings.setName("Listings"); amenities.setName("Amenities")

    project.write(QGZ)
    print(f"saved project -> {QGZ}")
    print(f"layouts: {[l.name() for l in project.layoutManager().layouts()]}")
    qgs.exitQgis()


if __name__ == "__main__":
    main()
