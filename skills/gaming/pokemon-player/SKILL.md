---
name: pokemon-player
description: Play Pokemon games autonomously via headless emulation. Starts a game serve...
triggers:
- pokemon player
- pokemon-player
tags:
- gaming
- pokemon
- emulator
- pyboy
- gameplay
- gameboy
metadata:
  hermes:
    tags: []
depends_on:
  - web-access
  - browser-automation

---
# Pokemon Player

Play Pokemon games via headless emulation using the `pokemon-agent` package.

## When to Use
- User says "play pokemon", "start pokemon", "pokemon game"
- User asks about Pokemon Red, Blue, Yellow, FireRed, etc.
- User wants to watch an AI play Pokemon
- User references a ROM file (.gb, .gbc, .gba)

## Startup Procedure

### 1. First-time setup (clone, venv, install)
The repo is NousResearch/pokemon-agent on GitHub. Clone it, then
set up a Python 3.10+ virtual environment. Use uv (preferred for speed)
to create the venv and install the package in editable mode with the
pyboy extra. If uv is not available, fall back to python3 -m venv + pip.

On this machine it is already set up at /home/teknium/pokemon-agent
with a venv ready — just cd there and source .venv/bin/activate.

You also need a ROM file. Ask the user for theirs. On this machine
one exists at roms/pokemon_red.gb inside that directory.
NEVER download or provide ROM files — always ask the user.

### 2. Start the game server
From inside the pokemon-agent directory with the venv activated, run
pokemon-agent serve with --rom pointing to the ROM and --port 9876.
Run it in the background with &.
To resume from a saved game, add --load-state with the save name.
Wait 4 seconds for startup, then verify with GET /health.


> 🔍 **### 3. Set up live dash** moved to [references/detailed.md](references/detailed.md)

## Verification Checklist

- [ ] Read the full content to ensure understanding
- [ ] Verify all code examples are syntactically correct
- [ ] Check that all referenced files exist
- [ ] Test the workflow with a simple input

## Common Pitfalls

1. **Missing dependencies**: Ensure all required tools are installed before starting.
2. **Wrong input format**: Verify input matches the expected format before processing.
3. **Version mismatch**: Check version compatibility between tools.
