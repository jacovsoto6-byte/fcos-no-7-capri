"""CLI shim for auspicious_audi.

Example:
    python -m auspicious_audi.cli --sample-rate 44100 --channels 2 --duration 2
"""

from __future__ import annotations

import argparse
import math
import random

from .core import analyze_audio


def _generate_demo_signal(duration_seconds: float, sample_rate: int, channels: int = 1) -> list[float]:
    total = int(duration_seconds * sample_rate)
    samples: list[float] = []
    for i in range(total):
        t = i / max(sample_rate, 1)
        envelope = 0.35 + 0.2 * math.sin(2 * math.pi * 220 * t)
        noise = (random.random() - 0.5) * 0.06
        sample = envelope * math.sin(2 * math.pi * 220 * t) + noise
        samples.append(max(-1.0, min(1.0, sample)))
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description="auspicious_audi: lightweight audio analysis")
    parser.add_argument("--sample-rate", type=int, default=44100)
    parser.add_argument("--channels", type=int, default=1)
    parser.add_argument("--duration", type=float, default=1.0)
    args = parser.parse_args()

    signal = _generate_demo_signal(args.duration, args.sample_rate, args.channels)
    result = analyze_audio(signal, sample_rate=args.sample_rate, channels=args.channels)
    print(f"sample_rate={result.profile.sample_rate}")
    print(f"channels={result.profile.channels}")
    print(f"duration_seconds={result.profile.duration_seconds:.3f}")
    print(f"peak_level={result.profile.peak_level:.6f}")
    print(f"rms_level={result.profile.rms_level:.6f}")
    print(f"loudness_hint={result.profile.loudness_hint}")


if __name__ == "__main__":
    main()
