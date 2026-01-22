#!/usr/bin/env python3
"""
Revive - Computational Photography for Vintage Cameras

Usage:
    python revive.py                        # Process all RAW files
    python revive.py --camera sony_rx1r     # Use RX1R optimizations
    python revive.py --cameras              # List available cameras
"""

import argparse
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
from tqdm import tqdm

from core import RawProcessor, Enhancer, Sharpener, Denoiser, read_exif, get_iso
from cameras import get_camera, list_cameras, CAMERAS


RAW_EXTENSIONS = {'.arw', '.cr2', '.cr3', '.nef', '.orf', '.raf', '.rw2', '.dng'}


def get_raw_files(input_dir: Path) -> list[Path]:
    """Find all RAW files in input directory."""
    files = []
    for ext in RAW_EXTENSIONS:
        files.extend(input_dir.glob(f'*{ext}'))
        files.extend(input_dir.glob(f'*{ext.upper()}'))
    return sorted(files)


def save_image(image: np.ndarray, output_path: Path, 
               format: str = 'tiff', quality: int = 95):
    """Save image to file with maximum quality preservation."""
    import cv2
    
    if format.lower() in ('jpg', 'jpeg'):
        if image.dtype == np.uint16:
            image_8bit = (image / 256).astype(np.uint8)
        else:
            image_8bit = image
        # Convert RGB to BGR for OpenCV
        bgr = cv2.cvtColor(image_8bit, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    
    elif format.lower() == 'tiff':
        # OpenCV can write 16-bit TIFFs properly
        # Convert RGB to BGR for OpenCV
        bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), bgr)
        
    elif format.lower() == 'png':
        if image.dtype == np.uint16:
            # PNG supports 16-bit
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), bgr)
        else:
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), bgr)



