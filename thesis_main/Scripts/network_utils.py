"""
network_utils.py
----------------
Shared utility for Metro Cebu road network (osmnx).

Provides:
  - load_metro_cebu_graph()             : download/cache the street network
  - network_distances_from_sources()    : batch Dijkstra from named target nodes (CBD)
  - network_distances_from_properties() : per-property Dijkstra for Hansen scores
"""

import os, sys, importlib.util as _ilu
# macOS fix: set PROJ data dir before pyproj C context initialises
_pyproj_spec = _ilu.find_spec("pyproj")
if _pyproj_spec:
    _proj_data = os.path.join(os.path.dirname(_pyproj_spec.origin), "proj_dir", "share", "proj")
    if os.path.isfile(os.path.join(_proj_data, "proj.db")):
        os.environ.setdefault("PROJ_DATA", _proj_data)
        import pyproj.datadir as _pd; _pd.set_data_dir(_proj_data)

import os, math, pickle, logging
import numpy as np
logging.getLogger("osmnx").setLevel(logging.WARNING)
import osmnx as ox
import networkx as nx

# Workaround: pyproj proj.db lookup fails in this environment; the Metro Cebu
# graph is always EPSG:4326 (unprojected), so force is_projected -> False to
# bypass the CRS database round-trip inside ox.distance.nearest_nodes.
if hasattr(ox, "projection"):
    ox.projection.is_projected = lambda _crs: False

GRAPH_CACHE = "thesis_main/Data/processed/metro_cebu_network.pkl"
METRO_CEBU_BBOX = (10.17, 123.74, 10.43, 124.07)

def _haversine_m(lat1, lon1, lat2, lon2):
    R = 6_371_000
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1; dlon = rlon2 - rlon1
    a = math.sin(dlat/2)**2 + math.cos(rlat1)*math.cos(rlat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))

def load_metro_cebu_graph(cache_path=GRAPH_CACHE):
    if os.path.exists(cache_path):
        print(f"  Loading cached graph from {cache_path}...")
        with open(cache_path, "rb") as f: G = pickle.load(f)
        print(f"  Graph: {len(G.nodes):,} nodes, {len(G.edges):,} edges")
        return G
    print("  Downloading Metro Cebu road network via osmnx (first run)...")
    south, west, north, east = METRO_CEBU_BBOX
    G = ox.graph_from_bbox((west, south, east, north), network_type="drive", simplify=True)
    G = ox.convert.to_undirected(G)
    print(f"  Downloaded: {len(G.nodes):,} nodes, {len(G.edges):,} edges")
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    with open(cache_path, "wb") as f: pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  Cached to {cache_path}")
    return G

def network_distances_from_sources(G, source_coords, target_coords_dict):
    target_names = list(target_coords_dict.keys())
    target_lats  = [target_coords_dict[n][0] for n in target_names]
    target_lons  = [target_coords_dict[n][1] for n in target_names]
    target_nodes = ox.nearest_nodes(G, X=target_lons, Y=target_lats)
    target_node_map = dict(zip(target_names, target_nodes))
    dist_from_target = {}
    for name, t_node in target_node_map.items():
        try: dist_from_target[name] = nx.single_source_dijkstra_path_length(G, t_node, weight="length")
        except: dist_from_target[name] = {}
    src_nodes = ox.nearest_nodes(G, X=[c[1] for c in source_coords], Y=[c[0] for c in source_coords])
    distances, fallback_flags = [], []
    for src_node, (slat, slon) in zip(src_nodes, source_coords):
        row_dist, row_flag = {}, {}
        for name in target_names:
            tlat, tlon = target_coords_dict[name]
            d = dist_from_target[name].get(src_node, None)
            if d is not None: row_dist[name]=d; row_flag[name]=False
            else: row_dist[name]=_haversine_m(slat,slon,tlat,tlon); row_flag[name]=True
        distances.append(row_dist); fallback_flags.append(row_flag)
    return distances, fallback_flags

def network_distances_from_properties(
    G, source_coords, amenity_coords_by_category,
    radius_km=5.0,
    category_radii=None,   # dict mapping category name to radius_km override
):
    """Return per-property, per-category network distances (km) for all POIs
    within the true network-distance threshold.

    The haversine distance is used only as a loose computational pre-screen
    (1.5x the target radius). The final cutoff is applied on actual network
    distance, so the radius is a true road-network threshold.

    Parameters
    ----------
    G : networkx graph  (osmnx road network)
    source_coords : list of (lat, lon) tuples  -- one per property
    amenity_coords_by_category : dict  {cat: (lat_array, lon_array)}
    radius_km : float  -- default radius for all categories
    category_radii : dict or None  -- per-category override, e.g. {"recreation": 0.8}
    """
    import numpy as np
    src_lats = np.array([c[0] for c in source_coords])
    src_lons = np.array([c[1] for c in source_coords])
    src_nodes = ox.nearest_nodes(G, X=src_lons.tolist(), Y=src_lats.tolist())
    amenity_nodes_by_cat = {}
    for cat, (alats, alons) in amenity_coords_by_category.items():
        amenity_nodes_by_cat[cat] = ox.nearest_nodes(G, X=alons.tolist(), Y=alats.tolist()) if len(alats)>0 else []
    dist_results = []
    for i, (src_node, slat, slon) in enumerate(zip(src_nodes, src_lats, src_lons)):
        try: length_map = nx.single_source_dijkstra_path_length(G, src_node, weight="length")
        except: length_map = {}
        row = {}
        for cat, (alats, alons) in amenity_coords_by_category.items():
            # Resolve effective radius for this category
            eff_radius = category_radii.get(cat, radius_km) if category_radii else radius_km
            if len(alats)==0: row[cat]=np.array([]); continue
            dlat=np.radians(alats-slat); dlon=np.radians(alons-slon)
            a=(np.sin(dlat/2)**2 + np.cos(np.radians(slat))*np.cos(np.radians(alats))*np.sin(dlon/2)**2)
            hav_km=6371.0*2*np.arcsin(np.sqrt(a))
            # Loose haversine pre-screen (1.5x buffer) -- never excludes a valid POI
            prescreen=np.where(hav_km<=eff_radius*1.5)[0]
            if len(prescreen)==0: row[cat]=np.array([]); continue
            a_nodes=amenity_nodes_by_cat[cat]
            net_km=[]
            for idx in prescreen:
                d_m=length_map.get(a_nodes[idx],None)
                nkm = d_m/1000.0 if d_m is not None else float(hav_km[idx])
                # True network distance cutoff
                if nkm <= eff_radius:
                    net_km.append(nkm)
            row[cat]=np.array(net_km)
        dist_results.append(row)
        if (i+1)%100==0: print(f"    Processed {i+1}/{len(source_coords)} properties...")
    return dist_results
