import numpy as np
import pandas as pd
import streamlit as st
from sklearn.neighbors import BallTree

from lib.config import ABT_PATH, LOCAL_LOOKUP_COLS


EARTH_RADIUS_M = 6_371_000.0
FALLBACK_DISTANCE_M = 5_000.0


class MCRAILookup:
    """Nearest-neighbour lookup of all location-derived features (MCRAI scores,
    network CBD distances, road-network distances, spatial lag, BIR commercial)
    from the training ABT.

    These features cannot be recomputed from user input at prediction time
    (they need the POI sets, the osmnx graph, and neighbour prices), so they are
    approximated from the nearest training properties. CBD distances are looked up
    here too, so a dropped pin inherits the trained network distance (including
    Mactan bridge friction) instead of a straight-line haversine approximation.
    """

    def __init__(self) -> None:
        abt = pd.read_csv(ABT_PATH, usecols=["latitude", "longitude", *LOCAL_LOOKUP_COLS])
        abt = abt.dropna(subset=["latitude", "longitude", *LOCAL_LOOKUP_COLS]).reset_index(drop=True)

        self.lookup_df = abt[["latitude", "longitude", *LOCAL_LOOKUP_COLS]].copy()
        coords_rad = np.radians(self.lookup_df[["latitude", "longitude"]].to_numpy())
        self.tree = BallTree(coords_rad, metric="haversine")
        self.medians = self.lookup_df[LOCAL_LOOKUP_COLS].median().to_dict()
        self.fallback = False

    def query(self, lat: float, lon: float, k: int = 5) -> dict[str, float]:
        neighbor_count = max(1, min(k, len(self.lookup_df)))
        query_rad = np.radians(np.array([[lat, lon]], dtype=float))
        distances_rad, indices = self.tree.query(query_rad, k=neighbor_count)
        distances_m = distances_rad[0] * EARTH_RADIUS_M

        if distances_m[0] > FALLBACK_DISTANCE_M:
            self.fallback = True
            return {col: float(self.medians[col]) for col in LOCAL_LOOKUP_COLS}

        self.fallback = False
        nearest_rows = self.lookup_df.iloc[indices[0]][LOCAL_LOOKUP_COLS]
        weights = 1.0 / np.maximum(distances_m, 1.0)
        weights = weights / weights.sum()
        weighted = nearest_rows.mul(weights, axis=0).sum(axis=0)
        return {col: float(weighted[col]) for col in LOCAL_LOOKUP_COLS}


@st.cache_resource
def get_mcrai_lookup() -> MCRAILookup:
    """Build the nearest-neighbour lookup once per Streamlit process."""
    return MCRAILookup()
