#!/bin/bash
# ADD_CARRIER_LOGOS.command: moves the carrier logos downloaded from each carrier's official website into the site,
# rebuilds the review and launch copies, and refreshes the King_Health_Direct_Upload folder.
# Fallback: bash "/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health/ADD_CARRIER_LOGOS.command"
# standard-exempt: copies local files and rebuilds; commits, pushes and deploys nothing.
set -u
chmod +x "$0" "${0%/*}"/*.command 2>/dev/null || true
REPO="/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health"
UPLOAD="/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health_Direct_Upload"
DL="$HOME/Downloads"
DEST="$REPO/site/media/carriers"
mkdir -p "$DEST"
cd "$REPO" || { echo "STOPPED. King_Health is not where this button expects it: $REPO"; exit 1; }
newest() { ls -t "$DL"/$1 2>/dev/null | head -1; }
found=0
while IFS='|' read -r pattern target; do
  src="$(newest "$pattern")"
  if [ -n "$src" ]; then cp "$src" "$DEST/$target" && echo "  added  $target   (from $(basename "$src"))" && found=$((found+1));
  else echo "  MISSING $target   (no file matching $pattern in Downloads)"; fi
done <<'MAP'
aetna*.svg|aetna.svg
humana*.svg|humana.svg
kh-unitedhealthcare*.svg|unitedhealthcare.svg
kh-clover-health*.svg|clover-health.svg
devoted-health*.svg|devoted-health.svg
horizon-bcbsnj*.png|horizon-bcbsnj.png
wellpoint*.svg|wellpoint.svg
MAP
echo "$found of 7 logos added to site/media/carriers."
if ! python3 -c "import PIL, segno" 2>/dev/null; then python3 -m pip install --user --quiet pillow segno 2>/dev/null || python3 -m pip install --user --quiet --break-system-packages pillow segno; fi
echo "Rebuilding the review copy ..."; python3 _build/build.py | tail -1 || { echo "STOPPED. Review build failed."; exit 1; }
echo "Rebuilding the launch copy ..."
TMP="$(mktemp -d)"; cp -R _build site brand "$TMP/" && (cd "$TMP" && python3 _build/build.py --release | tail -1) || { echo "STOPPED. Launch build failed."; exit 1; }
rsync -a --delete "$TMP/site/" public/; rm -rf "$TMP"
if [ -d "$UPLOAD" ]; then rsync -a "$REPO/public/" "$UPLOAD/" && echo "King_Health_Direct_Upload refreshed."; fi
echo
echo "Done. Refresh the site preview to see the logos. Then push (PUSH_TO_GITHUB) and upload King_Health_Direct_Upload to Javon's Cloudflare."
read -r -p "Press Return to close this window..." _
