"""Core audio utilities for auspicious_audi.

This module provides a lightweight analytical layer for audio signals,
without depending on heavyweight media libraries.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Sequence
import math


@dataclass
class AudioProfile:
    sample_rate: int
    channels: int
    duration_seconds: float
    peak_level: float
    rms_level: float
    loudness_hint: str


@dataclass
class AnalysisResult:
    profile: AudioProfile
    metadata: Dict[str, float]


def _as_float_list(values: Sequence[float]) -> List[float]:
    return [float(v) for v in values]


def analyze_audio(samples: Sequence[float], sample_rate: int = 44100, channels: int = 1) -> AnalysisResult:
    """Compute a stable summary profile for a signal.

    Args:
        samples: Audio samples, expected to be normalized floats in [-1, 1].
        sample_rate: Sampling rate in Hz.
        channels: Number of channels.

    Returns:
        AnalysisResult containing a compact audio profile and metadata.
    """
    xs = _as_float_list(samples)
    if not xs:
        raise ValueError("samples must not be empty")

    peak = max(abs(v) for v in xs)
    mean_sq = sum(v * v for v in xs) / len(xs)
    rms = math.sqrt(mean_sq)
    duration_seconds = len(xs) / max(sample_rate, 1)

    if rms < 0.05:
        loudness_hint = "soft"
    elif rms < 0.25:
        loudness_hint = "balanced"
    elif rms < 0.5:
        loudness_hint = "bold"
    else:
        loudness_hint = "hot"

    profile = AudioProfile(
        sample_rate=sample_rate,
        channels=channels,
        duration_seconds=duration_seconds,
        peak_level=peak,
        rms_level=rms,
        loudness_hint=loudness_hint,
    )

    metadata = {
        "sample_count": float(len(xs)),
        "peak_db": 20.0 * math.log10(max(peak, 1e-9)),
        "rms_db": 20.0 * math.log10(max(rms, 1e-9)),
        "crest_factor": peak / max(rms, 1e-9),
    }
    return AnalysisResult(profile=profile, metadata=metadata)


if __name__ == "__main__":
    signal = [0.0, 0.1, -0.08, 0.2, -0.15, 0.25, -0.1, 0.05]
    result = analyze_audio(signal)
    print(result.profile)
    print(result.metadata)
