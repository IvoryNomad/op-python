"""
op_python - Python wrapper for 1Password CLI
"""

from .op_client import OnePasswordError, OpClient

__version__ = "0.1.0"
__all__ = ["OpClient", "OnePasswordError"]
