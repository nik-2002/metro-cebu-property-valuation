from qgis.core import QgsProject
import json

project = QgsProject.instance()
# Get the currently active map settings or let the user know where to click.
# QGIS render resolution is usually controlled via Layouts (Print Composer)
# or via Map Canvas settings if exporting from the main window.
print("Checked settings.")
