import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./styles.css";

type ViewName = "market" | "surface" | "predict";
type SurfaceKey = "sdh" | "condo" | "vacant";

type Listing = {
  propertyId: number;
  latitude: number;
  longitude: number;
  pricePerSqm: number;
  pricePhp: number | null;
  city: string;
  barangay: string;
  propertyType: string;
  stratum: "Condominium" | "Houses" | "Vacant Lot";
  address: string;
  areaSqm: number | null;
  bedrooms?: number | null;
  bathrooms?: number | null;
  bedroomsImputed?: boolean;
  bathroomsImputed?: boolean;
  mcrai?: Record<string, number | null>;
  dist?: Record<string, number | null>;
  birZonalRr?: number | null;
  spatialLag?: number | null;
};

type Poi = {
  category: string;
  latitude: number;
  longitude: number;
  amenity: string;
  amenityType: string;
};

type SurfaceProperties = {
  barangay: string;
  lgu: string;
  adm4_pcode?: string;
  price_per_sqm: number;
  price_q25?: number;
  price_q75?: number;
  price_label: string;
  confidence_label: string;
  point_count: number;
  low_confidence?: boolean;
  fillColor?: string;
  classLabel?: string;
};

type BarangayFeatureRecord = {
  n_listings: number;
  mcrai: Record<string, number>;
  dist: Record<string, number>;
  bir_zonal_rr_median?: number;
  spatial_lag_price?: number;
  listing_price_median: number;
  listing_price_min: number;
  listing_price_max: number;
};

type BarangayFeatures = {
  mcrai_max: Record<string, number>;
  barangays: Record<string, BarangayFeatureRecord>;
};

type SurfaceFeature = GeoJSON.Feature<GeoJSON.Geometry, SurfaceProperties>;
type SurfaceCollection = GeoJSON.FeatureCollection<GeoJSON.Geometry, SurfaceProperties>;

type ResolveResponse = {
  city: string | null;
  inside_metro: boolean;
  bir_estimate: number | null;
};

type Driver = { label: string; shap: number; pct: number };

type PredictResponse = {
  city: string;
  bir_used: number;
  stratum_label: string;
  model_family: string;
  price_per_sqm: number;
  price_php: number;
  ci_available: boolean;
  ci_low_per_sqm: number;
  ci_high_per_sqm: number;
  mdape: number | null;
  mape: number | null;
  pe20: number | null;
  mcrai_fallback: boolean;
  drivers: Driver[];
  driver_error: string | null;
};

type State = {
  view: ViewName;
  lgu: string;
  barangay: string;
  strata: Set<string>;
  poiCategories: Set<string>;
  showHeatmap: boolean;
  showLgu: boolean;
  showPois: boolean;
  listingNodeSize: number;
  selectedId: number | null;
  surfaceKey: SurfaceKey;
  hideLowConfidence: boolean;
  showSurfaceLgu: boolean;
  selectedSurface: SurfaceProperties | null;
  predictType: string;
  predictArea: number;
  predictBeds: string;
  predictBaths: string;
  predictPin: { lat: number; lon: number } | null;
  predictCity: string | null;
  predictInside: boolean;
  predictBir: number | null;
  predictBirOverride: boolean;
  predictBirValue: number | null;
  predictResolving: boolean;
  predictLoading: boolean;
  predictResult: PredictResponse | null;
  predictError: string | null;
  predictNearby: Array<{ listing: Listing; dist: number }>;
};

const metroCebuCities = [
  "Cebu City",
  "Consolacion",
  "Lapu-Lapu City",
  "Mandaue City",
  "Minglanilla",
  "Talisay City",
];

const surfaceMeta: Record<SurfaceKey, { file: string; label: string; subtitle: string }> = {
  sdh: {
    file: "barangay_surface_sdh.geojson",
    label: "Single Detached",
    subtitle: "150 sqm lot archetype",
  },
  condo: {
    file: "barangay_surface_condo.geojson",
    label: "Condominium",
    subtitle: "60 sqm unit archetype",
  },
  vacant: {
    file: "barangay_surface_vacant.geojson",
    label: "Vacant Lot",
    subtitle: "200 sqm lot archetype",
  },
};

const stratumColors: Record<string, string> = {
  Condominium: "#2563eb",
  Houses: "#16a34a",
  "Vacant Lot": "#d97706",
};

const poiColors: Record<string, string> = {
  Grocery: "#d97706",
  Retail: "#db2777",
  Health: "#0284c7",
  Hospitals: "#dc2626",
  Education: "#4f46e5",
  Security: "#111827",
  Recreation: "#16a34a",
  Tourism: "#7e22ce",
};

const priceStops = [
  [49, 46, 129],
  [34, 113, 177],
  [21, 156, 128],
  [244, 185, 66],
  [204, 45, 45],
];

const surfacePalette = ["#eff3ff", "#c6dbef", "#9ecae1", "#6baed6", "#2171b5"];
const lowConfidenceColor = "#94a3b8";

const mcraiLabels: Record<string, string> = {
  composite: "Overall access (composite)",
  education: "Education",
  grocery: "Grocery",
  health: "Health",
  hospitals: "Hospitals",
  recreation: "Recreation",
  security: "Security",
  tourism: "Tourism",
  retail_density: "Retail density",
};
const mcraiOrder = [
  "composite",
  "grocery",
  "health",
  "education",
  "retail_density",
  "tourism",
  "recreation",
  "hospitals",
  "security",
];
const cbdLabels: Record<string, string> = {
  cbp: "Cebu Business Park",
  mandaue: "Mandaue CBD",
  mactan: "Mactan CBD",
  srp: "SRP",
  talisay: "Talisay–Tabunok",
  consolacion: "Consolacion",
  naga: "Naga City",
  airport: "Airport",
};
const roadLabels: Record<string, string> = {
  trunk_road: "Trunk road",
  primary_road: "Primary road",
};

