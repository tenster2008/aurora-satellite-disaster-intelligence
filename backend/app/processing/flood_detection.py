
import ee
import json
import sys
import traceback
from pathlib import Path

# =====================================================
# AURORA - HISTORICAL FLOOD DETECTION ENGINE
# Study Area: Dibrugarh, Assam, India
# Satellite: Sentinel-1 GRD
# Comparison: 24 June 2024 vs 6 July 2024
# =====================================================

PROJECT_ID = "fifth-legacy-496207-v9"

CENTER = [94.912, 27.472]
BUFFER_METERS = 10000

PRE_DATE = "2024-06-24"
POST_DATE = "2024-07-06"

# Save output inside backend/app/data/
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def log(message):
    print(message, flush=True)


def initialize_earth_engine():
    log("\n[1/7] Connecting to Google Earth Engine...")

    ee.Initialize(project=PROJECT_ID)

    log("Earth Engine connected successfully.")


def create_roi():
    log("\n[2/7] Creating Dibrugarh study area...")

    roi = ee.Geometry.Point(CENTER).buffer(BUFFER_METERS)

    log("Study area created: 10 km radius.")

    return roi


def get_collection(start_date, end_date, roi):

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .filter(ee.Filter.eq("relativeOrbitNumber_start", 143))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VH"
            )
        )
        .select(["VV", "VH"])
    )

    return collection


def create_observation(collection, roi, label):

    count = collection.size().getInfo()

    log(f"{label}: {count} Sentinel-1 scenes found.")

    if count == 0:
        raise RuntimeError(
            f"No Sentinel-1 scenes found for {label}. "
            "Check dates, orbit and study area."
        )

    # Combine the available image slices.
    image = collection.sort("sliceNumber").mosaic()

    return image.clip(roi)


def detect_flood_candidates(pre, post, roi):

    log("\n[4/7] Calculating Sentinel-1 backscatter changes...")

    vv_change = (
        post.select("VV")
        .subtract(pre.select("VV"))
        .rename("VV_change")
    )

    vh_change = (
        post.select("VH")
        .subtract(pre.select("VH"))
        .rename("VH_change")
    )

    # Experimental backscatter-change thresholds.
    vv_candidate = vv_change.lt(-1.0)
    vh_candidate = vh_change.lt(-1.5)

    # Exclude frequently observed permanent water.
    permanent_water = (
        ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
        .select("occurrence")
        .gte(90)
    )

    # Exclude steep terrain.
    elevation = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(elevation)

    suitable_terrain = slope.lt(5)

    # Combine all initial conditions.
    candidates = (
        vv_candidate
        .And(vh_candidate)
        .And(permanent_water.Not())
        .And(suitable_terrain)
        .rename("flood_candidate")
    )

    # Remove isolated candidate pixels.
    connected = candidates.selfMask()

    connected_count = connected.connectedPixelCount(
        maxSize=100,
        eightConnected=True
    )

    candidates = (
        connected
        .updateMask(connected_count.gte(8))
        .rename("flood_candidate")
        .toByte()
        .clip(roi)
    )

    return candidates, vv_change, vh_change


def calculate_statistics(vv_change, vh_change, roi):

    log("\n[5/7] Calculating backscatter statistics...")

    combined = ee.Image.cat([
        vv_change,
        vh_change
    ])

    statistics = combined.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        maxPixels=100000000,
        tileScale=4
    ).getInfo()

    return statistics


def export_geojson(candidate_image, roi):

    log("\n[6/7] Converting candidate raster into polygons...")

    # Ensure the first band is an integer label band.
    label_image = (
        candidate_image
        .select("flood_candidate")
        .toInt()
    )

    vectors = label_image.reduceToVectors(
        reducer=ee.Reducer.countEvery(),
        geometry=roi,
        scale=30,
        geometryType="polygon",
        eightConnected=True,
        labelProperty="class",
        maxPixels=100000000,
        tileScale=4,
        bestEffort=True
    )

    # Retrieve the vector features.
    features = vectors.getInfo()

    geojson = {
        "type": "FeatureCollection",
        "features": features.get("features", [])
    }

    output_file = OUTPUT_DIR / "flood_extent.geojson"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(geojson, file)

    return output_file, len(geojson["features"])


def run_flood_detection():

    log("\n========================================")
    log("       AURORA FLOOD DETECTION ENGINE")
    log("========================================")

    initialize_earth_engine()

    roi = create_roi()

    # PRE-FLOOD BASELINE
    log("\n[3/7] Preparing June 24 baseline...")

    pre_collection = get_collection(
        PRE_DATE,
        "2024-06-25",
        roi
    )

    pre = create_observation(
        pre_collection,
        roi,
        "PRE-FLOOD"
    )

    # POST-FLOOD COMPARISON
    log("\nPreparing July 6 comparison...")

    post_collection = get_collection(
        POST_DATE,
        "2024-07-07",
        roi
    )

    post = create_observation(
        post_collection,
        roi,
        "POST-FLOOD"
    )

    # CLASSIFICATION
    log("\nRunning flood-candidate classification...")

    candidates, vv_change, vh_change = detect_flood_candidates(
        pre,
        post,
        roi
    )

    # STATISTICS
    statistics = calculate_statistics(
        vv_change,
        vh_change,
        roi
    )

    log("\nMean backscatter changes (dB):")
    log(json.dumps(statistics, indent=4))

    # GEOJSON EXPORT
    output_file, polygon_count = export_geojson(
        candidates,
        roi
    )

    log("\n[7/7] Processing completed.")
    log("\n========================================")
    log("         AURORA PROCESSING REPORT")
    log("========================================")

    log(f"Candidate polygons: {polygon_count}")
    log(f"Output file: {output_file}")
    log(f"Output exists: {output_file.exists()}")

    log("\nIMPORTANT:")
    log(
        "This is an experimental flood-candidate layer. "
        "It is not a validated flood map."
    )

    log("Independent validation is required.")


if __name__ == "__main__":

    try:
        run_flood_detection()

    except Exception as error:

        log("\n========================================")
        log("AURORA PROCESSING FAILED")
        log("========================================")

        log(f"Error: {error}")

        traceback.print_exc()

        sys.exit(1)
