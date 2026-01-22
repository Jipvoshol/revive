"""
Image Enhancement Module
Exposure, contrast, and color adjustments
"""

import numpy as np
import cv2


class Enhancer:
    """Applies modern computational photography enhancements."""
    
    def __init__(self,
                  contrast: float = 1.1,
                  exposure: float = 0.0,      # EV compensation 
                  saturation: float = 1.05,
                  shadows: float = 0.0,       # Lift shadows
                  highlights: float = 0.0,    # Recover highlights  
                  apply_curve: bool = True):
        self.contrast = contrast
        self.exposure = exposure
        self.saturation = saturation
        self.shadows = shadows
        self.highlights = highlights
        self.apply_curve = apply_curve
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply enhancements to image."""
        original_dtype = image.dtype
        max_val = 65535.0 if original_dtype == np.uint16 else 255.0
        
        # Work in float [0, 1] for precision
        img = image.astype(np.float32) / max_val
        
        # 1. Exposure compensation (simple multiply, works on gamma-corrected data)
        if self.exposure != 0:
            # For gamma-corrected data, we can use a power function
            img = img * (2 ** self.exposure)
        
        # 2. Lift shadows if desired
        if self.shadows > 0:
            # Lift dark areas: dark pixels get boosted more
            img = img + self.shadows * 0.1 * (1.0 - img) * (1.0 - img)
        
        # 3. Compress highlights if desired
        if self.highlights > 0:
            # Soft-clip highlights
            img = 1.0 - (1.0 - img) ** (1.0 + self.highlights * 0.5)
            
        # 4. Contrast around midpoint 0.5
        if self.contrast != 1.0:
            img = (img - 0.5) * self.contrast + 0.5
        
        # 5. Saturation
        if self.saturation != 1.0:
            img = self._apply_saturation(img)
        
        # 6. S-Curve for final punch
        if self.apply_curve:
            img = self._apply_s_curve(img)
        
        img = np.clip(img, 0, 1)
        return (img * max_val).astype(original_dtype)
    
    def _apply_saturation(self, img: np.ndarray) -> np.ndarray:
        # Convert to 8-bit temporarily for OpenCV HSV
        img_8bit = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        hsv = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * self.saturation, 0, 255)
        hsv = hsv.astype(np.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return rgb.astype(np.float32) / 255.0
    
    def _apply_s_curve(self, img: np.ndarray) -> np.ndarray:
        """Apply subtle S-curve for punch."""
        curve_intensity = 0.05
        return img + curve_intensity * np.sin(np.pi * img)

