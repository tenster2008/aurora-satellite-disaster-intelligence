
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# AURORA BACKEND API
# ==========================================

app = FastAPI(
    title="AURORA API",
    description="Satellite Flood Intelligence and Community Impact Assessment",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Data directory
DATA_DIR = Path(__file__).resolve().parent / "data"

FLOOD_FILE = DATA_DIR / "flood_extent.geojson"
EXPOSURE_FILE = DATA_DIR / "exposure_summary.json"


def load_json(path: Path):
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        raise HTTPException(
            status_code=500,
            detail=f"Could not read data file: {path.name}"
        )


# ==========================================
# GENERAL ENDPOINTS
# ==========================================

@app.get("/")
def home():
    return {
        "project": "AURORA",
        "message": "Flood Intelligence Platform",
        "status": "running",
        "version": "1.1.0"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "backend": "operational"
    }


@app.get("/api/v1/regions")
def regions():
    return {
        "regions": [
            {
                "id": "DIB-001",
                "name": "Dibrugarh",
                "state": "Assam",
                "country": "India"
            }
        ]
    }


# ==========================================
# FLOOD DETECTION ENDPOINTS
# ==========================================

@app.get("/api/v1/flood/extent")
def flood_extent():

    data = load_json(FLOOD_FILE)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Flood extent data is not available yet."
        )

    if data.get("type") != "FeatureCollection":
        raise HTTPException(
            status_code=500,
            detail="Invalid GeoJSON format."
        )

    return data


@app.get("/api/v1/flood/summary")
def flood_summary():

    data = load_json(FLOOD_FILE)

    if data is None:
        return {
            "data_status": "not_available",
            "message": "Flood detection has not been processed."
        }

    features = data.get("features", [])

    return {
        "data_status": "available",
        "region": "Dibrugarh, Assam, India",
        "satellite": "Sentinel-1 GRD",
        "baseline_date": "2024-06-24",
        "comparison_date": "2024-07-06",
        "candidate_polygon_count": len(features),
        "classification_status": "experimental",
        "validation_status": "pending",
        "output_file": FLOOD_FILE.name
    }


# ==========================================
# EXPOSURE ENDPOINTS
# ==========================================

@app.get("/api/v1/exposure/summary")
def exposure():

    data = load_json(EXPOSURE_FILE)

    if data is None:
        return {
            "data_status": "not_available",
            "message": "Exposure data is awaiting processing."
        }

    return data


# ==========================================
# SYSTEM STATUS
# ==========================================

@app.get("/api/v1/system")
def system():

    flood_available = FLOOD_FILE.exists()
    exposure_available = EXPOSURE_FILE.exists()

    return {
        "project": "AURORA",
        "modules": {
            "satellite": (
                "experimental_data_available"
                if flood_available
                else "awaiting_data"
            ),
            "machine_learning": "awaiting_model",
            "exposure": (
                "data_available"
                if exposure_available
                else "awaiting_data"
            )
        }
    }
