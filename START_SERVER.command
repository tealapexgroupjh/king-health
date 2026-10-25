#!/bin/bash
# START_SERVER.command: serves the King Health site on this Mac so you can browse it at a local address.
# Double click START_SERVER.terminal to run this.
# Fallback if the executable bit is ever stripped:
#   bash "/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health/START_SERVER.command"
# Serves site/ (the review build, which refreshes itself after every rebuild). Add the word launch to serve public/ instead:
#   bash "/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health/START_SERVER.command" launch
# standard-exempt: serves local files read only; stages nothing, pushes nothing, deploys nothing.
set -u
chmod +x "$0" "${0%/*}"/*.command 2>/dev/null || true
REPO="/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health"
PORT=8790
DIR="site"; LABEL="review build (site/), refreshes after every rebuild"
if [ "${1:-}" = "launch" ]; then DIR="public"; PORT=8791; LABEL="launch build (public/), exactly what Cloudflare serves"; fi
cd "$REPO/$DIR" || { echo "STOPPED. King Health is not where this button expects it: $REPO/$DIR"; exit 1; }
URL="http://localhost:$PORT/index.html"
echo ""
echo "  KING HEALTH SITE SERVER"
echo "  Serving the $LABEL"
echo "  from $REPO/$DIR"
echo "  ==================================================="
if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "  A server is already running on port $PORT. Opening the site."
  open "$URL"; exit 0
fi
( sleep 1; open "$URL" ) &
echo "  Open: $URL"
echo "  Leave this window open while you browse. Close it, or press Control C, to stop."
echo ""
exec /usr/bin/python3 -m http.server $PORT --bind 127.0.0.1
