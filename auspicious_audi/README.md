# auspicious_audi

A compact audio utility package for signal analysis, tuning, and packaging.

## What it does

- analyzes a floating point audio signal
- computes peak and RMS levels
- estimates duration and loudness hint
- prints a compact summary via CLI

## Usage

```bash
python -m auspicious_audi.cli --sample-rate 44100 --channels 1 --duration 2
```

## Example output

```text
sample_rate=44100
channels=1
duration_seconds=2.000
peak_level=0.469592
rms_level=0.171935
loudness_hint=balanced
```

## Python API

```python
from auspicious_audi import analyze_audio

signal = [0.1, -0.2, 0.3, -0.1]
result = analyze_audio(signal, sample_rate=44100, channels=1)
print(result.profile)
print(result.metadata)
```
