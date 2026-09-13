"""Statistical tests used throughout the analysis: correlation with bootstrap CI,
the analytic null-noise band, and the permutation test for spatial overrepresentation."""

import numpy as np
from scipy.stats import spearmanr, mannwhitneyu


def spearman_with_bootstrap_ci(x, y, n_boot=10000, ci=95, seed=0):
    """
    Spearman correlation with a bootstrap confidence interval (resampling pairs
    with replacement), in addition to the standard p-value.

    Returns: dict with rho, p_value, ci_lower, ci_upper, n
    """
    x, y = np.asarray(x), np.asarray(y)
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[mask], y[mask]
    n = len(x)

    rho, pval = spearmanr(x, y)

    rng = np.random.default_rng(seed)
    boot_rhos = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_rhos[i] = spearmanr(x[idx], y[idx])[0]

    lower = np.percentile(boot_rhos, (100 - ci) / 2)
    upper = np.percentile(boot_rhos, 100 - (100 - ci) / 2)

    return {"rho": rho, "p_value": pval, "ci_lower": lower, "ci_upper": upper, "n": n}


def null_noise_band(n, ci=95):
    """
    Analytic approximation of the null-hypothesis (rho=0) sampling range for
    Spearman's rho at sample size n, using SE ~= 1/sqrt(n-3).
    Used to show that a set of rho estimates (e.g. across spatial scales) is
    indistinguishable from noise, without needing to re-permute each one.

    Returns: half-width of the band (i.e. the band is [-half_width, +half_width])
    """
    z = 1.96 if ci == 95 else None
    if z is None:
        raise ValueError("Only ci=95 is implemented; add other z-values if needed.")
    se = 1 / np.sqrt(n - 3)
    return z * se


def permutation_test_region_overlap(background_values, observed_subset_values,
                                      threshold, n_permutations=10000, seed=0):
    """
    Tests whether a subset of points (e.g. BLM debris-fail points) falls inside
    a high-value region (e.g. top-k% RTS tiles) more than chance, by comparing
    against random draws from the same background distribution.

    background_values: 1D array of all valid values in the study area (e.g. all
        RTS tiles in the core region), used to build the null distribution and
        to define `threshold` (usually a percentile of this array).
    observed_subset_values: the actual values (from the same value space, e.g.
        RTS at BLM debris-fail point locations) whose overrepresentation is
        being tested.
    threshold: values above this count as "in the high region".

    Returns: dict with observed_frac, null_mean, null_std, p_value (one-sided,
        tests whether observed is GREATER than chance)
    """
    n_subset = len(observed_subset_values)
    observed_frac = np.mean(np.asarray(observed_subset_values) > threshold)

    rng = np.random.default_rng(seed)
    null_fracs = np.empty(n_permutations)
    for i in range(n_permutations):
        draw = rng.choice(background_values, size=n_subset, replace=True)
        null_fracs[i] = np.mean(draw > threshold)

    p_value = np.mean(null_fracs >= observed_frac)

    return {
        "observed_frac": observed_frac,
        "null_mean": null_fracs.mean(),
        "null_std": null_fracs.std(),
        "p_value": p_value,
        "n_subset": n_subset,
    }


def compare_groups(group_a, group_b, label_a="group A", label_b="group B"):
    """
    Compares two groups (e.g. debris values for low-RTS vs high-RTS points)
    using a Mann-Whitney U test, and reports descriptive stats for both.

    Returns: dict with means, medians, n's, statistic, and p_value
    """
    group_a, group_b = np.asarray(group_a), np.asarray(group_b)
    stat, pval = mannwhitneyu(group_a, group_b, alternative="two-sided")

    return {
        f"{label_a}_mean": group_a.mean(), f"{label_a}_median": np.median(group_a), f"{label_a}_n": len(group_a),
        f"{label_b}_mean": group_b.mean(), f"{label_b}_median": np.median(group_b), f"{label_b}_n": len(group_b),
        "statistic": stat, "p_value": pval,
    }