const state: State = {
  view: "market",
  lgu: "All LGUs",
  barangay: "All barangays",
  strata: new Set(["Condominium", "Houses", "Vacant Lot"]),
  poiCategories: new Set(["Grocery", "Retail"]),
  showHeatmap: false,
  showLgu: true,
  showPois: true,
  listingNodeSize: 6,
  selectedId: null,
  surfaceKey: "sdh",
  hideLowConfidence: false,
  showSurfaceLgu: true,
  selectedSurface: null,
  predictType: "Condominium",
  predictArea: 60,
  predictBeds: "",
  predictBaths: "",
  predictPin: null,
  predictCity: null,
  predictInside: false,
  predictBir: null,
  predictBirOverride: false,
  predictBirValue: null,
  predictResolving: false,
  predictLoading: false,
  predictResult: null,
  predictError: null,
  predictNearby: [],
};

let listings: Listing[] = [];
let pois: Poi[] = [];
let barangayFeatures: BarangayFeatures = { mcrai_max: {}, barangays: {} };
let surfaces: Record<SurfaceKey, SurfaceCollection> = {} as Record<SurfaceKey, SurfaceCollection>;
let lguLayer: L.GeoJSON | null = null;
let listingLayer = L.layerGroup();
let poiLayer = L.layerGroup();
let surfaceLayer: L.GeoJSON | null = null;
let predictMarker: L.CircleMarker | null = null;
let predictBufferLayer: L.Circle | null = null;
let predictNearbyLayer = L.layerGroup();

const PREDICT_RADIUS_M = 1000;

function haversineM(aLat: number, aLon: number, bLat: number, bLon: number): number {
  const earth = 6371000;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(bLat - aLat);
  const dLon = toRad(bLon - aLon);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(aLat)) * Math.cos(toRad(bLat)) * Math.sin(dLon / 2) ** 2;
  return 2 * earth * Math.asin(Math.sqrt(h));
}

function nearbyListings(pin: { lat: number; lon: number }): Array<{ listing: Listing; dist: number }> {
  return listings
    .map((listing) => ({ listing, dist: haversineM(pin.lat, pin.lon, listing.latitude, listing.longitude) }))
    .filter((item) => item.dist <= PREDICT_RADIUS_M)
    .sort((a, b) => a.dist - b.dist);
}

const map = L.map("map", {
  center: [10.32, 123.9],
  zoom: 11,
  zoomControl: true,
  preferCanvas: true,
});

L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  subdomains: "abcd",
  maxZoom: 19,
}).addTo(map);

const byId = <T extends HTMLElement>(id: string) => {
  const element = document.getElementById(id);
  if (!element) throw new Error(`Missing element: ${id}`);
  return element as T;
};

const currency = (value: number | null | undefined) =>
  typeof value === "number" && Number.isFinite(value)
    ? `PHP ${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`
    : "n/a";

const escapeHtml = (value: string) =>
  value.replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char] as string,
  );

