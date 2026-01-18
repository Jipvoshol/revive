"""
Revive - Camera Profiles

Camera-specific optimizations and corrections.
"""
from .base import CameraProfile
from .sony_rx1r import SonyRX1R

# Registry of available cameras
CAMERAS = {
    'sony_rx1r': SonyRX1R,
}

def get_camera(name: str) -> CameraProfile:
    """Get camera profile by name."""
    if name not in CAMERAS:
        available = ', '.join(CAMERAS.keys())
        raise ValueError(f"Unknown camera: {name}. Available: {available}")
    return CAMERAS[name]()

def list_cameras() -> list[str]:
    """List all available camera profiles."""
    return list(CAMERAS.keys())

__all__ = ['CameraProfile', 'SonyRX1R', 'get_camera', 'list_cameras', 'CAMERAS']
