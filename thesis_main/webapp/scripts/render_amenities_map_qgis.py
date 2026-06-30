"""
render_amenities_map_qgis.py
============================
Renders a presentation-quality cartographic map of the curated amenity points
across Metro Cebu, colored by the eight MCRAI accessibility categories, using
headless PyQGIS over a light CartoDB basemap. Matches the styling of the
listings and study-area maps. Reads public/data/pois.json.

Improves the earlier plain matplotlib amenities map (diagrams/amenities_map.png,
"Map 3"). Run via the QGIS-bundled Python with the QGIS environment set.
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
    QgsPrintLayout, QgsLayoutSize, QgsLayoutPoint, QgsUnitTypes,
    QgsLayoutExporter, QgsRectangle,
)
from qgis.PyQt.QtGui import QColor, QFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "public", "data")
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "EDA", "plots", "amenities_map_qgis.png"))
TMP_GEOJSON = "/tmp/amenity_points.geojson"

WEBMERC = "EPSG:3857"

# user-selected map framing (EPSG:4326) captured from the QGIS canvas 2026-06-30;
# shared by all three Metro Cebu maps. xmin, ymin, xmax, ymax.
USER_BBOX = (123.71034639970264, 10.189215977449143,
             124.10600490419463, 10.501316464439972)

# data category value -> (display label, color). tab10-style qualitative palette.
CATEGORIES = [
    ("Education",   "Education",      "#1f77b4"),
    ("Grocery",     "Grocery",        "#ff7f0e"),
    ("Health",      "Health",         "#2ca02c"),
    ("Hospitals",   "Hospitals",      "#d62728"),
    ("Recreation",  "Recreation",     "#9467bd"),
    ("Retail",      "Retail density", "#8c564b"),
    ("Security",    "Security",       "#e377c2"),
    ("Tourism",     "Tourism",        "#17becf"),
]


def build_geojson():
    pois = json.load(open(os.path.join(DATA, "pois.json")))
    counts = Counter(r["category"] for r in pois)
    feats = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
        "properties": {"category": r["category"]},
    } for r in pois]
    json.dump({"type": "FeatureCollection",
               "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
               "features": feats}, open(TMP_GEOJSON, "w"))
    return len(feats), counts


def style_points(layer, counts):
    cats = []
    for value, label, hexcol in CATEGORIES:
        sym = QgsMarkerSymbol.createSimple({
            "name": "circle", "size": "1.4",
            "color": hexcol, "outline_color": "white", "outline_width": "0.1",
        })
        sym.setOpacity(0.80)
        cats.append(QgsRendererCategory(value, sym, f"{label} (n={counts.get(value, 0):,})"))
    layer.setRenderer(QgsCategorizedSymbolRenderer("category", cats))


def main():
    qgs = QgsApplication([], False)
    qgs.initQgis()
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem(WEBMERC))

    n, counts = build_geojson()

    base_url = ("type=xyz&url=https://basemaps.cartocdn.com/light_all/"
                "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=20&zmin=0")
    basemap = QgsRasterLayer(base_url, "Carto Light", "wms")
    lgu = QgsVectorLayer(os.path.join(DATA, "lgu_boundaries.geojson"), "LGU", "ogr")
    pts = QgsVectorLayer(TMP_GEOJSON, "Amenities", "ogr")
    assert lgu.isValid() and pts.isValid(), (lgu.isValid(), pts.isValid())

    # LGU outline only
    fill = QgsFillSymbol.createSimple({
        "color": "0,0,0,0", "outline_color": "#5a6b7b", "outline_width": "0.5"})
    lgu.renderer().setSymbol(fill)
    style_points(pts, counts)

    for lyr in (basemap, lgu, pts):
        if lyr.isValid():
            project.addMapLayer(lyr)

    # user-selected framing captured from the QGIS canvas (EPSG:4326): all six
    # LGUs in view with the eastern Olango islands cropped off.
    webmerc = QgsCoordinateReferenceSystem(WEBMERC)
    ll2wm = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), webmerc, project)
    ext = ll2wm.transformBoundingBox(QgsRectangle(*USER_BBOX))

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    page = layout.pageCollection().pages()[0]
    # size the map frame to the captured bbox aspect so nothing framed is cropped
    MAP_W, TOP, BOT = 270, 24, 14
    MAP_H = MAP_W * ext.height() / ext.width()
    PW, PH = MAP_W + 20, MAP_H + TOP + BOT
    page.setPageSize(QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))

    m = QgsLayoutItemMap(layout)
    m.attemptMove(QgsLayoutPoint(10, TOP, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(MAP_W, MAP_H, QgsUnitTypes.LayoutMillimeters))
    m.setExtent(ext)
    m.setLayers([pts, lgu, basemap])
    m.setBackgroundColor(QColor("white"))
    m.setFrameEnabled(True)
    m.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(m)

    title = QgsLayoutItemLabel(layout)
    title.setText("Curated Amenity Points Across Metro Cebu")
    tf = QFont("Helvetica", 20); tf.setBold(True)
    title.setFont(tf)
    title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(PW - 20, 11, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title)

    sub = QgsLayoutItemLabel(layout)
    sub.setText(f"{n:,} points across the eight MCRAI accessibility categories")
    sf = QFont("Helvetica", 11)
    sub.setFont(sf); sub.setFontColor(QColor("#555555"))
    sub.attemptMove(QgsLayoutPoint(10, 16, QgsUnitTypes.LayoutMillimeters))
    sub.attemptResize(QgsLayoutSize(PW - 20, 7, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub)

    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("MCRAI amenity category")
    legend.setAutoUpdateModel(False)
    grp = legend.model().rootGroup()
    grp.clear()
    node = grp.addLayer(pts)
    node.setName("")
    legend.model().refreshLayerLegend(node)
    legend.setLegendFilterByMapEnabled(False)
    legend.attemptMove(QgsLayoutPoint(PW - 68, 30, QgsUnitTypes.LayoutMillimeters))
    legend.setBackgroundEnabled(True)
    legend.setBackgroundColor(QColor(255, 255, 255, 235))
    legend.setFrameEnabled(True)
    legend.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(legend)

    sb = QgsLayoutItemScaleBar(layout)
    sb.setStyle("Single Box")
    sb.setLinkedMap(m)
    sb.setUnits(QgsUnitTypes.DistanceKilometers)
    sb.setUnitsPerSegment(2)
    sb.setNumberOfSegments(3)
    sb.setNumberOfSegmentsLeft(0)
    sb.setUnitLabel("km")
    sb.setFont(QFont("Helvetica", 9))
    sb.setBackgroundEnabled(True)
    sb.setBackgroundColor(QColor(255, 255, 255, 220))
    sb.update()
    sb.attemptMove(QgsLayoutPoint(15, PH - 30, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sb)

    na = QgsLayoutItemPicture(layout)
    found = None
    for root in QgsApplication.svgPaths():
        cand = os.path.join(root, "arrows", "NorthArrow_02.svg")
        if os.path.exists(cand):
            found = cand; break
    if found:
        na.setPicturePath(found)
        na.attemptMove(QgsLayoutPoint(PW - 26, PH - 32, QgsUnitTypes.LayoutMillimeters))
        na.attemptResize(QgsLayoutSize(14, 14, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(na)

    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = 150
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res = exporter.exportToImage(OUT, settings)
    print(f"export result={res}  ->  {OUT}  ({n:,} points)")

    qgs.exitQgis()


if __name__ == "__main__":
    main()
