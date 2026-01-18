"""
RAW Processor Module
Handles RAW file formats using rawpy/LibRaw
"""

import rawpy
import numpy as np
from pathlib import Path


class RawProcessor:
    """Processes RAW files to RGB arrays."""
    
    def __init__(self, 
                 use_camera_wb: bool = True,
                 output_bps: int = 16,
                 no_auto_bright: bool = False):
        """
        Initialize RAW processor.
        
        Args:
            use_camera_wb: Use camera white balance (True) or auto WB (False)
            output_bps: Output bits per sample (8 or 16)
            no_auto_bright: Disable auto brightness adjustment
        """
        self.use_camera_wb = use_camera_wb
        self.output_bps = output_bps
        self.no_auto_bright = no_auto_bright
    
    def process(self, raw_path: Path) -> np.ndarray:
        """
        Process a RAW file and return RGB array.
        
        Args:
            raw_path: Path to RAW file (.ARW, .CR2, .NEF, etc.)
            
        Returns:
            numpy array with RGB image data (H, W, 3)
        """
        with rawpy.imread(str(raw_path)) as raw:
            rgb = raw.postprocess(
                demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
                use_camera_wb=self.use_camera_wb,
                use_auto_wb=not self.use_camera_wb,
                output_bps=self.output_bps,
                output_color=rawpy.ColorSpace.sRGB,
                no_auto_bright=self.no_auto_bright,
                highlight_mode=rawpy.HighlightMode.Blend,
                gamma=(1, 1) if self.output_bps == 16 else (2.222, 4.5),
            )
        return rgb
    
    def get_metadata(self, raw_path: Path) -> dict:
        """Extract metadata from RAW file."""
        with rawpy.imread(str(raw_path)) as raw:
            return {
                'camera_make': raw.camera_make,
                'camera_model': raw.camera_model,
                'raw_width': raw.raw_image.shape[1] if raw.raw_image is not None else None,
                'raw_height': raw.raw_image.shape[0] if raw.raw_image is not None else None,
            }
