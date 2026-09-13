"""GEE data fetching utilities: single-point patches, bulk rasters, disk-backed caching."""

import os
import pickle
import numpy as np
import ee


def get_patch(lat, lon, start_date, end_date, buffer_m=35, bands=("B2", "B3", "B4", "B8")):
    """Fetch the least-cloudy Sentinel-2 patch for a single point and date range."""
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(buffer_m).bounds()

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )
    if collection.size().getInfo() == 0:
        return None

    image = collection.first().select(list(bands))
    try:
        sampled = image.sampleRectangle(region=region, defaultValue=0)
        arrays = [np.array(sampled.get(b).getInfo()) for b in bands]
        return np.stack(arrays, axis=-1).astype(np.float32)
    except Exception as e:
        print(f"Failed at ({lat},{lon}): {e}")
        return None


def get_patch_cached(cache_dir, site_id, window_name, lat, lon, start_date, end_date, buffer_m=35):
    """Disk-cached wrapper around get_patch(). Survives Colab disconnects."""
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = f"{site_id}__{window_name}__buffer{buffer_m}.pkl"
    cache_path = os.path.join(cache_dir, cache_key)

    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    patch = get_patch(lat, lon, start_date, end_date, buffer_m=buffer_m)
    with open(cache_path, "wb") as f:
        pickle.dump(patch, f)
    return patch


def fetch_bulk_raster_cached(cache_dir, region, lat_min, lat_max, lon_min, lon_max,
                              window_name, start_date, end_date, scale=10, max_chunk_px=450):
    """
    Fetch a full-area raster in chunks (GEE sampleRectangle caps at 262144 px),
    using a mosaic (not a single least-cloudy image) so the result isn't
    truncated by individual Sentinel-2 granule footprint boundaries.
    """
    os.makedirs(cache_dir, exist_ok=True)
    manifest_path = os.path.join(cache_dir, f"bulk_{window_name}_scale{scale}_manifest.pkl")
    if os.path.exists(manifest_path):
        with open(manifest_path, "rb") as f:
            return pickle.load(f)

    mid_lat = (lat_min + lat_max) / 2
    m_per_deg_lat = 111_000
    m_per_deg_lon = 111_000 * np.cos(np.radians(mid_lat))
    total_rows = int((lat_max - lat_min) * m_per_deg_lat / scale)
    total_cols = int((lon_max - lon_min) * m_per_deg_lon / scale)

    n_row_chunks = max(1, -(-total_rows // max_chunk_px))
    n_col_chunks = max(1, -(-total_cols // max_chunk_px))

    lat_edges = np.linspace(lat_max, lat_min, n_row_chunks + 1)
    lon_edges = np.linspace(lon_min, lon_max, n_col_chunks + 1)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start_date, end_date)
    )
    image = (
        collection.sort("CLOUDY_PIXEL_PERCENTAGE", False)
        .mosaic()
        .select(["B2", "B3", "B4", "B8"])
        .reproject(crs="EPSG:32611", scale=scale)
    )

    row_bands = []
    for i in range(n_row_chunks):
        col_chunks = []
        for j in range(n_col_chunks):
            chunk_path = os.path.join(cache_dir, f"bulk_{window_name}_scale{scale}_chunk_{i}_{j}.pkl")
            if os.path.exists(chunk_path):
                with open(chunk_path, "rb") as f:
                    chunk_arr = pickle.load(f)
            else:
                sub_region = ee.Geometry.Rectangle(
                    [lon_edges[j], lat_edges[i + 1], lon_edges[j + 1], lat_edges[i]]
                )
                sampled = image.sampleRectangle(region=sub_region, defaultValue=0)
                arrays = [np.array(sampled.get(b).getInfo()) for b in ["B2", "B3", "B4", "B8"]]
                chunk_arr = np.stack(arrays, axis=-1).astype(np.float32)
                with open(chunk_path, "wb") as f:
                    pickle.dump(chunk_arr, f)
            col_chunks.append(chunk_arr)

        min_h = min(c.shape[0] for c in col_chunks)
        row_bands.append(np.concatenate([c[:min_h] for c in col_chunks], axis=1))

    min_w = min(r.shape[1] for r in row_bands)
    raster = np.concatenate([r[:, :min_w] for r in row_bands], axis=0)

    with open(manifest_path, "wb") as f:
        pickle.dump(raster, f)
    return raster