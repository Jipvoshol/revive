"""
Denoising Module
Multiple denoising algorithms from basic to AI-powered
"""

import numpy as np
import cv2
from typing import Literal


class Denoiser:
    """
    Image denoiser with multiple algorithm options.
    
    Strengths: 'off', 'light', 'medium', 'strong', 'auto'
    """
    
    def __init__(self,
                 strength: Literal['off', 'light', 'medium', 'strong', 'auto'] = 'auto',
                 preserve_detail: bool = True):
        self.strength = strength
        self.preserve_detail = preserve_detail
        self._strength_params = {
            'off': 0,
            'light': 3,
            'medium': 6,
            'strong': 10,
        }
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply denoising to image."""
        if self.strength == 'off':
            return image
        
        original_dtype = image.dtype
        is_16bit = original_dtype == np.uint16
        
        if is_16bit:
            image_8bit = (image / 256).astype(np.uint8)
        else:
            image_8bit = image
        
        if self.strength == 'auto':
            h = self._estimate_noise_strength(image_8bit)
        else:
            h = self._strength_params[self.strength]
        
        if h == 0:
            return image
        
        if self.preserve_detail:
            denoised = self._denoise_preserve_detail(image_8bit, h)
        else:
            denoised = self._denoise_standard(image_8bit, h)
        
        if is_16bit:
            denoised = (denoised.astype(np.uint16) * 256)
            denoised = self._restore_detail_16bit(image, denoised)
        
        return denoised.astype(original_dtype)
    
    def _estimate_noise_strength(self, image: np.ndarray) -> int:
        """Estimate noise level and return appropriate h value."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sigma = np.median(np.abs(cv2.Laplacian(gray, cv2.CV_64F))) / 0.6745
        
        if sigma < 5:
            return 2
        elif sigma < 10:
            return 4
        elif sigma < 20:
            return 7
        else:
            return 10
    
        return cv2.fastNlMeansDenoisingColored(
            image, None, h=h, hColor=h,
            templateWindowSize=7, searchWindowSize=21
        )
    
    def _denoise_preserve_detail(self, image: np.ndarray, h: int) -> np.ndarray:
        """Edge-aware denoising."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_mask = cv2.dilate(edges, None, iterations=1)
        edge_mask = cv2.GaussianBlur(edge_mask.astype(np.float32), (5, 5), 2)
        edge_mask = edge_mask / max(edge_mask.max(), 1)
        edge_mask = edge_mask[:, :, np.newaxis]
        
        denoised_strong = cv2.fastNlMeansDenoisingColored(
            image, None, h=h, hColor=h,
            templateWindowSize=7, searchWindowSize=21
        )
        denoised_light = cv2.fastNlMeansDenoisingColored(
            image, None, h=max(2, h // 2), hColor=max(2, h // 2),
            templateWindowSize=5, searchWindowSize=15
        )
        
        result = (denoised_strong * (1 - edge_mask) + 
                  denoised_light * edge_mask).astype(np.uint8)
        return result
    
    def _restore_detail_16bit(self, original: np.ndarray, 
                               denoised: np.ndarray) -> np.ndarray:
        """Restore fine detail from original 16-bit image."""
        original_blur = cv2.GaussianBlur(original.astype(np.float32), (3, 3), 0.5)
        detail = original.astype(np.float32) - original_blur
        result = denoised.astype(np.float32) + detail * 0.3
        return np.clip(result, 0, 65535).astype(np.uint16)
