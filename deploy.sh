#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.deploy"

# Load credentials
if [ ! -f "$ENV_FILE" ]; then
  echo "No .env.deploy found. Let's set it up (saved locally, never committed)."
  read -p "DreamHost hostname (e.g. patrickthoffman.com): " DH_HOST
  read -p "DreamHost username: " DH_USER
  read -s -p "DreamHost password: " DH_PASS
  echo
  read -p "Remote path (e.g. /home/yourusername/patrickthoffman.com/): " DH_DIR
  cat > "$ENV_FILE" <<EOF
DH_HOST=$DH_HOST
DH_USER=$DH_USER
DH_PASS='$DH_PASS'
DH_DIR=$DH_DIR
EOF
  echo "Credentials saved to .env.deploy"
fi

source "$ENV_FILE"

# Commit message from argument or prompt
MSG="${1:-}"
if [ -z "$MSG" ]; then
  read -p "Commit message: " MSG
fi

# Git: stage, commit, push
cd "$SCRIPT_DIR"
git add .
if git diff --cached --quiet; then
  echo "Nothing to commit, skipping git step."
else
  git commit -m "$MSG"
  git push
  echo "Pushed to GitHub."
fi

# Deploy to DreamHost
echo "Deploying to DreamHost..."
lftp -c "
  set sftp:auto-confirm yes
  set net:max-retries 3
  open sftp://$DH_USER:$DH_PASS@$DH_HOST
  mirror --reverse --verbose \
    --exclude-glob .git \
    --exclude-glob .git/ \
    --exclude-glob .DS_Store \
    --exclude-glob .dh-diag \
    --exclude-glob .dh-diag/ \
    --exclude-glob .env.deploy \
    --exclude-glob deploy.sh \
    $SCRIPT_DIR/ $DH_DIR
  quit
"
echo "Done. Site is live."
