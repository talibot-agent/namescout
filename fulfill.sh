#!/bin/bash
# Usage: ./fulfill.sh "<Name>" <order_id>   -> orders/<order_id>/<slug>.html (+json, summary.txt)
set -e; cd "$(dirname "$0")"; N="$1"; O="$2"; mkdir -p "orders/$O"
python3 agent.py "$N" > "orders/$O/summary.txt" 2>&1
L=$(python3 -c 'import sys,agent;print(agent.slug(sys.argv[1]))' "$N"); cp "reports/$L.html" "reports/$L.json" "orders/$O/"
echo "orders/$O"