const quantile = (values: number[], q: number) => {
  if (!values.length) return 0;
  const pos = (values.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  const next = values[base + 1];
  return next === undefined ? values[base] : values[base] + rest * (next - values[base]);
};

const classBreaks = (features: SurfaceFeature[]) => {
  const confident = features
    .filter((feature) => !feature.properties.low_confidence)
    .map((feature) => Number(feature.properties.price_per_sqm))
    .sort((a, b) => a - b);
  const prices = confident.length
    ? confident
    : features.map((feature) => Number(feature.properties.price_per_sqm)).sort((a, b) => a - b);
  return [0, 0.2, 0.4, 0.6, 0.8, 1].map((q) => quantile(prices, q));
};

const classIndex = (value: number, breaks: number[]) => {
  const index = breaks.slice(1).findIndex((breakValue) => value <= breakValue);
  return Math.max(0, Math.min(surfacePalette.length - 1, index === -1 ? surfacePalette.length - 1 : index));
};

const priceRampColor = (value: number, low: number, high: number) => {
  const span = high - low || 1;
  const t = Math.max(0, Math.min(1, (value - low) / span));
  const scaled = t * (priceStops.length - 1);
  const idx = Math.min(priceStops.length - 2, Math.floor(scaled));
  const f = scaled - idx;
  const rgb = priceStops[idx].map((channel, channelIdx) =>
    Math.round(channel + (priceStops[idx + 1][channelIdx] - channel) * f),
  );
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
};

const selectedCheckboxValues = (name: string) =>
  new Set(Array.from(document.querySelectorAll<HTMLInputElement>(`input[name="${name}"]:checked`)).map((input) => input.value));

const filteredListings = () =>
  listings.filter((listing) => {
    if (!state.strata.has(listing.stratum)) return false;
    if (state.lgu !== "All LGUs" && listing.city !== state.lgu) return false;
    if (state.barangay !== "All barangays" && listing.barangay !== state.barangay) return false;
    return true;
  });

const filteredPois = () => {
  if (!state.showPois) return [];
  return pois.filter((poi) => state.poiCategories.has(poi.category));
};

function setLayerVisibility(layer: L.Layer | null, visible: boolean) {
  if (!layer) return;
  if (visible && !map.hasLayer(layer)) layer.addTo(map);
  if (!visible && map.hasLayer(layer)) layer.removeFrom(map);
}

function clearDynamicLayers() {
  listingLayer.clearLayers();
  poiLayer.clearLayers();
  if (surfaceLayer && map.hasLayer(surfaceLayer)) surfaceLayer.removeFrom(map);
  surfaceLayer = null;
  if (predictMarker && map.hasLayer(predictMarker)) predictMarker.removeFrom(map);
  predictMarker = null;
  if (predictBufferLayer && map.hasLayer(predictBufferLayer)) predictBufferLayer.removeFrom(map);
  predictBufferLayer = null;
  predictNearbyLayer.clearLayers();
  if (map.hasLayer(predictNearbyLayer)) predictNearbyLayer.removeFrom(map);
}

function renderLguOptions() {
  const select = byId<HTMLSelectElement>("lgu-filter");
  select.innerHTML = ["All LGUs", ...metroCebuCities].map((city) => `<option value="${city}">${city}</option>`).join("");
  select.value = state.lgu;
}

function renderBarangayOptions() {
  const select = byId<HTMLSelectElement>("barangay-filter");
  const scoped = listings.filter((listing) => state.lgu === "All LGUs" || listing.city === state.lgu);
  const barangays = Array.from(new Set(scoped.map((listing) => listing.barangay).filter(Boolean))).sort();
  if (state.barangay !== "All barangays" && !barangays.includes(state.barangay)) state.barangay = "All barangays";
  select.innerHTML = ["All barangays", ...barangays]
    .map((barangay) => `<option value="${barangay}">${barangay}</option>`)
    .join("");
  select.value = state.barangay;
}

function renderViewChrome() {
  byId("market-controls").hidden = state.view !== "market";
  byId("surface-controls").hidden = state.view !== "surface";
  byId("predict-controls").hidden = state.view !== "predict";
  byId("selected-section").hidden = state.view !== "market";
  byId("market-section").hidden = state.view !== "market";
  byId("ranking-section").hidden = state.view !== "market";
  byId("surface-section").hidden = state.view !== "surface";
  byId("predict-section").hidden = state.view !== "predict";
  byId("market-view").classList.toggle("active", state.view === "market");
  byId("surface-view").classList.toggle("active", state.view === "surface");
  byId("predict-view").classList.toggle("active", state.view === "predict");
}

function renderMarketLegend() {
  const legend = byId("legend");
  if (state.showHeatmap) {
    legend.innerHTML = `
      <div class="legend-title">Price heatmap</div>
      <div class="price-ramp"></div>
      <div class="price-labels"><span>Lower PHP/sqm</span><span>Higher PHP/sqm</span></div>
    `;
    return;
  }
  const items = Array.from(state.strata)
    .map((stratum) => `<span class="legend-item"><i style="background:${stratumColors[stratum]}"></i>${stratum}</span>`)
    .join("");
  legend.innerHTML = `<div class="legend-title">Listings</div><div class="legend-row">${items}</div>`;
}

function renderNodeSizeControl() {
  byId<HTMLOutputElement>("node-size-value").textContent = `${state.listingNodeSize} px`;
  byId<HTMLInputElement>("node-size-slider").value = String(state.listingNodeSize);
}

function renderSurfaceLegend(breaks: number[], showLowConfidence: boolean) {
  const items = surfacePalette
    .map(
      (color, idx) =>
        `<span class="legend-item"><i class="legend-box" style="background:${color}"></i>${currency(breaks[idx])}-${currency(breaks[idx + 1])}</span>`,
    )
    .join("");
  const low = showLowConfidence
    ? `<span class="legend-item"><i class="legend-box" style="background:${lowConfidenceColor}"></i>Low confidence</span>`
    : "";
  byId("legend").innerHTML = `<div class="legend-title">Barangay PHP/sqm</div><div class="legend-row surface-legend">${items}${low}</div>`;
}

function renderListingLayer(view: Listing[]) {
  listingLayer.clearLayers();
  const prices = view.map((listing) => listing.pricePerSqm).sort((a, b) => a - b);
  const low = prices[Math.floor(prices.length * 0.05)] ?? 0;
  const high = prices[Math.floor(prices.length * 0.95)] ?? low + 1;

  for (const listing of view) {
    const selected = listing.propertyId === state.selectedId;
    const radius = selected ? state.listingNodeSize + 4 : state.listingNodeSize;
    L.circleMarker([listing.latitude, listing.longitude], {
      radius,
      color: selected ? "#111827" : "#ffffff",
      weight: selected ? 3 : 1.4,
      fillColor: state.showHeatmap ? priceRampColor(listing.pricePerSqm, low, high) : stratumColors[listing.stratum],
      fillOpacity: 0.92,
    })
      .bindTooltip(
        `<strong>${listing.stratum} · ${listing.city}</strong><br>${currency(listing.pricePerSqm)} / sqm<br>${listing.barangay || ""}`,
      )
      .on("click", () => {
        state.selectedId = listing.propertyId;
        render();
      })
      .addTo(listingLayer);
  }
}

function renderPoiLayer(view: Poi[]) {
  poiLayer.clearLayers();
  for (const poi of view) {
    L.circleMarker([poi.latitude, poi.longitude], {
      radius: 4,
      color: "#ffffff",
      weight: 0.8,
      fillColor: poiColors[poi.category] ?? "#64748b",
      fillOpacity: 0.9,
    })
      .bindTooltip(`<strong>${poi.category} POI</strong><br>${poi.amenity}<br>${poi.amenityType}`)
      .addTo(poiLayer);
  }
}

function renderMarketMetrics(view: Listing[], poiView: Poi[]) {
  byId("page-title").textContent = "Residential Market Map";
  byId("subtitle").textContent = `${view.length.toLocaleString()} listings · ${poiView.length.toLocaleString()} visible POIs`;

  const prices = view.map((listing) => listing.pricePerSqm).sort((a, b) => a - b);
  const median = prices.length ? prices[Math.floor(prices.length / 2)] : null;
  const average = prices.length ? prices.reduce((sum, price) => sum + price, 0) / prices.length : null;

  byId("metric-count").textContent = view.length.toLocaleString();
  byId("metric-median").textContent = currency(median);
  byId("metric-average").textContent = currency(average);
  byId("metric-pois").textContent = poiView.length.toLocaleString();
}

function roomValue(value: number | null | undefined): string {
  if (value == null) return "";
  return value % 1 === 0 ? String(value) : value.toFixed(1);
}

// Shared MCRAI + accessibility + BIR/spatial-lag block, used by both the barangay
// detail panel and the in-depth property breakdown.
function featureBlocksHtml(
  mcrai: Record<string, number | null> | undefined,
  dist: Record<string, number | null> | undefined,
  bir: number | null | undefined,
  spatialLag: number | null | undefined,
  footerNote?: string,
): string {
  const parts: string[] = [];

  if (mcrai && mcraiOrder.some((key) => mcrai[key] != null)) {
    parts.push(`<div class="bd-section">Amenity access (MCRAI)</div>`);
    for (const key of mcraiOrder) {
      const value = mcrai[key];
      if (value == null) continue;
      const max = barangayFeatures.mcrai_max[key] || value || 1;
      const width = Math.min(100, Math.max(3, (value / max) * 100));
      parts.push(
        `<div class="bd-bar-row"><div class="bd-bar-top"><span>${mcraiLabels[key] ?? key}</span><b>${value.toFixed(1)}</b></div>` +
          `<div class="bd-track"><span class="bd-bar" style="width:${width.toFixed(0)}%"></span></div></div>`,
      );
    }
  }

  if (dist) {
    const cbdEntries = Object.keys(cbdLabels)
      .filter((key) => dist[key] != null)
      .map((key) => ({ key, m: dist[key] as number }));
    if (cbdEntries.length) {
      const nearest = cbdEntries.reduce((a, b) => (b.m < a.m ? b : a));
      parts.push(`<div class="bd-section">Accessibility</div>`);
      parts.push(
        `<div class="bd-row"><span>Nearest CBD node</span><b>${cbdLabels[nearest.key]} · ${(nearest.m / 1000).toFixed(1)} km</b></div>`,
      );
      const grid = cbdEntries
        .map(
          (entry) =>
            `<div class="bd-dist"><span>${cbdLabels[entry.key]}</span><b>${(entry.m / 1000).toFixed(1)} km</b></div>`,
        )
        .join("");
      parts.push(`<div class="bd-dist-grid">${grid}</div>`);
    }
    for (const key of Object.keys(roadLabels)) {
      if (dist[key] == null) continue;
      parts.push(
        `<div class="bd-row"><span>${roadLabels[key]}</span><b>${((dist[key] as number) / 1000).toFixed(2)} km</b></div>`,
      );
    }
  }

  if (bir != null || spatialLag != null) {
    parts.push(`<div class="bd-section">Other model features</div>`);
    if (bir != null) {
      parts.push(`<div class="bd-row"><span>BIR zonal — residential</span><b>${currency(bir)} /sqm</b></div>`);
    }
    if (spatialLag != null) {
      parts.push(
        `<div class="bd-row"><span>Neighbourhood price level (spatial lag)</span><b>${currency(spatialLag)}</b></div>`,
      );
    }
  }

  if (footerNote) parts.push(`<p class="bd-note">${footerNote}</p>`);
  return parts.join("");
}

function renderSelectedProperty() {
  const target = byId("selected-property");
  const listing = listings.find((item) => item.propertyId === state.selectedId);
  if (!listing) {
    target.className = "empty";
    target.textContent = "Select a listing on the map.";
    return;
  }

  const parts: string[] = [];
  parts.push(`<strong>${currency(listing.pricePerSqm)} <span>/ sqm listed</span></strong>`);
  parts.push(`<p>${escapeHtml(listing.stratum)} · ${escapeHtml(listing.propertyType)}</p>`);
  parts.push(`<p>${listing.barangay ? `${escapeHtml(listing.barangay)}, ` : ""}${escapeHtml(listing.city)}</p>`);
  if (listing.address) parts.push(`<p>${escapeHtml(listing.address)}</p>`);

  const meta: string[] = [];
  if (listing.areaSqm != null) meta.push(`${listing.areaSqm.toLocaleString()} sqm`);
  if (listing.pricePhp != null) meta.push(`${currency(listing.pricePhp)} total`);
  if (meta.length) parts.push(`<p class="sel-meta">${meta.join(" · ")}</p>`);

  if (listing.stratum !== "Vacant Lot" && (listing.bedrooms != null || listing.bathrooms != null)) {
    const rooms: string[] = [];
    if (listing.bedrooms != null) rooms.push(`${roomValue(listing.bedrooms)} bed`);
    if (listing.bathrooms != null) rooms.push(`${roomValue(listing.bathrooms)} bath`);
    const estimated = listing.bedroomsImputed || listing.bathroomsImputed;
    parts.push(
      `<p class="sel-rooms">${rooms.join(" · ")}${estimated ? ` <span class="muted">(some estimated)</span>` : ""}</p>`,
    );
  }

  parts.push(
    featureBlocksHtml(
      listing.mcrai,
      listing.dist,
      listing.birZonalRr,
      listing.spatialLag,
      `Property #${listing.propertyId} — record from the training ABT.`,
    ),
  );

  target.className = "selection";
  target.innerHTML = parts.join("");
}

function renderRanking() {
  const target = byId("lgu-ranking");
  const rows = metroCebuCities
    .map((city) => {
      const cityRows = listings.filter((listing) => state.strata.has(listing.stratum) && listing.city === city);
      const prices = cityRows.map((listing) => listing.pricePerSqm).sort((a, b) => a - b);
      return { city, median: prices.length ? prices[Math.floor(prices.length / 2)] : 0 };
    })
    .filter((row) => row.median > 0)
    .sort((a, b) => b.median - a.median);

  const top = rows[0]?.median || 1;
  target.innerHTML = rows
    .map(
      (row, idx) => `
        <div class="rank-line"><span>${idx + 1}. ${row.city}</span><strong>${currency(row.median)}</strong></div>
        <div class="rank-track"><i style="width:${(row.median / top) * 100}%"></i></div>
      `,
    )
    .join("");
}

function decoratedSurface() {
  const source = surfaces[state.surfaceKey];
  const allFeatures = source.features as SurfaceFeature[];
  const breaks = classBreaks(allFeatures);
  const features = allFeatures
    .filter((feature) => !(state.hideLowConfidence && feature.properties.low_confidence))
    .map((feature) => {
      const clone: SurfaceFeature = {
        ...feature,
        properties: { ...feature.properties },
      };
      if (clone.properties.low_confidence) {
        clone.properties.fillColor = lowConfidenceColor;
        clone.properties.classLabel = "Low confidence";
      } else {
        const idx = classIndex(Number(clone.properties.price_per_sqm), breaks);
        clone.properties.fillColor = surfacePalette[idx];
        clone.properties.classLabel = `${currency(breaks[idx])}-${currency(breaks[idx + 1])}`;
      }
      return clone;
    });
  return {
    collection: { ...source, features } as SurfaceCollection,
    breaks,
    allFeatures,
    visibleFeatures: features,
  };
}

function renderSurfaceLayer() {
  if (surfaceLayer && map.hasLayer(surfaceLayer)) surfaceLayer.removeFrom(map);
  const decorated = decoratedSurface();
  surfaceLayer = L.geoJSON(decorated.collection, {
    style: (feature) => ({
      color: "#ffffff",
      weight: 1,
      opacity: 0.82,
      fillColor: feature?.properties?.fillColor ?? "#cbd5e1",
      fillOpacity: feature?.properties?.low_confidence ? 0.46 : 0.82,
    }),
    onEachFeature: (feature, layer) => {
      const props = feature.properties as SurfaceProperties;
      layer.bindTooltip(surfaceTooltip(props));
      layer.on("click", () => {
        state.selectedSurface = props;
        renderSurfaceSummary(decorated);
      });
    },
  }).addTo(map);
  if (lguLayer && map.hasLayer(lguLayer)) lguLayer.bringToFront();
  renderSurfaceLegend(decorated.breaks, !state.hideLowConfidence);
  renderSurfaceSummary(decorated);
}

function renderSurfaceSummary(decorated = decoratedSurface()) {
  const meta = surfaceMeta[state.surfaceKey];
  const prices = decorated.allFeatures.map((feature) => Number(feature.properties.price_per_sqm)).sort((a, b) => a - b);
  const lowCount = decorated.allFeatures.filter((feature) => feature.properties.low_confidence).length;
  const median = quantile(prices, 0.5);
  byId("page-title").textContent = "Metro Cebu Price Surface";
  byId("subtitle").textContent = `${meta.label} · ${meta.subtitle} · ${decorated.visibleFeatures.length.toLocaleString()} of ${decorated.allFeatures.length.toLocaleString()} barangays visible`;
  byId("surface-visible").textContent = `${decorated.visibleFeatures.length.toLocaleString()} / ${decorated.allFeatures.length.toLocaleString()}`;
  byId("surface-median").textContent = currency(median);
  byId("surface-low").textContent = `${Math.round((lowCount / Math.max(decorated.allFeatures.length, 1)) * 100)}%`;
  byId("surface-selected").textContent = state.selectedSurface?.barangay ?? "None";
  renderBarangayDetail();
}

function surfaceTooltip(props: SurfaceProperties): string {
  const range =
    props.price_q25 != null && props.price_q75 != null
      ? `<br>Range ${currency(props.price_q25)} – ${currency(props.price_q75)} /sqm`
      : "";
  const record = props.adm4_pcode ? barangayFeatures.barangays[props.adm4_pcode] : undefined;
  const access =
    record && record.mcrai.composite != null
      ? `<br>Overall access (MCRAI): ${record.mcrai.composite.toFixed(0)}`
      : "";
  return (
    `<strong>${escapeHtml(props.barangay)}</strong> · ${escapeHtml(props.lgu)}` +
    `<br>Median ${escapeHtml(props.price_label)}${range}${access}` +
    `<br><span style="opacity:0.82">${escapeHtml(props.confidence_label)} · click for features</span>`
  );
}

function renderBarangayDetail() {
  const target = byId("surface-detail");
  const props = state.selectedSurface;
  if (!props) {
    target.className = "empty";
    target.textContent = "Click a barangay to see the amenity scores and features behind its price.";
    return;
  }

  const record = props.adm4_pcode ? barangayFeatures.barangays[props.adm4_pcode] : undefined;
  const parts: string[] = [];
  parts.push(
    `<div class="bd-head"><strong>${escapeHtml(props.barangay)}</strong><span>${escapeHtml(props.lgu)}</span></div>`,
  );
  parts.push(
    `<div class="bd-price"><strong>${escapeHtml(props.price_label)}</strong>` +
      `<span>median · ${escapeHtml(surfaceMeta[state.surfaceKey].label)} surface</span></div>`,
  );
  const range =
    props.price_q25 != null && props.price_q75 != null
      ? `${currency(props.price_q25)} – ${currency(props.price_q75)} /sqm`
      : "—";
  parts.push(`<div class="bd-row"><span>Price range (q25–q75)</span><b>${range}</b></div>`);
  if (record) {
    parts.push(
      `<div class="bd-row"><span>Listings sampled</span><b>${record.n_listings}</b></div>` +
        `<div class="bd-row"><span>Actual listing median</span><b>${currency(record.listing_price_median)} /sqm</b></div>`,
    );
  }
  parts.push(`<div class="bd-row"><span>Confidence</span><b>${escapeHtml(props.confidence_label)}</b></div>`);

  if (!record) {
    parts.push(
      `<p class="bd-note">No listings fall inside this barangay, so its amenity profile can't be averaged. The price is interpolated from nearby barangays.</p>`,
    );
    target.className = "surface-detail";
    target.innerHTML = parts.join("");
    return;
  }

  parts.push(
    featureBlocksHtml(
      record.mcrai,
      record.dist,
      record.bir_zonal_rr_median,
      record.spatial_lag_price,
      `Amenity scores and distances are averaged over the ${record.n_listings} listing(s) inside this barangay — the location factors behind its price band.`,
    ),
  );

  target.className = "surface-detail";
  target.innerHTML = parts.join("");
}

function renderMarket() {
  clearDynamicLayers();
  listingLayer.addTo(map);
  poiLayer.addTo(map);
  setLayerVisibility(lguLayer, state.showLgu);
  renderBarangayOptions();
  renderNodeSizeControl();
  renderMarketLegend();
  const view = filteredListings();
  const poiView = filteredPois();
  renderListingLayer(view);
  renderPoiLayer(poiView);
  renderMarketMetrics(view, poiView);
  renderSelectedProperty();
  renderRanking();
}

function renderSurface() {
  clearDynamicLayers();
  setLayerVisibility(lguLayer, state.showSurfaceLgu);
  renderSurfaceLayer();
}

function renderPredictControls() {
  const cityEl = byId("predict-city");
  if (!state.predictPin) {
    cityEl.className = "predict-pill empty";
    cityEl.textContent = "Drop a pin on the map →";
  } else if (state.predictResolving) {
    cityEl.className = "predict-pill empty";
    cityEl.textContent = "Resolving location…";
  } else if (state.predictInside && state.predictCity) {
    cityEl.className = "predict-pill";
    cityEl.textContent = state.predictCity;
  } else {
    cityEl.className = "predict-pill empty";
    cityEl.textContent = "Outside Metro Cebu";
  }

  const bir = byId("predict-bir-readout");
  if (state.predictInside && state.predictBir != null) {
    bir.innerHTML = `${currency(state.predictBir)}<small>/ sqm · auto from location</small>`;
  } else if (state.predictPin && state.predictResolving) {
    bir.innerHTML = `<small>Estimating from location…</small>`;
  } else {
    bir.innerHTML = `<small>Set once a pin is inside Metro Cebu.</small>`;
  }

  const isLot = state.predictType === "Vacant Lot";
  const isCondo = state.predictType === "Condominium";
  byId("predict-area-label").textContent = isCondo
    ? "Floor area (sqm)"
    : isLot
      ? "Lot area (sqm)"
      : "Total area (sqm)";
  byId("predict-rooms").hidden = isLot;

  const overrideInput = byId<HTMLInputElement>("predict-bir-value");
  overrideInput.hidden = !state.predictBirOverride;
  if (
    state.predictBirOverride &&
    state.predictBirValue != null &&
    document.activeElement !== overrideInput
  ) {
    overrideInput.value = String(Math.round(state.predictBirValue));
  }

  const ready =
    state.predictInside &&
    Number.isFinite(state.predictArea) &&
    state.predictArea > 0 &&
    !state.predictLoading;
  byId<HTMLButtonElement>("predict-run").disabled = !ready;
}

function renderPredictResult() {
  const target = byId("predict-result");
  if (state.predictLoading) {
    target.className = "predict-result loading";
    target.textContent = "Predicting…";
    return;
  }
  if (state.predictError) {
    target.className = "predict-result";
    target.innerHTML = `<div class="result-error">${escapeHtml(state.predictError)}</div>`;
    return;
  }
  const r = state.predictResult;
  if (!r) {
    target.className = "empty";
    target.textContent = "Drop a pin inside Metro Cebu, then press Predict Price.";
    return;
  }

  const pct = (value: number | null) => (typeof value === "number" ? `${Math.round(value)}%` : "n/a");
  const parts: string[] = [];
  parts.push(
    `<div class="result-model">Model: <strong>${escapeHtml(r.stratum_label)}</strong> · ${escapeHtml(r.model_family)} ` +
      `(group-CV MdAPE ≈ ${pct(r.mdape)}, MAPE ≈ ${pct(r.mape)}, PE20 ≈ ${pct(r.pe20)})</div>`,
  );
  parts.push(`<strong class="result-price">${currency(r.price_per_sqm)}<span>predicted / sqm</span></strong>`);
  parts.push(`<div class="result-total">Total: ${currency(r.price_php)}</div>`);
  if (r.ci_available) {
    parts.push(
      `<div class="result-ci">Model range: ${currency(r.ci_low_per_sqm)} – ${currency(r.ci_high_per_sqm)} / sqm</div>`,
    );
  }
  if (r.mcrai_fallback) {
    parts.push(
      `<div class="result-warning">Location is outside the Metro Cebu training area — ` +
        `local accessibility features approximated from city averages.</div>`,
    );
  }

  const driverParts: string[] = ['<div class="driver-panel"><div class="driver-head">Price drivers</div>'];
  if (r.drivers.length) {
    for (const driver of r.drivers) {
      const up = driver.shap >= 0;
      const color = up ? "#e23e57" : "#2563eb";
      const sign = up ? "+" : "−";
      const width = Math.min(100, Math.max(8, Math.abs(driver.pct)));
      driverParts.push(
        `<div class="driver-row"><div class="driver-top">` +
          `<span class="driver-label">${escapeHtml(driver.label)}</span>` +
          `<span class="driver-impact" style="color:${color}">${sign}${Math.abs(driver.pct).toFixed(0)}%</span>` +
          `</div><div class="driver-track"><span class="driver-bar" style="width:${width.toFixed(0)}%;background:${color}"></span></div></div>`,
      );
    }
    driverParts.push(
      `<div class="driver-note">Approximate effect on price/sqm. Red raises the estimate, blue lowers it.</div>`,
    );
  } else if (r.driver_error) {
    driverParts.push(`<div class="driver-note">${escapeHtml(r.driver_error)}</div>`);
  }
  driverParts.push("</div>");
  parts.push(driverParts.join(""));

  target.className = "predict-result";
  target.innerHTML = parts.join("");
}

function refreshPredict() {
  renderPredictControls();
  renderPredictResult();
}

function renderPredict() {
  clearDynamicLayers();
  setLayerVisibility(lguLayer, true);
  state.predictNearby = state.predictPin ? nearbyListings(state.predictPin) : [];

  if (state.predictPin) {
    const { lat, lon } = state.predictPin;
    predictBufferLayer = L.circle([lat, lon], {
      radius: PREDICT_RADIUS_M,
      color: "#2563eb",
      weight: 1.4,
      fillColor: "#2563eb",
      fillOpacity: 0.06,
    }).addTo(map);

    predictNearbyLayer.clearLayers();
    for (const { listing, dist } of state.predictNearby) {
      L.circleMarker([listing.latitude, listing.longitude], {
        radius: 5,
        color: "#ffffff",
        weight: 1,
        fillColor: stratumColors[listing.stratum] ?? "#64748b",
        fillOpacity: 0.92,
      })
        .bindTooltip(
          `<strong>${listing.stratum}</strong> · ${currency(listing.pricePerSqm)} /sqm<br>${Math.round(dist)} m from pin`,
        )
        .addTo(predictNearbyLayer);
    }
    predictNearbyLayer.addTo(map);

    // Pin drawn last so it sits above the nearby points.
    predictMarker = L.circleMarker([lat, lon], {
      radius: 9,
      color: "#ffffff",
      weight: 3,
      fillColor: "#e23e57",
      fillOpacity: 1,
    }).addTo(map);
  }

  byId("page-title").textContent = "Property Price Predictor";
  byId("subtitle").textContent = state.predictPin
    ? `Pin ${state.predictPin.lat.toFixed(5)}, ${state.predictPin.lon.toFixed(5)} · ${state.predictNearby.length} listing(s) within 1 km`
    : "Click anywhere inside the six Metro Cebu LGUs.";
  byId("legend").innerHTML = "";
  refreshPredict();
  renderPredictNearby();
}

function renderPredictNearby() {
  const target = byId("predict-nearby");
  if (!state.predictPin) {
    target.hidden = true;
    return;
  }
  target.hidden = false;
  const near = state.predictNearby;
  if (!near.length) {
    target.innerHTML =
      `<div class="nearby-head">Nearby listings · 1 km</div>` +
      `<p class="bd-note">No actual ABT listings within 1 km of this pin.</p>`;
    return;
  }
  const rows = near
    .slice(0, 40)
    .map((item, idx) => {
      const listing = item.listing;
      const where = listing.barangay || listing.city;
      return (
        `<div class="nearby-row"><span class="nearby-rank">${idx + 1}</span>` +
        `<span class="nearby-main"><b>${currency(listing.pricePerSqm)} /sqm</b>` +
        `<span>${escapeHtml(listing.stratum)}${where ? ` · ${escapeHtml(where)}` : ""}</span></span>` +
        `<span class="nearby-dist">${Math.round(item.dist)} m</span></div>`
      );
    })
    .join("");
  const more = near.length > 40 ? `<p class="bd-note">Showing the 40 closest of ${near.length}.</p>` : "";
  target.innerHTML = `<div class="nearby-head">Nearby listings · ${near.length} within 1 km</div>${rows}${more}`;
}

async function resolvePin() {
  const pin = state.predictPin;
  if (!pin) return;
  state.predictResolving = true;
  refreshPredict();
  try {
    const response = await fetch(`/api/resolve?lat=${pin.lat}&lon=${pin.lon}`);
    const data = (await response.json()) as ResolveResponse;
    if (state.predictPin !== pin) return; // a newer pin superseded this lookup
    state.predictCity = data.city;
    state.predictInside = data.inside_metro;
    state.predictBir = data.bir_estimate;
    if (!state.predictBirOverride) state.predictBirValue = data.bir_estimate;
  } catch {
    if (state.predictPin !== pin) return;
    state.predictCity = null;
    state.predictInside = false;
    state.predictBir = null;
  } finally {
    if (state.predictPin === pin) {
      state.predictResolving = false;
      refreshPredict();
    }
  }
}

async function runPredict() {
  const pin = state.predictPin;
  if (!pin || !state.predictInside) return;
  const beds = state.predictBeds.trim();
  const baths = state.predictBaths.trim();
  const body = {
    lat: pin.lat,
    lon: pin.lon,
    property_type: state.predictType,
    area_sqm: state.predictArea,
    bedrooms: beds === "" ? null : Number(beds),
    bathrooms: baths === "" ? null : Number(baths),
    bir_override:
      state.predictBirOverride && state.predictBirValue ? state.predictBirValue : null,
  };
  state.predictLoading = true;
  state.predictError = null;
  refreshPredict();
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const payload = (await response.json().catch(() => ({}))) as { detail?: string };
      throw new Error(payload.detail ?? `Request failed (${response.status})`);
    }
    state.predictResult = (await response.json()) as PredictResponse;
  } catch (error) {
    state.predictResult = null;
    state.predictError = error instanceof Error ? error.message : "Prediction failed.";
  } finally {
    state.predictLoading = false;
    refreshPredict();
  }
}

