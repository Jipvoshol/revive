# Revive

**Computational photography for vintage cameras.**

> *"Your camera deserves 2025 software"*

Revive brings modern AI-powered processing to vintage digital cameras that have *superior hardware* but *outdated software*.

## Quick Start

```bash
pip install -r requirements.txt

# Process RAW files
python revive.py --input ./input --output ./output

# Use camera-specific optimizations
python revive.py --camera sony_rx1r

# List available camera profiles
python revive.py --cameras
```

## Supported Cameras

| Camera | Profile | Corrections |
|--------|---------|-------------|
| Sony RX1R | `sony_rx1r` | Italian Flag, Distortion, Vignetting, Color |
| *More coming...* | | |

## Options

```bash
python revive.py --help

# Camera selection
--camera sony_rx1r       # Use camera-specific corrections
--cameras                # List available profiles

# Output
--format jpg             # Output format (tiff, jpg, png)
--quality 95             # JPEG quality

# Processing
--denoise auto           # off, light, medium, strong, auto
--sharpen 1.0            # Sharpening strength (0-3)
--contrast 1.1           # Contrast multiplier
--saturation 1.05        # Saturation multiplier
```

## Project Structure

```
revive/
├── revive.py         # Main CLI
├── core/             # General processing (any camera)
│   ├── raw.py       # RAW decoding
│   ├── denoise.py   # AI denoising
│   ├── sharpen.py   # Smart sharpening
│   ├── enhance.py   # Color/contrast
│   └── utils.py     # EXIF, utilities
├── cameras/          # Camera-specific profiles
│   ├── base.py      # Base class
│   └── sony_rx1r.py # Sony RX1R
├── looks/            # Film emulations (coming)
├── input/            # Your RAW files
└── output/           # Processed images
```

## Philosophy

Modern smartphones produce incredible photos not because of their tiny sensors, but because of **computational photography** — AI-driven processing that happens after capture.

**Revive** brings these same techniques to cameras that have *superior hardware* but *decade-old software*.

A Sony RX1R from 2013 has:
- 🎯 **Full-frame sensor** (3.8× larger than any iPhone)
- 🔭 **Zeiss 35mm f/2** (optically superior to any smartphone)
- 📸 **14-bit RAW** (maximum data for processing)

But its image processing is stuck in 2013. **Revive fixes that.**

## License

MIT License - Free and open source.
