# QGIS MCP Server — Research & Setup Guide

## Summary

Setting up a **QGIS MCP server** is straightforward on your Mac. No Docker is needed — it's a native **QGIS plugin + Python MCP server** combo. Your system already has all prerequisites installed.

---

## System Check ✅

| Prerequisite | Status | Details |
|:---|:---|:---|
| QGIS 3.x | ✅ Installed | `/Applications/QGIS.app` |
| `uv` package manager | ✅ Installed | `uv 0.10.3` at `/Users/nicoestreba/miniconda3/bin/uv` |
| Python 3.10+ | ✅ Assumed | (via miniconda3) |
| QGIS profile directory | ✅ Exists | `~/Library/Application Support/QGIS/QGIS3/profiles/` |
| QGIS plugins directory | ⚠️ Not yet created | Will be created on first QGIS launch or manually |
| Existing MCP config | ✅ Found | `~/.gemini/antigravity/mcp_config.json` (8 servers, no QGIS entry yet) |

> [!NOTE]
> The Docker setup you remember was likely the **GitHub MCP server** (`ghcr.io/github/github-mcp-server`), not QGIS. The QGIS MCP server is purely local — no Docker required.

---

## How It Works

The QGIS MCP server has **two components**:

```
┌─────────────────┐     socket      ┌──────────────┐     MCP      ┌──────────────┐
│  QGIS Desktop   │ ◄────────────►  │  QGIS Plugin │ ◄──────────► │  MCP Server  │
│  (GUI)          │                  │  (socket svr)│              │  (Python/uv) │
└─────────────────┘                  └──────────────┘              └──────────────┘
                                                                         ▲
                                                                         │ MCP Protocol
                                                                         ▼
                                                                   ┌──────────────┐
                                                                   │  Antigravity │
                                                                   │  (LLM Client)│
                                                                   └──────────────┘
```

1. **QGIS Plugin** — Installed inside QGIS, creates a socket server to receive commands
2. **MCP Server** — Python script run via `uv`, implements the Model Context Protocol

### Available Tools (once connected)
- `ping` — Check connectivity
- `get_qgis_info` — Get QGIS version/installation info
- `load_project` / `create_new_project` / `save_project` — Project management
- `add_vector_layer` / `add_raster_layer` — Layer management
- `get_layers` / `remove_layer` / `zoom_to_layer` — Layer operations
- `get_layer_features` — Retrieve features from vector layers
- `execute_processing` — Run QGIS Processing Toolbox algorithms
- `render_map` — Render current map view to image
- `execute_code` — Run arbitrary PyQGIS code ⚠️

---

## Setup Steps

### Step 1: Clone the Repository

```bash
cd ~/Projects  # or wherever you keep repos
git clone https://github.com/jjsantos01/qgis_mcp.git
```

### Step 2: Install the QGIS Plugin

```bash
# Create the plugins directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins

# Copy the plugin
cp -r ~/Projects/qgis_mcp/qgis_mcp_plugin ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
```

Then in QGIS:
1. Restart QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **"QGIS MCP"**
4. Enable the checkbox

### Step 3: Add to Antigravity MCP Config

Add this entry to `~/.gemini/antigravity/mcp_config.json`:

```json
"qgis": {
    "command": "/Users/nicoestreba/miniconda3/bin/uv",
    "args": [
        "--directory",
        "/Users/nicoestreba/Projects/qgis_mcp/src/qgis_mcp",
        "run",
        "qgis_mcp_server.py"
    ],
    "env": {}
}
```

### Step 4: Start the Connection

1. In QGIS: **Plugins → QGIS MCP → QGIS MCP** → Click **"Start Server"**
2. Restart Antigravity (or the MCP client) to pick up the new config
3. The QGIS MCP tools should now appear

---

## Potential Use for Your Thesis

With QGIS MCP running, you could use Antigravity to:

| Task | QGIS MCP Tool |
|:---|:---|
| Load Metro Cebu property data | `add_vector_layer` |
| Load HDX building footprints | `add_vector_layer` |
| Compute spatial joins (proximity) | `execute_processing` |
| Generate choropleth maps | `execute_code` (PyQGIS) |
| Render publication-quality maps | `render_map` |
| Calculate building density | `execute_processing` / `execute_code` |
| Create interactive map output | `execute_code` (PyQGIS + QGIS2Web) |

---

## GIS Data Status — HDX Philippines Buildings

Per [GIS_Data_Notes.md](file:///Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA%26P/classes/Data%20Science/16%20Thesis/thesis_main/Data/GIS_Data_Notes.md):

- **Source**: [HOTOSM Philippines Buildings](https://data.humdata.org/dataset/hotosm_phl_buildings)
- **Content**: ~11.6M building footprints from OpenStreetMap
- **Formats**: GeoJSON, KML, SHP, Geopackage, CSV

> [!IMPORTANT]
> **Data NOT downloaded yet.** The markdown file contains only notes about the dataset. No GIS data files (`.shp`, `.geojson`, `.gpkg`) were found anywhere in the thesis project directory or Google Drive.
>
> **Next step**: Download the Shapefile or Geopackage for Cebu from the HDX link, then load it into QGIS.

---

## Questions for You

1. **Clone location**: Where should I clone the `qgis_mcp` repo? I assumed `~/Projects/` — is that correct, or do you have a preferred location?
2. **QGIS version**: Can you confirm your QGIS version? The MCP plugin was tested on 3.22. Open QGIS → **Help → About** to check.
3. **Proceed with setup?** Shall I go ahead and clone the repo, install the plugin, and update your MCP config?
