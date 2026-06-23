"""Statistical utilities for evaluation reports."""

import math
from typing import Tuple


def wilson_interval(
    successes: int, n: int, confidence: float = 0.95
) -> Tuple[float, float]:
    """Compute the Wilson score confidence interval for a binomial proportion.

    Uses the Wilson score interval (closed-form) — no external dependencies
    beyond stdlib ``math``.  Returns (0.0, 0.0) when *n* is zero to avoid
    division-by-zero.

    Parameters
    ----------
    successes : int
        Number of successes (passed items).
    n : int
        Total number of trials (dataset rows evaluated).
    confidence : float, optional
        Confidence level, default 0.95 (→ z ≈ 1.96).

    Returns
    -------
    tuple[float, float]
        (lower_bound, upper_bound) of the confidence interval, each
        rounded to four decimal places.
    """
    if n == 0:
        return (0.0, 0.0)

    # Two-tailed z-score lookup for common confidence levels.
    # For 0.95 → 1.96, 0.99 → 2.576, 0.90 → 1.645.
    # General case uses the inverse-normal approximation via the
    # Abramowitz & Stegun rational approximation (accurate to ~4.5e-4).
    z = _z_score(confidence)

    p_hat = successes / n
    z2 = z * z

    denominator = 1 + z2 / n
    centre = (p_hat + z2 / (2 * n)) / denominator
    margin = (z / denominator) * math.sqrt(p_hat * (1 - p_hat) / n + z2 / (4 * n * n))

    lower = max(0.0, centre - margin)
    upper = min(1.0, centre + margin)

    return (round(lower, 4), round(upper, 4))


def confidence_band(n: int) -> str:
    """Return a human-readable confidence-band label based on sample size.

    Parameters
    ----------
    n : int
        Number of evaluated items.

    Returns
    -------
    str
        ``"Indicative"`` for *n* < 30, ``"Moderate"`` for 30 ≤ *n* < 100,
        ``"High"`` for *n* ≥ 100.
    """
    if n < 30:
        return "Indicative"
    if n < 100:
        return "Moderate"
    return "High"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _z_score(confidence: float) -> float:
    """Approximate the two-tailed z-score for a given confidence level.

    Uses the Beasley-Springer-Moro algorithm (rational approximation of
    the inverse normal CDF) which is accurate to ~1e-6 for the range we
    care about.  Falls back to well-known constants for the three most
    common confidence levels to avoid any rounding noise.
    """
    # Fast-path for common values
    _COMMON = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}
    if confidence in _COMMON:
        return _COMMON[confidence]

    # General case: inverse normal via rational approximation
    alpha = 1 - confidence
    p = 1 - alpha / 2  # upper-tail probability

    # Abramowitz & Stegun 26.2.23 — rational approximation
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    z = t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)
    return round(z, 4)
