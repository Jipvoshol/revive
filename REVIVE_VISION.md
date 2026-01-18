# Revive: Computational Photography for Vintage Cameras

> *"Turn your €300 vintage camera into a 2025 shooter"*

## 🎯 Vision

Modern smartphones produce incredible photos not because of their tiny sensors, but because of **computational photography** — AI-driven processing that happens after the shutter clicks.

**Revive** brings these same techniques to vintage digital cameras that have *superior hardware* but *outdated software*.

A Sony RX1R from 2013 has:
- A **full-frame sensor** (3.8× larger than any iPhone)
- A **Zeiss 35mm f/2 lens** (optically superior to any smartphone)
- **RAW capability** (14-bit uncompressed data)

But its image processing is stuck in 2013. We fix that.

---

## 🔥 The Problem We Solve

| Camera | Original Price | Used Price | Hardware | Software |
|--------|----------------|------------|----------|----------|
| Sony RX1R | €2,800 | €500-800 | Excellent | Outdated |
| Canon 5D II | €2,500 | €300-400 | Excellent | Outdated |
| Nikon D700 | €2,800 | €300-400 | Excellent | Outdated |
| Leica M9 | €6,000 | €1,500 | Excellent | Outdated |

These cameras are *overpowered* for their current price. The only thing holding them back is decade-old image processing.

**Revive** applies modern computational photography:
- AI denoising (turn ISO 6400 into ISO 800)
- Intelligent sharpening (edge-aware, no halos)
- HDR tone mapping (maximize dynamic range)
- Film emulation (Portra, Kodachrome, etc.)
- Camera-specific color science

---

## 🏗️ Architecture

```
                            Revive
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  📁 input/                                                   │
│      └── *.ARW, *.CR2, *.NEF, *.DNG                         │
│              │                                               │
│              ▼                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Camera Profile (cameras/sony_rx1r.py)                │   │
│  │   - Color matrix                                      │   │
│  │   - Lens corrections                                  │   │
│  │   - Sensor noise characteristics                      │   │
│  │   - Default settings                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│              │                                               │
│              ▼                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Processing Pipeline                                   │   │
│  │   1. RAW Decode (rawpy)                              │   │
│  │   2. Lens Correction                                  │   │
│  │   3. AI Denoise (Custom)                             │   │
│  │   4. Exposure/Contrast                               │   │
│  │   5. Color Grading (Film Look)                       │   │
│  │   6. Smart Sharpen                                    │   │
│  │   7. Output                                           │   │
│  └──────────────────────────────────────────────────────┘   │
│              │                                               │
│              ▼                                               │
│  📁 output/                                                  │
│      └── *_revived.tiff / .jpg                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
revive/
├── revive.py                     # Main CLI
│
├── core/                         # General processing (any camera)
│   ├── __init__.py
│   ├── raw.py                   # RAW decoding
│   ├── denoise.py               # AI denoising
│   ├── sharpen.py               # Smart sharpening
│   ├── enhance.py               # Color/contrast
│   └── utils.py                 # EXIF, utilities
│
├── cameras/                      # Camera-specific profiles
│   ├── base.py                  # Base class
│   ├── sony_rx1r.py             # Sony RX1R
│   └── ...
│
├── looks/                        # Film emulation / color grades
│   ├── __init__.py
│   └── ...
│
├── input/                        # Input drop folder
├── output/                       # Output folder
│
├── tests/
├── README.md
└── LICENSE (MIT)
```

---

## 🎨 Unique Features

### 1. Camera Profiles

Camera-specific optimizations, not generic processing:

```python
# cameras/sony_rx1r.py
class SonyRX1R(CameraProfile):
    name = "Sony RX1R"
    
    # Sensor noise characteristics (measured)
    noise_profile = {
        100: 1.0, 
        800: 4.0,
        6400: 14.0,
    }
    
    # Zeiss lens corrections
    barrel_distortion = -0.008
    vignette_strength = 0.15
```

### 2. Film Looks (Recipes)

Community-contributed color grades:

```python
# looks/portra_400.py
class Portra400(FilmLook):
    name = "Kodak Portra 400"
    
    # Warm shadows, neutral highlights
    shadows_hue = 30      # Orange
    shadows_sat = 0.15
    # ...
```

---

## 📈 Roadmap

### Phase 1: Core (v0.1) ✅ 
- [x] Basic RAW processing
- [x] Smart denoising (OpenCV NLM + Edge Mask)
- [x] Smart sharpening
- [x] Enhancement (contrast, saturation, S-curve)
- [x] Batch processing
- [x] CLI interface
- [x] Sony RX1R Profile
- [x] Profile auto-detection from EXIF

### Phase 2: AI Upgrade (v0.2)
- [ ] Integrate NAFNet for real AI denoising
- [ ] Add Real-ESRGAN for optional upscaling
- [ ] GPU acceleration

### Phase 3: Camera Profiles (v0.3)
- [ ] Canon 5D Mark II profile
- [ ] Nikon D700 profile
- [ ] Leica M9 profile



## 📄 License

**MIT License** — fully open source, no restrictions.