function render() {
  renderViewChrome();
  if (state.view === "market") renderMarket();
  if (state.view === "surface") renderSurface();
  if (state.view === "predict") renderPredict();
}

function attachEvents() {
  byId("market-view").addEventListener("click", () => {
    state.view = "market";
    render();
  });
  byId("surface-view").addEventListener("click", () => {
    state.view = "surface";
    render();
  });
  byId("predict-view").addEventListener("click", () => {
    state.view = "predict";
    render();
  });
  byId<HTMLSelectElement>("lgu-filter").addEventListener("change", (event) => {
    state.lgu = (event.target as HTMLSelectElement).value;
    render();
  });
  byId<HTMLSelectElement>("barangay-filter").addEventListener("change", (event) => {
    state.barangay = (event.target as HTMLSelectElement).value;
    render();
  });
  byId<HTMLInputElement>("heatmap-toggle").addEventListener("change", (event) => {
    state.showHeatmap = (event.target as HTMLInputElement).checked;
    render();
  });
  byId<HTMLInputElement>("lgu-toggle").addEventListener("change", (event) => {
    state.showLgu = (event.target as HTMLInputElement).checked;
    render();
  });
  byId<HTMLInputElement>("poi-toggle").addEventListener("change", (event) => {
    state.showPois = (event.target as HTMLInputElement).checked;
    render();
  });
  byId<HTMLInputElement>("node-size-slider").addEventListener("input", (event) => {
    state.listingNodeSize = Number((event.target as HTMLInputElement).value);
    render();
  });
  byId<HTMLSelectElement>("surface-archetype").addEventListener("change", (event) => {
    state.surfaceKey = (event.target as HTMLSelectElement).value as SurfaceKey;
    state.selectedSurface = null;
    render();
  });
  byId<HTMLInputElement>("hide-low-confidence").addEventListener("change", (event) => {
    state.hideLowConfidence = (event.target as HTMLInputElement).checked;
    state.selectedSurface = null;
    render();
  });
  byId<HTMLInputElement>("surface-lgu-toggle").addEventListener("change", (event) => {
    state.showSurfaceLgu = (event.target as HTMLInputElement).checked;
    render();
  });
  byId<HTMLSelectElement>("predict-type").addEventListener("change", (event) => {
    state.predictType = (event.target as HTMLSelectElement).value;
    state.predictResult = null;
    state.predictError = null;
    refreshPredict();
  });
  byId<HTMLInputElement>("predict-area").addEventListener("input", (event) => {
    state.predictArea = Number((event.target as HTMLInputElement).value);
    state.predictResult = null;
    state.predictError = null;
    refreshPredict();
  });
  byId<HTMLInputElement>("predict-bedrooms").addEventListener("input", (event) => {
    state.predictBeds = (event.target as HTMLInputElement).value;
    state.predictResult = null;
  });
  byId<HTMLInputElement>("predict-bathrooms").addEventListener("input", (event) => {
    state.predictBaths = (event.target as HTMLInputElement).value;
    state.predictResult = null;
  });
  byId<HTMLInputElement>("predict-bir-override").addEventListener("change", (event) => {
    state.predictBirOverride = (event.target as HTMLInputElement).checked;
    if (state.predictBirOverride && state.predictBirValue == null) {
      state.predictBirValue = state.predictBir;
    }
    state.predictResult = null;
    refreshPredict();
  });
  byId<HTMLInputElement>("predict-bir-value").addEventListener("input", (event) => {
    state.predictBirValue = Number((event.target as HTMLInputElement).value);
    state.predictResult = null;
  });
  byId<HTMLButtonElement>("predict-run").addEventListener("click", () => {
    void runPredict();
  });
  map.on("click", (event: L.LeafletMouseEvent) => {
    if (state.view !== "predict") return;
    state.predictPin = {
      lat: Number(event.latlng.lat.toFixed(6)),
      lon: Number(event.latlng.lng.toFixed(6)),
    };
    state.predictCity = null;
    state.predictInside = false;
    state.predictBir = null;
    state.predictResult = null;
    state.predictError = null;
    renderPredict();
    void resolvePin();
  });

  for (const input of document.querySelectorAll<HTMLInputElement>('input[name="stratum"]')) {
    input.addEventListener("change", () => {
      state.strata = selectedCheckboxValues("stratum");
      render();
    });
  }
  for (const input of document.querySelectorAll<HTMLInputElement>('input[name="poi"]')) {
    input.addEventListener("change", () => {
      state.poiCategories = selectedCheckboxValues("poi");
      render();
    });
  }
}

