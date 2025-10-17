"""Compatibility shim: re-export Config from the package so imports like
`from config import Config` work when code is executed from project root.
"""
from campusgo_api.config import Config

__all__ = ['Config']
