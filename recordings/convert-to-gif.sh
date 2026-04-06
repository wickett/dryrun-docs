#!/usr/bin/env bash
# Convert a .webm screen recording to an optimized GIF.
#
# Requires: ffmpeg (with libvpx support)
#
# Usage:
#   bash recordings/convert-to-gif.sh <input.webm> <output.gif>
#
# Options (via environment variables):
#   FPS=12        Frames per second (default: 12 - good balance of smoothness and size)
#   WIDTH=960     Output width in pixels (default: 960 - height scales proportionally)
#   SPEED=1.0     Playback speed multiplier (default: 1.0; use 1.5 to speed up)

set -euo pipefail

INPUT="${1:?Usage: convert-to-gif.sh <input.webm> <output.gif>}"
OUTPUT="${2:?Usage: convert-to-gif.sh <input.webm> <output.gif>}"

FPS="${FPS:-12}"
WIDTH="${WIDTH:-960}"
SPEED="${SPEED:-1.0}"

PALETTE=$(mktemp /tmp/palette-XXXXXX.png)
trap 'rm -f "$PALETTE"' EXIT

# Build the filter chain
FILTERS="fps=${FPS},scale=${WIDTH}:-1:flags=lanczos"
if [ "$(echo "$SPEED != 1.0" | bc -l)" -eq 1 ]; then
  FILTERS="setpts=PTS/${SPEED},${FILTERS}"
fi

echo "Converting: $INPUT → $OUTPUT"
echo "  FPS=$FPS  WIDTH=$WIDTH  SPEED=$SPEED"
echo ""

# Pass 1: generate an optimal 256-color palette from the video
ffmpeg -y -i "$INPUT" -vf "${FILTERS},palettegen=stats_mode=diff" "$PALETTE" 2>/dev/null

# Pass 2: render the GIF using the palette for high quality dithering
ffmpeg -y -i "$INPUT" -i "$PALETTE" -lavfi "${FILTERS} [x]; [x][1:v] paletteuse=dither=floyd_steinberg" "$OUTPUT" 2>/dev/null

SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "✓ Created $OUTPUT ($SIZE)"
