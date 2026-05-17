---
name: pixel-art
description: Convert images into retro pixel art with hardware-accurate palettes (NES, G...
version: 2.0.0
triggers:
- pixel art
- pixel-art
author: dodo-reach
license: MIT
metadata:
  hermes:
    tags:
    - creative
    - pixel-art
    - arcade
    - snes
    - nes
    - gameboy
    - retro
    - image
    - video
    category: creative
    credits:
    - Hardware palettes and animation loops ported from Synero/pixel-art-studio (MIT) — https://github.com/Synero/pixel-art-studio
depends_on: []

---
# Pixel Art

Convert any image into retro pixel art, then optionally animate it into a short
MP4 or GIF with era-appropriate effects (rain, fireflies, snow, embers).

Two scripts ship with this skill:

- `scripts/pixel_art.py` — photo → pixel-art PNG (Floyd-Steinberg dithering)
- `scripts/pixel_art_video.py` — pixel-art PNG → animated MP4 (+ optional GIF)

Each is importable or runnable directly. Presets snap to hardware palettes
when you want era-accurate colors (NES, Game Boy, PICO-8, etc.), or use
adaptive N-color quantization for arcade/SNES-style looks.

## When to Use

- User wants retro pixel art from a source image
- User asks for NES / Game Boy / PICO-8 / C64 / arcade / SNES styling
- User wants a short looping animation (rain scene, night sky, snow, etc.)
- Posters, album covers, social posts, sprites, characters, avatars

## Workflow

Before generating, confirm the style with the user. Different presets produce
very different outputs and regenerating is costly.

### Step 1 — Offer a style

Call `clarify` with 4 representative presets. Pick the set based on what the
user asked for — don't just dump all 14.

Default menu when the user's intent is unclear:

```python
clarify(
    question="Which pixel-art style do you want?",
    choices=[
        "arcade — bold, chunky 80s cabinet feel (16 colors, 8px)",
        "nes — Nintendo 8-bit hardware palette (54 colors, 8px)",
        "gameboy — 4-shade green Game Boy DMG",
        "snes — cleaner 16-bit look (32 colors, 4px)",
    ],
)
```

When the user already named an era (e.g. "80s arcade", "Gameboy"), skip
`clarify` and use the matching preset directly.

### Step 2 — Offer animation (optional)

If the user asked for a video/GIF, or the output might benefit from motion,
ask which scene:

```python
clarify(
    question="Want to animate it? Pick a scene or skip.",
    choices=[
        "night — stars + fireflies + leaves",
        "urban — rain + neon pulse",
        "snow — falling snowflakes",
        "skip — just the image",
    ],
)
```

Do NOT call `clarify` more than twice in a row. One for style, one for scene if
animation is on the table. If the user explicitly asked for a specific style
and scene in their message, skip `clarify` entirely.

### Step 3 — Generate

Run `pixel_art()` first; if animation was requested, chain into
`pixel_art_video()` on the result.


> 🔍 **## Preset Catalog** moved to [references/detailed.md](references/detailed.md)
