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
  price_per_sqm: number;
  price_label: string;
  confidence_label: string;
  point_count: number;
  low_confidence?: boolean;
  fillColor?: string;
  classLabel?: string;
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
};

let listings: Listing[] = [];
let pois: Poi[] = [];
let surfaces: Record<SurfaceKey, SurfaceCollection> = {} as Record<SurfaceKey, SurfaceCollection>;
let lguLayer: L.GeoJSON | null = null;
let listingLayer = L.layerGroup();
let poiLayer = L.layerGroup();
let surfaceLayer: L.GeoJSON | null = null;
let predictMarker: L.CircleMarker | null = null;

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

function renderSelectedProperty() {
  const target = byId("selected-property");
  const listing = listings.find((item) => item.propertyId === state.selectedId);
  if (!listing) {
    target.className = "empty";
    target.textContent = "Select a listing on the map.";
    return;
  }
  target.className = "selection";
  target.innerHTML = `
    <strong>${currency(listing.pricePerSqm)} <span>/ sqm listed</span></strong>
    <p>${listing.stratum} · ${listing.propertyType}</p>
    <p>${listing.barangay ? `${listing.barangay}, ` : ""}${listing.city}</p>
    <p>${listing.address || "No address text"}</p>
    <p>${listing.areaSqm ? `${listing.areaSqm.toLocaleString()} sqm` : ""}</p>
  `;
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
      layer.bindTooltip(
        `<strong>${props.barangay}</strong><br>${props.lgu}<br><strong>${props.price_label}</strong><br>${props.confidence_label}<br>${props.point_count} grid cells aggregated`,
      );
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
  if (state.predictPin) {
    predictMarker = L.circleMarker([state.predictPin.lat, state.predictPin.lon], {
      radius: 9,
      color: "#ffffff",
      weight: 3,
      fillColor: "#e23e57",
      fillOpacity: 1,
    }).addTo(map);
  }
  byId("page-title").textContent = "Property Price Predictor";
  byId("subtitle").textContent = state.predictPin
    ? `Pin ${state.predictPin.lat.toFixed(5)}, ${state.predictPin.lon.toFixed(5)}`
    : "Click anywhere inside the six Metro Cebu LGUs.";
  byId("legend").innerHTML = "";
  refreshPredict();
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
  const [listingResponse, poiResponse, lguResponse, sdhResponse, condoResponse, vacantResponse] = await Promise.all([
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

  lguLayer = L.geoJSON(lguGeojson, {
    style: {
      color: "#334155",
      weight: 1.7,
      fillOpacity: 0,
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
