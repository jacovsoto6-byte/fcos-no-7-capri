"""auspicious_audi

A small, auditable audio analysis and packaging utility.
"""

from .core import AudioProfile, AnalysisResult, analyze_audio

__all__ = ["AudioProfile", "AnalysisResult", "analyze_audio"]
__version__ = "0.1.0"
