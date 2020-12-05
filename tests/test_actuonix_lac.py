"""Module level tests"""
from actuonix_lac import __version__


def test_version() -> None:
    """Make sure version string is correct"""
    assert __version__ == "1.0.0"
