"""
MotoGP Analytics Database Package
=================================
Database infrastructure for MotoGP analytics project.
"""

__version__ = "1.0.0"
__author__ = "MotoGP Analytics Team"

from .api.database import DatabaseManager
from .api.models import APIResponse

__all__ = ["DatabaseManager", "APIResponse"]