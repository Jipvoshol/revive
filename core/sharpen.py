"""
Sharpening Module
Smart, edge-aware sharpening
"""

import numpy as np
import cv2


class Sharpener:
    """Applies smart sharpening to images."""
    
    def __init__(self, strength: float = 1.0, radius: float = 1.0, threshold: int = 3):
        self.strength = strength
        self.radius = radius
        self.threshold = threshold
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply smart sharpening to image."""
        if self.strength == 0:
            return image
        
        original_dtype = image.dtype
        max_val = 65535 if original_dtype == np.uint16 else 255
        img = image.astype(np.float32)
        
        sharpened = self._unsharp_mask_edge_aware(img, max_val)
        sharpened = np.clip(sharpened, 0, max_val)
        return sharpened.astype(original_dtype)
    
    def _unsharp_mask_edge_aware(self, img: np.ndarray, max_val: int) -> np.ndarray:
        """Edge-aware unsharp mask."""
        sigma = self.radius * 2
        ksize = int(sigma * 3) | 1
        
        blurred = cv2.GaussianBlur(img, (ksize, ksize), sigma)
        difference = img - blurred
        
        gray = cv2.cvtColor((img / max_val * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_mask = cv2.GaussianBlur(edges.astype(np.float32), (5, 5), 1)
        edge_mask = edge_mask / max(edge_mask.max(), 1)
        edge_mask = edge_mask[:, :, np.newaxis]
        
        threshold_scaled = self.threshold * (max_val / 255)
        mask = np.abs(difference).mean(axis=2, keepdims=True) > threshold_scaled
        combined_mask = mask.astype(np.float32) * edge_mask
        
        sharpened = img + difference * self.strength * (0.5 + 0.5 * combined_mask)
        return sharpened
