"""
render_study_area_map_qgis.py
=============================
Renders a presentation-quality study-area locator map of the six Metro Cebu
LGUs using headless PyQGIS: a light CartoDB basemap, the LGU polygons filled by
a categorical color per LGU (semi-transparent so the basemap reads through),
labeled, exported through a print layout (title, scale bar, north arrow).

Improves the earlier plain choropleth (diagrams/lgu_boundaries.png, "Map 1").
Run via the QGIS-bundled Python with the QGIS environment set.
"""

import os
import json

from qgis.core import (
    QgsApplication, QgsProject, QgsVectorLayer, QgsRasterLayer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFillSymbol,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemScaleBar, QgsLayoutItemPicture, QgsPrintLayout,
    QgsLayoutSize, QgsLayoutPoint, QgsUnitTypes, QgsLayoutExporter, QgsRectangle,
)
from qgis.PyQt.QtGui import QColor, QFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "public", "data")
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "EDA", "plots", "study_area_map_qgis.png"))

WEBMERC = "EPSG:3857"

# user-selected map framing (EPSG:4326) captured from the QGIS canvas 2026-06-30;
# shared by all three Metro Cebu maps. xmin, ymin, xmax, ymax.
USER_BBOX = (123.71034639970264, 10.189215977449143,
             124.10600490419463, 10.501316464439972)

LGU_COLORS = {
    "Cebu City":      "#9ecae1",
    "Mandaue City":   "#bcbddc",
    "Lapu-Lapu City": "#fdae6b",
    "Talisay City":   "#fff2ae",
    "Minglanilla":    "#fbb4ae",
    "Consolacion":    "#b3de69",
}


def style_lgu(layer):
    cats = []
    for name, hexcol in LGU_COLORS.items():
        sym = QgsFillSymbol.createSimple({
            "color": hexcol, "outline_color": "#4a5a68", "outline_width": "0.5",
        })
        sym.setOpacity(0.55)
        cats.append(QgsRendererCategory(name, sym, name))
    layer.setRenderer(QgsCategorizedSymbolRenderer("lgu", cats))

    pal = QgsPalLayerSettings()
    pal.fieldName = "lgu"
    pal.enabled = True
    fmt = QgsTextFormat()
    f = QFont("Helvetica", 13); f.setBold(True)
    fmt.setFont(f); fmt.setSize(13)
    fmt.setColor(QColor("#222b33"))
    buf = QgsTextBufferSettings(); buf.setEnabled(True); buf.setSize(1.2)
    buf.setColor(QColor("white")); fmt.setBuffer(buf)
    pal.setFormat(fmt)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))
    layer.setLabelsEnabled(True)


def main():
    qgs = QgsApplication([], False)
    qgs.initQgis()
    project = QgsProject.instance()
    project.setCrs(QgsCoordinateReferenceSystem(WEBMERC))

    base_url = ("type=xyz&url=https://basemaps.cartocdn.com/light_all/"
                "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=20&zmin=0")
    basemap = QgsRasterLayer(base_url, "Carto Light", "wms")
    lgu = QgsVectorLayer(os.path.join(DATA, "lgu_boundaries.geojson"), "LGU", "ogr")
    assert lgu.isValid(), "LGU layer invalid"

    style_lgu(lgu)
    for lyr in (basemap, lgu):
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
    m.setLayers([lgu, basemap])
    m.setBackgroundColor(QColor("white"))
    m.setFrameEnabled(True)
    m.setFrameStrokeColor(QColor("#9aa6b2"))
    layout.addLayoutItem(m)

    title = QgsLayoutItemLabel(layout)
    title.setText("Metro Cebu Study Area")
    tf = QFont("Helvetica", 20); tf.setBold(True)
    title.setFont(tf)
    title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))
    title.attemptResize(QgsLayoutSize(PW - 20, 11, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title)

    sub = QgsLayoutItemLabel(layout)
    sub.setText("The six local government units in the modeling scope")
    sf = QFont("Helvetica", 11)
    sub.setFont(sf); sub.setFontColor(QColor("#555555"))
    sub.attemptMove(QgsLayoutPoint(10, 16, QgsUnitTypes.LayoutMillimeters))
    sub.attemptResize(QgsLayoutSize(PW - 20, 7, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub)

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
    print(f"export result={res}  ->  {OUT}")

    qgs.exitQgis()


if __name__ == "__main__":
    main()
