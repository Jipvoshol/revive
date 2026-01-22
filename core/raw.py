"""
RAW Processor Module
Handles RAW file formats using Apple's native decoder (macOS) or rawpy (other platforms)
"""

import rawpy
import numpy as np
import cv2
import subprocess
import tempfile
import platform
from pathlib import Path


class RawProcessor:
    """Processes RAW files to RGB arrays using the best available decoder."""
    
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
        self.use_apple_decoder = platform.system() == 'Darwin'
    
    def process(self, raw_path: Path) -> np.ndarray:
        """
        Process a RAW file and return RGB array.
        
        Uses Apple's native decoder on macOS for best quality,
        falls back to rawpy on other platforms.
        """
        if self.use_apple_decoder:
            return self._process_with_sips(raw_path)
        else:
            return self._process_with_rawpy(raw_path)
    
    def _process_with_sips(self, raw_path: Path) -> np.ndarray:
        """Process RAW using Apple's sips command for native quality."""
        # Create temp file for intermediate TIFF (preserves quality)
        with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Use sips to convert RAW to TIFF (highest quality)
            result = subprocess.run([
                'sips', '-s', 'format', 'tiff',
                str(raw_path), '--out', tmp_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"sips failed: {result.stderr}")
            
            # Load the TIFF with OpenCV
            img = cv2.imread(tmp_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise RuntimeError(f"Failed to read converted image: {tmp_path}")
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Ensure correct bit depth
            if self.output_bps == 16 and rgb.dtype == np.uint8:
                rgb = (rgb.astype(np.uint16) * 257)  # Scale 8-bit to 16-bit
            elif self.output_bps == 8 and rgb.dtype == np.uint16:
                rgb = (rgb / 257).astype(np.uint8)
            
            return rgb
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    def _process_with_rawpy(self, raw_path: Path) -> np.ndarray:
        """Process RAW using rawpy (fallback for non-macOS)."""
        with rawpy.imread(str(raw_path)) as raw:
            rgb = raw.postprocess(
                demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                dcb_iterations=3,
                dcb_enhance=True,
                use_camera_wb=self.use_camera_wb,
                use_auto_wb=not self.use_camera_wb,
                output_bps=self.output_bps,
                output_color=rawpy.ColorSpace.sRGB,
                no_auto_bright=self.no_auto_bright,
                highlight_mode=rawpy.HighlightMode.Blend,
                gamma=(2.4, 12.92),
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

