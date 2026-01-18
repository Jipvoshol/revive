"""
Image Enhancement Module
Exposure, contrast, and color adjustments
"""

import numpy as np
import cv2


class Enhancer:
    """Applies image enhancements."""
    
    def __init__(self,
                 contrast: float = 1.1,
                 brightness: float = 0.0,
                 saturation: float = 1.05,
                 apply_curve: bool = True):
        self.contrast = contrast
        self.brightness = brightness
        self.saturation = saturation
        self.apply_curve = apply_curve
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply enhancements to image."""
        original_dtype = image.dtype
        max_val = 65535.0 if original_dtype == np.uint16 else 255.0
        
        img = image.astype(np.float32) / max_val
        img = self._apply_contrast_brightness(img)
        
        if self.saturation != 1.0:
            img = self._apply_saturation(img)
        
        if self.apply_curve:
            img = self._apply_s_curve(img)
        
        img = np.clip(img, 0, 1)
        return (img * max_val).astype(original_dtype)
    
    def _apply_contrast_brightness(self, img: np.ndarray) -> np.ndarray:
        img = (img - 0.5) * self.contrast + 0.5
        img = img + self.brightness
        return img
    
    def _apply_saturation(self, img: np.ndarray) -> np.ndarray:
        img_8bit = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        hsv = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * self.saturation, 0, 255)
        hsv = hsv.astype(np.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return rgb.astype(np.float32) / 255.0
    
    def _apply_s_curve(self, img: np.ndarray) -> np.ndarray:
        """Apply subtle S-curve for punch."""
        curve_intensity = 0.08
        img = img + curve_intensity * np.sin(np.pi * img)
        return img
