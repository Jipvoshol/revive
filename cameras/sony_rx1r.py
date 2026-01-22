"""
Sony RX1R Camera Profile

Specific optimizations for the Sony RX1R full-frame compact camera.

Known issues addressed:
1. Barrel distortion (0.7%)
2. "Italian Flag" color shift (cyan-red across frame)
3. Vignetting at f/2 (~2EV)
4. Sony color science (warm shadows, green-blue shift)
5. Chromatic aberration in corners
"""

import numpy as np
import cv2
from typing import Optional
from dataclasses import dataclass
from .base import CameraProfile


@dataclass
class SonyRX1R(CameraProfile):
    """Sony RX1R camera profile with optimized settings."""
    
    name: str = "Sony RX1R"
    make: str = "Sony"
    model: str = "RX1R"
    
    # Zeiss 35mm f/2 lens characteristics
    barrel_distortion: float = -0.008      # -0.8%
    vignette_strength: float = 0.15        # 2EV at f/2
    italian_flag_strength: float = 0.0     # Disabled for now - needs calibration
    shadow_warmth: float = 0.0             # Disabled for now - needs calibration
    green_blue_shift: float = 0.0          # Disabled for now - needs calibration

    
    # Noise profile per ISO
    noise_profile = {
        100: 1.0, 200: 1.5, 400: 2.5, 800: 4.0,
        1600: 6.0, 3200: 9.0, 6400: 14.0, 
        12800: 22.0, 25600: 35.0,
    }
    
    def apply_corrections(self, image: np.ndarray, 
                          iso: Optional[int] = None) -> np.ndarray:
        """Apply all RX1R-specific corrections."""
        original_dtype = image.dtype
        max_val = 65535.0 if original_dtype == np.uint16 else 255.0
        
        img = image.astype(np.float32) / max_val
        
        # Apply corrections in optimal order
        img = self._correct_barrel_distortion(img)
        img = self._correct_italian_flag(img)
        img = self._correct_vignette(img)
        img = self._correct_color_cast(img)
        img = self._reduce_chromatic_aberration(img)
        
        img = np.clip(img, 0, 1)
        return (img * max_val).astype(original_dtype)
    
    def get_recommended_denoise(self, iso: int) -> str:
        """Get recommended denoise strength for RX1R."""
        if iso <= 400:
            return 'off'
        elif iso <= 1600:
            return 'light'
        elif iso <= 6400:
            return 'medium'
        else:
            return 'strong'
    
    def _correct_barrel_distortion(self, image: np.ndarray) -> np.ndarray:
        """Correct 0.7% barrel distortion from Zeiss 35mm f/2."""
        h, w = image.shape[:2]
        k1 = self.barrel_distortion
        
        if abs(k1) < 0.0001:
            return image
        
        fx = fy = max(w, h)
        cx, cy = w / 2, h / 2
        
        camera_matrix = np.array([
            [fx, 0, cx], [0, fy, cy], [0, 0, 1]
        ], dtype=np.float32)
        
        dist_coeffs = np.array([k1, 0, 0, 0, 0], dtype=np.float32)
        new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h)
        )
        
        img_uint = (image * 255).astype(np.uint8)
        undistorted = cv2.undistort(img_uint, camera_matrix, dist_coeffs, None, new_camera_matrix)
        return undistorted.astype(np.float32) / 255.0
    
    def _correct_italian_flag(self, image: np.ndarray) -> np.ndarray:
        """Correct cyan-red color shift across frame."""
        h, w, c = image.shape
        x_gradient = np.linspace(-1, 1, w).reshape(1, w, 1)
        
        correction = np.zeros_like(image)
        correction[:, :, 0] = -x_gradient[:, :, 0] * self.italian_flag_strength
        correction[:, :, 2] = x_gradient[:, :, 0] * self.italian_flag_strength
        
        luminance = np.mean(image, axis=2, keepdims=True)
        midtone_mask = 4 * luminance * (1 - luminance)
        
        return np.clip(image + correction * midtone_mask, 0, 1)
    
    def _correct_vignette(self, image: np.ndarray) -> np.ndarray:
        """Correct corner darkening at f/2."""
        h, w, c = image.shape
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h / 2, w / 2
        
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2) / max_dist
        
        correction = 1 + self.vignette_strength * (dist ** 2)
        return np.clip(image * correction[:, :, np.newaxis], 0, 1)
    
    def _correct_color_cast(self, image: np.ndarray) -> np.ndarray:
        """Correct Sony color tendencies."""
        img = image.copy()
        
        luminance = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
        shadow_mask = np.clip(1 - luminance * 2, 0, 1)[:, :, np.newaxis]
        
        # Reduce red in shadows
        img[:, :, 0] = img[:, :, 0] + shadow_mask[:, :, 0] * self.shadow_warmth
        
        # Fix green→blue shift
        green = img[:, :, 1]
        green_dominant = (green > img[:, :, 2]) & (green > img[:, :, 0])
        img[:, :, 2] = np.where(green_dominant, 
                                 img[:, :, 2] - self.green_blue_shift * green,
                                 img[:, :, 2])
        
        return np.clip(img, 0, 1)
    
    def _reduce_chromatic_aberration(self, image: np.ndarray) -> np.ndarray:
        """Reduce color fringing in corners."""
        h, w, c = image.shape
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h / 2, w / 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2) / max_dist
        
        corner_mask = np.clip((dist - 0.7) / 0.3, 0, 1).reshape(h, w)
        
        if corner_mask.max() < 0.01:
            return image
        
        red_blur = cv2.GaussianBlur(image[:, :, 0], (3, 3), 0.5)
        blue_blur = cv2.GaussianBlur(image[:, :, 2], (3, 3), 0.5)
        
        image[:, :, 0] = image[:, :, 0] * (1 - corner_mask) + red_blur * corner_mask
        image[:, :, 2] = image[:, :, 2] * (1 - corner_mask) + blue_blur * corner_mask
        
        return image
