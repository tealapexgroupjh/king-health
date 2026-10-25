#!/bin/bash
# BUILD.command: rebuilds the King Health site (site/ for review, public/ for launch) and runs the checks.
# Fallback: bash "/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health/BUILD.command"
# standard-exempt: builds local files only; commits, pushes and deploys nothing.
set -u
chmod +x "$0" "${0%/*}"/*.command 2>/dev/null || true
REPO="/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health"
cd "$REPO" || { echo "STOPPED. King_Health is not where this button expects it: $REPO"; exit 1; }
if ! python3 -c "import PIL, segno" 2>/dev/null; then
  echo "Installing the two image helpers the build uses (Pillow and segno) ..."
  python3 -m pip install --user --quiet pillow segno 2>/dev/null || python3 -m pip install --user --quiet --break-system-packages pillow segno || { echo "STOPPED. Could not install Pillow and segno."; exit 1; }
fi
echo "1 of 3: review build (site/) ..."
python3 _build/build.py || { echo "STOPPED. Review build failed."; exit 1; }
echo "2 of 3: launch build (public/) ..."
TMP="$(mktemp -d)"
cp -R _build site brand "$TMP/" && (cd "$TMP" && python3 _build/build.py --release) || { echo "STOPPED. Launch build failed."; exit 1; }
rsync -a --delete "$TMP/site/" public/
rm -rf "$TMP"
echo "3 of 3: checks ..."
python3 _build/release_check.py | tail -8
echo
echo "Done. Preview: open site/index.html through the site launcher. Publish: double click PUSH_TO_GITHUB.terminal."
read -r -p "Press Return to close this window..." _
