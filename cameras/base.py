"""
Base Camera Profile

Abstract base class for camera-specific corrections.
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class CameraProfile(ABC):
    """Base class for camera-specific profiles."""
    
    name: str = "Generic Camera"
    make: str = ""
    model: str = ""
    
    @abstractmethod
    def apply_corrections(self, image: np.ndarray, 
                          iso: Optional[int] = None) -> np.ndarray:
        """
        Apply camera-specific corrections to image.
        
        Args:
            image: Input image (H, W, 3), uint8 or uint16
            iso: ISO value from EXIF (optional)
        
        Returns:
            Corrected image
        """
        pass
    
    @abstractmethod
    def get_recommended_denoise(self, iso: int) -> str:
        """
        Get recommended denoise strength based on ISO.
        
        Args:
            iso: ISO value
            
        Returns:
            Denoise strength: 'off', 'light', 'medium', 'strong'
        """
        pass
    
    def matches(self, make: str, model: str) -> bool:
        """Check if this profile matches a camera make/model."""
        return (self.make.upper() in make.upper() and 
                self.model.upper() in model.upper())
