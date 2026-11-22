
import ee
import urllib.request
from pathlib import Path

# Initialize the already authenticated Earth Engine project
ee.Initialize(project="fifth-legacy-496207-v9")

# Dibrugarh study area
point = ee.Geometry.Point([94.912, 27.472])
region = point.buffer(10000).bounds()

# Sentinel-1 collection
collection = (
    ee.ImageCollection("COPERNICUS/S1_GRD")
    .filterBounds(region)
    .filter(ee.Filter.eq("instrumentMode", "IW"))
    .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
    .filter(ee.Filter.eq("relativeOrbitNumber_start", 143))
    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
)

# Output folder
project_root = Path(__file__).resolve().parents[3]
output_dir = project_root / "frontend" / "public" / "satellite"
output_dir.mkdir(parents=True, exist_ok=True)

# Actual satellite acquisition dates
dates = [
    ("before", "2024-06-24", "2024-06-25"),
    ("after", "2024-07-06", "2024-07-07"),
]

for label, start, end in dates:
    print(f"\nProcessing {label}: {start}")

    images = collection.filterDate(start, end)
    count = images.size().getInfo()

    print("Matching satellite scenes:", count)

    if count == 0:
        raise RuntimeError(f"No Sentinel-1 scenes found for {start}")

    image = images.mosaic().clip(region)

    # VV / VH false-colour SAR visualisation
    params = {
        "region": region,
        "dimensions": 1200,
        "format": "png",
        "bands": ["VV", "VH", "VV"],
        "min": [-25, -30, -25],
        "max": [-5, -10, -5],
    }

    url = image.getThumbURL(params)

    output_file = output_dir / f"{label}.png"
    urllib.request.urlretrieve(url, str(output_file))

    print("Saved:", output_file)

print("\nSUCCESS: Both satellite images generated.")
