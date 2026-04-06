# Recordings

Playwright-based screen recordings for DryRun Security product documentation. Each script drives the browser through a feature flow, captures video, and converts it to an optimized GIF for embedding in docs pages.

## Prerequisites

```bash
npm install
npx playwright install chromium
```

ffmpeg is required for GIF conversion (pre-installed on most macOS/Linux systems).

## Quick start

```bash
# Record (reuses your logged-in Chrome session - close Chrome first)
node recordings/record-deepscan.js --profile

# Or record with a fresh browser (you'll need to log in)
node recordings/record-deepscan.js

# Convert to GIF
bash recordings/convert-to-gif.sh recordings/output/deepscan.webm recordings/output/deepscan.gif
```

## Writing a new recording

1. Copy an existing recording script (e.g., `record-deepscan.js`)
2. Edit the navigation steps - use `pause(ms)` between actions to give viewers time to see each step
3. Run the script, then convert with `convert-to-gif.sh`
4. Move the final GIF to `assets/recordings/` and reference it in `build.py`

## Options

**Recording scripts** support `--profile` to reuse your Chrome session (you must close Chrome first).

**`convert-to-gif.sh`** accepts environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FPS`    | 12      | Frames per second |
| `WIDTH`  | 960     | Output width in pixels (height scales proportionally) |
| `SPEED`  | 1.0     | Playback speed multiplier (e.g., 1.5 to speed up) |

Example: `FPS=15 WIDTH=1280 bash recordings/convert-to-gif.sh input.webm output.gif`

## Output

Generated files go in `recordings/output/` (git-ignored). Final GIFs for the docs site should be placed in `assets/recordings/` and committed.
