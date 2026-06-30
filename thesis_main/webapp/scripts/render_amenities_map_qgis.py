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

    # frame to the amenity-point extent, then clamp east edge to drop Olango
    webmerc = QgsCoordinateReferenceSystem(WEBMERC)
    xform = QgsCoordinateTransform(pts.crs(), webmerc, project)
    ext = xform.transformBoundingBox(pts.extent())
    listings = json.load(open(os.path.join(DATA, "listings.json")))
    max_lon = max(r["longitude"] for r in listings)
    ll = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), webmerc, project)
    east_cap = ll.transform(max_lon, sum(r["latitude"] for r in listings) / len(listings)).x()
    mx, my = ext.width() * 0.04, ext.height() * 0.06
    ext = QgsRectangle(ext.xMinimum() - mx, ext.yMinimum() - my,
                       east_cap + ext.width() * 0.04, ext.yMaximum() + my)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    page = layout.pageCollection().pages()[0]
    PW, PH = 290, 250
    page.setPageSize(QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))

    m = QgsLayoutItemMap(layout)
    m.attemptMove(QgsLayoutPoint(10, 24, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(PW - 20, PH - 34, QgsUnitTypes.LayoutMillimeters))
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