def process_file(raw_path: Path,
                 output_dir: Path,
                 raw_processor: RawProcessor,
                 camera_profile,  # Optional camera-specific processor
                 enhancer: Enhancer,
                 sharpener: Sharpener,
                 denoiser: Denoiser,
                 output_format: str = 'tiff',
                 quality: int = 95) -> Optional[Path]:
    """Process a single RAW file."""
    try:
        # Read EXIF for smart processing
        iso = get_iso(raw_path) if camera_profile else None
        
        # Step 1: RAW → RGB
        rgb = raw_processor.process(raw_path)
        
        # Step 2: Camera-specific corrections
        if camera_profile:
            rgb = camera_profile.apply_corrections(rgb, iso=iso)
        
        # Step 3: Smart denoising
        if camera_profile and iso and denoiser.strength == 'auto':
            recommended = camera_profile.get_recommended_denoise(iso)
            smart_denoiser = Denoiser(strength=recommended, preserve_detail=True)
            denoised = smart_denoiser.apply(rgb)
        else:
            denoised = denoiser.apply(rgb)
        
        # Step 4: Enhance
        enhanced = enhancer.apply(denoised)
        
        # Step 5: Sharpen
        sharpened = sharpener.apply(enhanced)
        
        # Step 6: Save
        ext = '.tiff' if output_format == 'tiff' else f'.{output_format}'
        output_path = output_dir / f"{raw_path.stem}_revived{ext}"
        save_image(sharpened, output_path, output_format, quality)
        
        return output_path
        
    except Exception as e:
        print(f"  Error: {raw_path.name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Revive - Computational Photography for Vintage Cameras',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python revive.py                          # Process with auto settings
  python revive.py --camera sony_rx1r       # Use Sony RX1R optimizations
  python revive.py --format jpg             # Output as JPEG
  python revive.py --cameras                # List available camera profiles
        """
    )
    
    # Camera selection
    parser.add_argument('--camera', '-c', type=str, default=None,
                       help='Camera profile to use (e.g., sony_rx1r)')
    parser.add_argument('--cameras', action='store_true',
                       help='List available camera profiles')
    
    # Paths
    parser.add_argument('--input', '-i', type=Path, default=Path('input'),
                       help='Input directory (default: input/)')
    parser.add_argument('--output', '-o', type=Path, default=Path('output'),
                       help='Output directory (default: output/)')
    
    # Output format
    parser.add_argument('--format', '-f', choices=['tiff', 'jpg', 'png'],
                       default='tiff', help='Output format (default: tiff)')
    parser.add_argument('--quality', '-q', type=int, default=95,
                       help='JPEG quality 1-100 (default: 95)')
    
    # Processing options
    parser.add_argument('--sharpen', type=float, default=1.0,
                       help='Sharpening strength 0-3 (default: 1.0)')
    parser.add_argument('--contrast', type=float, default=1.1,
                       help='Contrast multiplier (default: 1.1)')
    parser.add_argument('--exposure', type=float, default=0.0,
                       help='Exposure boost in EV (default: 0.0)')
    parser.add_argument('--shadows', type=float, default=0.0,
                       help='Shadow lift strength 0-1 (default: 0.0)')
    parser.add_argument('--highlights', type=float, default=0.0,
                       help='Highlight recovery strength 0-1 (default: 0.0)')
    parser.add_argument('--saturation', type=float, default=1.05,
                       help='Saturation multiplier (default: 1.05)')

    parser.add_argument('--no-curve', action='store_true',
                       help='Disable S-curve enhancement')
    parser.add_argument('--denoise', '-d', 
                       choices=['off', 'light', 'medium', 'strong', 'auto'],
                       default='auto', help='Denoise strength (default: auto)')
    
    args = parser.parse_args()
    
    # List cameras and exit
    if args.cameras:
        print("Available camera profiles:")
        for name in list_cameras():
            camera = get_camera(name)
            print(f"  {name:20} - {camera.name}")
        return 0
    
    # Validate input
    if not args.input.exists():
        print(f"Error: Input directory '{args.input}' does not exist.")
        return 1
    
    args.output.mkdir(parents=True, exist_ok=True)
    raw_files = get_raw_files(args.input)
    
    if not raw_files:
        print(f"No RAW files found in '{args.input}'")
        return 1
    
    # Load camera profile
    camera_profile = None
    if args.camera:
        try:
            camera_profile = get_camera(args.camera)
            print(f"Using camera profile: {camera_profile.name}")
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    print(f"Found {len(raw_files)} RAW file(s)")
    print(f"Output format: {args.format.upper()}")
    print()
    
    # Initialize processors
    raw_processor = RawProcessor(use_camera_wb=True, output_bps=16)
    enhancer = Enhancer(
        contrast=args.contrast, 
        exposure=args.exposure,
        saturation=args.saturation,
        shadows=args.shadows,
        highlights=args.highlights,
        apply_curve=not args.no_curve
    )
    sharpener = Sharpener(strength=args.sharpen)
    denoiser = Denoiser(strength=args.denoise, preserve_detail=True)
    
    # Process files
    successful = 0
    failed = 0
    
    for raw_path in tqdm(raw_files, desc="Processing"):
        # Auto-detect camera if not explicitly specified
        file_camera_profile = camera_profile
        if not file_camera_profile:
            from core.utils import detect_camera
            detected = detect_camera(raw_path)
            if detected:
                try:
                    file_camera_profile = get_camera(detected)
                except ValueError:
                    pass

        result = process_file(
            raw_path=raw_path,
            output_dir=args.output,
            raw_processor=raw_processor,
            camera_profile=file_camera_profile,
            enhancer=enhancer,
            sharpener=sharpener,
            denoiser=denoiser,
            output_format=args.format,
            quality=args.quality,
        )
        
        if result:
            successful += 1
        else:
            failed += 1
    
    print()
    print(f"Done! Processed {successful} file(s)")
    if failed:
        print(f"  ({failed} failed)")
    print(f"Output: {args.output.absolute()}")
    
    return 0


if __name__ == '__main__':
    exit(main())
