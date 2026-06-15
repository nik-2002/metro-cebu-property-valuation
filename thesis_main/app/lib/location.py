"""Resolve which Metro Cebu LGU contains a dropped-pin coordinate.

The predictor derives the City from the pin (point-in-polygon) instead of asking the
user, so a pin in Minglanilla can never be paired with City = Cebu City. Geometry comes
from the same boundary file the Market Map draws (app/data/lgu_boundaries.geojson),
which carries one MultiPolygon per LGU under the ``lgu`` property.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from shapely.geometry import Point, shape


_LGU_GEOJSON = Path(__file__).resolve().parents[1] / "data" / "lgu_boundaries.geojson"


@lru_cache(maxsize=1)
def _lgu_geometries() -> list[tuple[str, object]]:
    data = json.loads(_LGU_GEOJSON.read_text())
    geoms = []
    for feature in data.get("features", []):
        name = (feature.get("properties") or {}).get("lgu")
        geom = feature.get("geometry")
        if name and geom:
            geoms.append((str(name), shape(geom)))
    return geoms


def city_from_point(lat: float, lon: float) -> str | None:
    """Return the LGU whose boundary contains the point, or None if outside all six."""
    pt = Point(float(lon), float(lat))
    for name, geom in _lgu_geometries():
        if geom.contains(pt):
            return name
    return None
