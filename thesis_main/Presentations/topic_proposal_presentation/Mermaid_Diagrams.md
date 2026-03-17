# Mermaid Diagrams — Thesis Proposal Presentation

> Export each diagram as PNG → `thesis_main/Presentations/assets/`

---

## 1. Data Landscape → Use on **Slide 14** (Hybrid Data Strategy)

```mermaid
graph TB
    subgraph "Market Value Spectrum"
        direction TB
        CEILING["🔺 CEILING<br/>Online Listings<br/>(Asking Prices)"]
        TRUE["✅ TRUE MARKET VALUE<br/>(Estimated by Model)"]
        FLOOR["🔻 FLOOR<br/>BDO Foreclosures<br/>(Distressed Prices)"]
    end

    subgraph "Listing Sources"
        LC["LeeChiu<br/>390 listings<br/>(title, price, location, description)"]
        LN["LifeNavi<br/>~5,237 listings<br/>(price, area, BR, TB, description)"]
        LAM["Lamudi<br/>(Future scrape)"]
    end

    subgraph "Administrative & Macro"
        BIR["BIR Zonal Values<br/>(Per Barangay)"]
        BSP["BSP RPPI<br/>(Quarterly Index)"]
    end

    subgraph "Verified Transactions"
        BDO["BDO Foreclosures<br/>955 raw entries<br/>(~80-100 Cebu)"]
    end

    LC --> CEILING
    LN --> CEILING
    LAM --> CEILING
    BDO --> FLOOR
    BIR --> TRUE
    BSP --> TRUE
    CEILING -.->|"Bracket"| TRUE
    FLOOR -.->|"Bracket"| TRUE
```

---

## 2. Data Pipeline → Use on **Slide 15** (Data Pipeline)

```mermaid
flowchart LR
    subgraph "Stage 1: Ingest"
        A1["BDO Excel"] --> MERGE["Merge &<br/>Standardize"]
        A2["LeeChiu CSV<br/>(390 rows)"] --> MERGE
        A3["LifeNavi CSVs<br/>(~5,237 rows)"] --> MERGE
    end

    subgraph "Stage 2: Filter"
        MERGE --> F1["📍 Metro Cebu<br/>Only"]
        F1 --> F2["🏠 Residential<br/>Only"]
    end

    subgraph "Stage 3: Parse"
        F2 --> P1["Regex Extract:<br/>BR, TB, Area,<br/>Parking, Type"]
        P1 --> P2["Price Parsing:<br/>PHP → float"]
    end

    subgraph "Stage 4: Geocode"
        P2 --> G1["Address →<br/>Lat/Lon"]
        G1 --> G2["Assign<br/>Barangay"]
    end

    subgraph "Stage 5: Augment"
        G2 --> E1["Proximity:<br/>CBD, IT Park,<br/>CBRT Stations"]
        E1 --> E2["Amenity Score:<br/>OSM POIs<br/>within 1km"]
        E2 --> E3["Text Features:<br/>TF-IDF from<br/>descriptions"]
        E3 --> E4["Admin + Macro:<br/>BIR Zonal,<br/>BSP RPPI"]
    end

    E4 --> OUT["📊 Model-Ready<br/>Dataset"]

    style OUT fill:#2d6a4f,color:#fff,stroke:#1b4332
```
