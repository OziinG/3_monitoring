#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

IS_CI="${CI:-false}"

# Install dependencies (skip in CI, workflow handles it)
if [ "$IS_CI" != "true" ]; then
    echo "Local mode: Installing dependencies..."
    pip install -r requirements.txt
fi

# 1. Collect DB metadata
echo "Collecting DB metadata..."
python src/db/collect_metadata.py

# 2. Query match data (yesterday)
echo "Querying match data..."
python src/match/query_matches.py today

# 3. Generate all HTML pages
echo "Generating HTML pages..."
python generate_all.py

# 4. Commit and push (only if not in CI)
if [ "$IS_CI" != "true" ]; then
    echo "Committing changes..."
    git add src/db/db_monitoring.sqlite src/match/data.txt index.html db.html match.html
    git commit -m "Update monitoring dashboard $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

    echo "Pushing to main..."
    git push origin main
fi

echo "Deployment complete!"
