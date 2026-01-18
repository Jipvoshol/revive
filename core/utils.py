"""
Utility Functions
EXIF reading, file handling, etc.
"""

from pathlib import Path
from typing import Optional


def read_exif(raw_path: Path) -> dict:
    """
    Read EXIF metadata from a RAW file.
    
    Returns:
        Dictionary with EXIF data (ISO, FNumber, ExposureTime, Make, Model)
    """
    import rawpy
    
    exif = {}
    
    try:
        with rawpy.imread(str(raw_path)) as raw:
            exif['Make'] = getattr(raw, 'camera_make', '')
            exif['Model'] = getattr(raw, 'camera_model', '')
    except Exception:
        pass
    
    try:
        import exifread
        with open(str(raw_path), 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
            # ISO
            for iso_tag in ['EXIF ISOSpeedRatings', 'EXIF PhotographicSensitivity']:
                if iso_tag in tags:
                    try:
                        exif['ISO'] = int(str(tags[iso_tag]))
                        break
                    except:
                        pass
            
            # Aperture
            if 'EXIF FNumber' in tags:
                try:
                    fnum = tags['EXIF FNumber']
                    if hasattr(fnum, 'values') and len(fnum.values) > 0:
                        ratio = fnum.values[0]
                        exif['FNumber'] = float(ratio.num) / float(ratio.den)
                except:
                    pass
            
            # Shutter speed
            if 'EXIF ExposureTime' in tags:
                exif['ExposureTime'] = str(tags['EXIF ExposureTime'])
            
            # Make/Model fallback
            if 'Make' not in exif and 'Image Make' in tags:
                exif['Make'] = str(tags['Image Make'])
            if 'Model' not in exif and 'Image Model' in tags:
                exif['Model'] = str(tags['Image Model'])
                
    except ImportError:
        pass
    except Exception:
        pass
    
    return exif


def get_iso(raw_path: Path) -> Optional[int]:
    """Get ISO value from a RAW file."""
    exif = read_exif(raw_path)
    return exif.get('ISO')


def detect_camera(raw_path: Path) -> Optional[str]:
    """
    Detect camera model from RAW file.
    
    Returns:
        Camera identifier string (e.g., 'sony_rx1r') or None
    """
    exif = read_exif(raw_path)
    make = exif.get('Make', '').upper()
    model = exif.get('Model', '').upper()
    
    # Sony cameras
    if 'SONY' in make:
        if 'RX1R' in model and 'II' not in model:
            return 'sony_rx1r'
        elif 'RX1R II' in model or 'RX1RM2' in model:
            return 'sony_rx1r2'
        elif 'RX1' in model:
            return 'sony_rx1'
        elif 'A7R' in model:
            return 'sony_a7r'
    
    # Canon cameras
    if 'CANON' in make:
        if '5D MARK II' in model or '5D2' in model:
            return 'canon_5d2'
        elif '6D' in model:
            return 'canon_6d'
    
    # Nikon cameras
    if 'NIKON' in make:
        if 'D700' in model:
            return 'nikon_d700'
        elif 'D600' in model or 'D610' in model:
            return 'nikon_d610'
    
    return None
