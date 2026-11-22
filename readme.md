# AURORA — Satellite Flood Intelligence & Community Impact Assessment

**Earth Observation | Satellite Applications | Disaster Management**

AURORA is an AI-powered satellite flood intelligence research prototype designed to analyse historical satellite observations and identify experimental flood-change candidate regions.

**Pilot Study Area:** Dibrugarh, Assam, India

---

## 1. Overview

Flooding can rapidly transform landscapes and affect communities, infrastructure, and essential services. Satellite imagery provides valuable geospatial information for understanding these changes.

AURORA uses historical Sentinel-1 Synthetic Aperture Radar (SAR) imagery to identify potential flood-related surface changes and display the resulting candidate regions through an interactive geospatial dashboard.

The platform combines satellite data processing, geospatial analysis, and web-based visualization in one workflow.

## 2. Key Features

- Historical Sentinel-1 SAR imagery analysis.
- VV and VH backscatter change detection.
- Permanent water body masking.
- Terrain slope filtering.
- Connected-pixel filtering.
- Experimental flood candidate polygon generation.
- Interactive MapLibre geospatial dashboard.
- Polygon inspection through map popups.
- GeoJSON download and export.
- Before-and-after satellite imagery comparison.
- FastAPI backend with health and flood-data endpoints.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | CSS |
| Mapping | MapLibre GL |
| Backend | Python, FastAPI |
| Satellite processing | Google Earth Engine |
| Satellite data | Sentinel-1 SAR |
| Geospatial output | GeoJSON |
| Development | VS Code |

## 4. Satellite Analysis Methodology

The prototype uses historical Sentinel-1 GRD observations.

**Study configuration:**
- Location: Dibrugarh, Assam
- Before observation: 24 June 2024
- After observation: 6 July 2024
- Satellite mode: IW
- Orbit: Ascending
- Relative orbit: 143
- Polarizations: VV and VH
- Analysis buffer: 10 km

**Experimental detection criteria:**

| Parameter | Criterion |
|---|---|
| VV backscatter change | Below -1.0 dB |
| VH backscatter change | Below -1.5 dB |
| Permanent water | Occurrence ≥90% excluded |
| Terrain slope | ≥5° excluded |
| Connected pixels | Minimum 8 |

The resulting candidate regions are converted into GeoJSON for visualization and inspection.

## 5. System Architecture

```text
Sentinel-1 SAR Data
        |
        v
Google Earth Engine
        |
        v
SAR Pre-processing
        |
        v
Backscatter Change Detection
        |
        v
Water & Terrain Filtering
        |
        v
Candidate Polygon Generation
        |
        v
GeoJSON Output
        |
        v
FastAPI Backend
        |
        v
React + MapLibre Dashboard
        |
        v
Interactive Analysis & Export
```

## 6. Installation and Setup

### Prerequisites

- Python 3.11
- Node.js and npm
- Git
- Google Earth Engine account and project access

### Clone the repository

```bash
git clone https://github.com/tenster2008/aurora-satellite-disaster-intelligence.git

cd aurora-satellite-disaster-intelligence
```

### Backend setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

Authenticate Google Earth Engine if required:

```powershell
earthengine authenticate
```

Start the backend:

```powershell
python -m uvicorn app.main:app --reload --app-dir backend
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Frontend setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

`http://localhost:5173`

## 7. API Endpoints

| Endpoint | Purpose |
|---|---|
| `/api/v1/health` | Backend health status |
| `/api/v1/flood/summary` | Flood candidate summary |
| `/api/v1/flood/extent` | GeoJSON candidate polygons |

## 8. Current Prototype Results

- 473 experimental candidate polygons generated for the pilot analysis.
- Interactive map visualization implemented.
- Polygon inspection and popup functionality implemented.
- GeoJSON export successfully tested.
- Historical SAR image comparison implemented.
- Backend health and summary endpoints operational.

## 9. Limitations and Future Scope

AURORA is currently a historical flood-assessment research prototype.

The following capabilities are not yet implemented:

- Independent ground-truth validation of candidate polygons.
- Population exposure assessment.
- Flood susceptibility modelling.
- Infrastructure impact assessment.
- Live flood monitoring and early-warning capabilities.

The detected polygons must not be interpreted as confirmed flood boundaries. SAR backscatter changes can also result from non-flood-related surface conditions.

Future development can integrate population datasets, infrastructure information, historical flood records, and validated machine-learning models.

## 10. Project Information

**Project:** AURORA  
**Domain:** Earth Observation & Satellite Applications  
**Pilot Location:** Dibrugarh, Assam, India  
**Project Type:** Hackathon Research Prototype

---

*Turning satellite observations into actionable geospatial evidence.*
