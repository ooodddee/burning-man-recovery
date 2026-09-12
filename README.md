# Recovery is Measurement-Dependent: Satellite Vision vs. Ground-Truth Debris Inspection at Black Rock City (2023)

This repository contains the data and code for a case study examining whether satellite-based visual change detection and official ground-truth debris inspection measure the same thing when assessing environmental "recovery" after a large temporary event (Burning Man 2023, Black Rock City, NV).

## Summary

Using Sentinel-2 imagery and a DINOv2-based visual change score (Residual Trace Score, RTS), we compare satellite-detected visual change against BLM's 2023 Post-Event Inspection (PEI) debris density measurements at 33 georeferenced monitoring points. We find no significant correlation between the two (Spearman rho = 0.056, p = 0.758), a result that is robust across spatial scales (10-50m), holds at the whole-city spatial scale (permutation test, all p > 0.6), and is not explained by three tested mechanistic hypotheses (activity intensity, baseline texture heterogeneity, absolute debris quantity). We argue this reflects a genuine construct mismatch between two different operationalizations of "recovery," rather than a simple measurement error or resolution artifact.

## Repository structure

```
data/         Raw and processed data (BLM PEI points, control points)
notebooks/    Analysis notebooks, numbered in pipeline order
src/          Reusable Python modules imported by the notebooks
figures/      Final figures used in the paper
results/      Cached intermediate result tables (CSV)
```

## Reproducing the analysis

1. Install dependencies: `pip install -r requirements.txt`
2. You will need:
   - A Google Earth Engine account and project (for Sentinel-2 access)
   - Access to a GPU-enabled runtime is recommended for DINOv2 feature extraction (Colab works)
3. Run the notebooks in `notebooks/` in numeric order. Each notebook caches its outputs to `results/` so later notebooks can be re-run independently once earlier ones have completed.

## Data sources

- Sentinel-2 Surface Reflectance imagery via Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`)
- BLM 2023 Post-Event Inspection report (public; see `data/DATA_DICTIONARY.md` for provenance and the specific coordinate/measurement corrections applied)

## Citation

If you use this code or data, please cite:

```
[citation to be added upon preprint/publication]
```

## License

Code is released under the MIT License (see `LICENSE`). Data derived from the BLM Post-Event Inspection report is public record; see `data/DATA_DICTIONARY.md` for details on how it was extracted and any corrections applied.
