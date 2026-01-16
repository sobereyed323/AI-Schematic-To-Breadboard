"""
Breadboard Layout Engine

This package provides tools for converting electronic schematics into
breadboard layouts with component placement, wire routing, and visualization.

Modules:
    layout_engine: Core breadboard layout and routing algorithms
    visualizer: Breadboard visualization and export
    instructions: Assembly instruction and BOM generation

Example:
    >>> from breadboard import BreadboardLayout, BreadboardVisualizer
    >>> layout = BreadboardLayout()
    >>> # Place components and route connections
    >>> visualizer = BreadboardVisualizer(layout)
    >>> visualizer.save("output/breadboard.png")
"""

from breadboard.layout_engine import (
    BreadboardLayout,
    Component,
    Connection,
    ComponentConflictError,
    RoutingError,
)
from breadboard.visualizer import BreadboardVisualizer
from breadboard.instructions import InstructionGenerator, BillOfMaterials

__version__ = "0.1.0"
__all__ = [
    "BreadboardLayout",
    "Component",
    "Connection",
    "ComponentConflictError",
    "RoutingError",
    "BreadboardVisualizer",
    "InstructionGenerator",
    "BillOfMaterials",
]
