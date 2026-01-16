"""
AI Enhancement Module

This package provides AI-powered enhancements for circuit analysis and
component classification using GPT-4 Vision and improved CNN techniques.

Modules:
    gpt_vision: GPT-4 Vision API integration for schematic analysis
    improved_classifier: Enhanced component classification combining CNN and GPT-4

Example:
    >>> from ai_enhancement import SchematicAnalyzer, ImprovedClassifier
    >>> analyzer = SchematicAnalyzer(api_key="your_key")
    >>> result = analyzer.analyze_schematic("schematic.png")
"""

from ai_enhancement.gpt_vision import (
    SchematicAnalyzer,
    APIError,
    ValidationResult,
)
from ai_enhancement.improved_classifier import (
    ImprovedClassifier,
    ClassificationResult,
)

__version__ = "0.1.0"
__all__ = [
    "SchematicAnalyzer",
    "APIError",
    "ValidationResult",
    "ImprovedClassifier",
    "ClassificationResult",
]
