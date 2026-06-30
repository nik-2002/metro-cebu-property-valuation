"""
render_listings_map_qgis.py
===========================
Renders a presentation-quality cartographic map of the open-market residential
listings across Metro Cebu using headless PyQGIS: a light CartoDB basemap for
geographic context, LGU boundaries with labels, and listings categorized by
deployed stratum, exported through a print layout (title, legend, scale bar,
north arrow) to a high-DPI PNG.

Run via the QGIS-bundled Python with the QGIS environment set (see the wrapper
in the calling shell command). Reads the static web-app data in public/data/.
"""

import os
import json

from qgis.core import (
    QgsApplication, QgsProject, QgsVectorLayer, QgsRasterLayer,
    QgsCoordinateReferenceSystem, QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsLayoutItemScaleBar, QgsLayoutItemPicture,
    QgsPrintLayout, QgsLayoutSize, QgsLayoutPoint, QgsUnitTypes,
    QgsLayoutExporter, QgsRectangle, QgsLayerTreeGroup, QgsLayoutItemPolygon,
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QSizeF, QPointF

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "public", "data")
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "EDA", "plots", "webapp_market_map_qgis.png"))
TMP_GEOJSON = "/tmp/listings_points.geojson"

WEBMERC = "EPSG:3857"

STRATA = [
    ("Condominium", "#1f6fb2"),
    ("Houses",      "#e07b39"),
    ("Vacant Lot",  "#3a9a5c"),
]


def build_listings_geojson():
    listings = json.load(open(os.path.join(DATA, "listings.json")))
    feats = []
    for r in listings:
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
            "properties": {"stratum": r.get("stratum"), "city": r.get("city")},
        })
    fc = {"type": "FeatureCollection",
          "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
          "features": feats}
    json.dump(fc, open(TMP_GEOJSON, "w"))
    return len(feats)


def style_listings(layer):
    cats = []
    for name, hexcol in STRATA:
        sym = QgsMarkerSymbol.createSimple({
            "name": "circle", "size": "1.8",
            "color": hexcol, "outline_color": "white", "outline_width": "0.2",
        })
        sym.setOpacity(0.85)
        cats.append(QgsRendererCategory(name, sym, name))
    layer.setRenderer(QgsCategorizedSymbolRenderer("stratum", cats))


def style_lgu(layer):
    fill = QgsFillSymbol.createSimple({
        "color": "0,0,0,0", "outline_color": "#5a6b7b", "outline_width": "0.5",
    })
    layer.renderer().setSymbol(fill)
    # labels
    pal = QgsPalLayerSettings()
    pal.fieldName = "lgu"
    pal.enabled = True
    fmt = QgsTextFormat()
    f = QFont("Helvetica", 11); f.setBold(True)
    fmt.setFont(f); fmt.setSize(11)
    fmt.setColor(QColor("#2b3640"))
    buf = QgsTextBufferSettings(); buf.setEnabled(True); buf.setSize(1.0)
    buf.setColor(QColor("white")); fmt.setBuffer(buf)
    pal.setFormat(fmt)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))
    layer.setLabelsEnabled(True)


def main():
    qgs = QgsApplication([], False)
    qgs.initQgis()
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem(WEBMERC))

    n = build_listings_geojson()

    # basemap (light CartoDB Positron)
    base_url = ("type=xyz&url=https://basemaps.cartocdn.com/light_all/"
                "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=20&zmin=0")
    basemap = QgsRasterLayer(base_url, "Carto Light", "wms")

    lgu = QgsVectorLayer(os.path.join(DATA, "lgu_boundaries.geojson"), "LGU boundaries", "ogr")
    pts = QgsVectorLayer(TMP_GEOJSON, "Listings", "ogr")
    assert lgu.isValid() and pts.isValid(), (lgu.isValid(), pts.isValid())

    style_lgu(lgu)
    style_listings(pts)

    # add in draw order (basemap bottom)
    for lyr in (basemap, lgu, pts):
        if lyr.isValid():
            project.addMapLayer(lyr)

    # extent from the LISTINGS layer (in web mercator), with margin: this crops
    # out the eastern Olango island group, which carries no listings.
    from qgis.core import QgsCoordinateTransform
    xform = QgsCoordinateTransform(pts.crs(), QgsCoordinateReferenceSystem(WEBMERC), project)
    ext = xform.transformBoundingBox(pts.extent())
    mx, my = ext.width() * 0.05, ext.height() * 0.06
    ext = QgsRectangle(ext.xMinimum() - mx, ext.yMinimum() - my,
                       ext.xMaximum() + mx, ext.yMaximum() + my)

    # ---- print layout ----
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    page = layout.pageCollection().pages()[0]
    PW, PH = 290, 250  # mm, landscape-ish to fit Metro Cebu
    page.setPageSize(QgsLayoutSize(PW, PH, QgsUnitTypes.LayoutMillimeters))

    # map item
    m = QgsLayoutItemMap(layout)
    m.setRect(0, 0, 1, 1)
    m.attemptMove(QgsLayoutPoint(10, 24, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(PW - 20, PH - 34, QgsUnitTypes.LayoutMillimeters))
    m.setExtent(ext)
    m.setLayers([pts, lgu, basemap])
    m.setBackgroundColor(QColor("white"))
    m.setFrameEnabled(True)
    m.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(m)

    # title
    title = QgsLayoutItemLabel(layout)
    title.setText("Open-Market Residential Listings Across Metro Cebu")
    tf = QFont("Helvetica", 20); tf.setBold(True)
    title.setFont(tf)
    title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(PW - 20, 11, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title)

    sub = QgsLayoutItemLabel(layout)
    sub.setText(f"{n:,} modeled listings from three online portals, by deployed property stratum")
    sf = QFont("Helvetica", 11)
    sub.setFont(sf); sub.setFontColor(QColor("#555555"))
    sub.attemptMove(QgsLayoutPoint(10, 16, QgsUnitTypes.LayoutMillimeters))
    sub.attemptResize(QgsLayoutSize(PW - 20, 7, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub)

    # legend (listings only)
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Property stratum")
    legend.setAutoUpdateModel(False)
    grp = legend.model().rootGroup()
    grp.clear()
    node = grp.addLayer(pts)
    # hide the redundant layer-name row so only the categories show
    node.setName("")
    legend.model().refreshLayerLegend(node)
    legend.setLegendFilterByMapEnabled(False)
    legend.attemptMove(QgsLayoutPoint(PW - 62, 30, QgsUnitTypes.LayoutMillimeters))
    legend.setBackgroundEnabled(True)
    legend.setBackgroundColor(QColor(255, 255, 255, 235))
    legend.setFrameEnabled(True)
    legend.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(legend)

    # scale bar
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

    # north arrow
    na = QgsLayoutItemPicture(layout)
    svg = os.path.join(QgsApplication.prefixPath(), "..", "Resources", "svg",
                       "arrows", "NorthArrow_02.svg")
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
    else:
        nlab = QgsLayoutItemLabel(layout)
        nlab.setText("N ↑")
        nf = QFont("Helvetica", 16); nf.setBold(True); nlab.setFont(nf)
        nlab.attemptMove(QgsLayoutPoint(PW - 24, PH - 34, QgsUnitTypes.LayoutMillimeters))
        nlab.attemptResize(QgsLayoutSize(16, 12, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(nlab)

    # export
    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = 150
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res = exporter.exportToImage(OUT, settings)
    print(f"export result={res}  ->  {OUT}  ({n:,} listings)")

    qgs.exitQgis()


if __name__ == "__main__":
    main()