async function init() {
  const [listingResponse, poiResponse, lguResponse, sdhResponse, condoResponse, vacantResponse] =
    await Promise.all([
      fetch("/data/listings.json"),
      fetch("/data/pois.json"),
      fetch("/data/lgu_boundaries.geojson"),
      fetch(`/data/${surfaceMeta.sdh.file}`),
      fetch(`/data/${surfaceMeta.condo.file}`),
      fetch(`/data/${surfaceMeta.vacant.file}`),
    ]);
  listings = (await listingResponse.json()) as Listing[];
  pois = (await poiResponse.json()) as Poi[];
  surfaces = {
    sdh: (await sdhResponse.json()) as SurfaceCollection,
    condo: (await condoResponse.json()) as SurfaceCollection,
    vacant: (await vacantResponse.json()) as SurfaceCollection,
  };
  const lguGeojson = await lguResponse.json();

  // Optional: barangay feature profiles power the Price Surface hover/click detail.
  // A failure here must never blank the Market Map or Price Surface, so it is loaded
  // separately and tolerated.
  try {
    const featuresResponse = await fetch("/data/barangay_features.json");
    if (featuresResponse.ok) {
      barangayFeatures = (await featuresResponse.json()) as BarangayFeatures;
    }
  } catch (error) {
    console.warn("Barangay feature detail unavailable:", error);
  }

  // interactive:false is critical — the LGU layer is brought to the front in the
  // Price Surface view to draw its borders over the choropleth. If it stayed
  // interactive its (transparent) polygons would swallow every click/hover before
  // the barangay layer underneath could receive them. As pure decoration, events
  // pass straight through to the barangay polygons (and the predictor's map click).
  lguLayer = L.geoJSON(lguGeojson, {
    interactive: false,
    style: {
      color: "#334155",
      weight: 1.7,
      fill: false,
    },
  }).addTo(map);

  renderLguOptions();
  renderBarangayOptions();
  attachEvents();
  render();
}

init().catch((error) => {
  console.error(error);
  byId("subtitle").textContent = "Unable to load exported app data.";
});
