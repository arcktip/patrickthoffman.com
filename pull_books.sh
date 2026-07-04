#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.deploy"

# ---------------------------------------------------------------------------
# One-time sync: /books was published straight to DreamHost outside of git,
# so it has zero footprint in this repo. This pulls it down so the repo,
# GitHub, and DreamHost can all stay in sync going forward.
# Run this once, then run deploy_v3.sh as usual to commit + push it.
# ---------------------------------------------------------------------------

if [ ! -f "$ENV_FILE" ]; then
  echo "No .env.deploy found. Run deploy_v3.sh once first to set up credentials."
  exit 1
fi
source "$ENV_FILE"

REMOTE_DIR="${DH_DIR%/}/books"
LOCAL_DIR="$SCRIPT_DIR/books"

echo "Pulling $REMOTE_DIR from $DH_HOST into:"
echo "  $LOCAL_DIR"
mkdir -p "$LOCAL_DIR"

lftp -c "
  set sftp:auto-confirm yes
  set net:max-retries 3
  set net:timeout 20
  set net:reconnect-interval-base 5
  open sftp://$DH_USER:$DH_PASS@$DH_HOST
  mirror --verbose \
    --exclude-glob .DS_Store \
    $REMOTE_DIR $LOCAL_DIR
  quit
"

echo ""
echo "Done. books/ is now in your local repo folder."
echo ""
echo "Next steps:"
echo "  1. (Optional) Look over what came down: ls -la books/"
echo "  2. Run: bash deploy_v3.sh \"Bring books/ into the repo for full sync\""
echo "     This commits + pushes books/ to GitHub, then re-uploads it to"
echo "     DreamHost — harmless, since the content is identical; it just"
echo "     confirms all three copies now match."
