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

# Git: stage, commit, push
# Pass a commit message as $1 to commit+push any staged changes.
# Pass no argument (or "") to skip git entirely and just run the lftp deploy.
cd "$SCRIPT_DIR"
if [ "$#" -gt 0 ] && [ -n "$1" ]; then
  git config user.email "arcktip@users.noreply.github.com"
  git config user.name "Patrick Hoffman"
  git add .
  if git diff --cached --quiet; then
    echo "Nothing new to commit."
  else
    git commit -m "$1"
    echo "Committed."
  fi
  if ! git push 2>/dev/null; then
    echo "WARNING: git push failed (run 'git pull && git push' to sync). Continuing to deploy..."
  else
    echo "Pushed to GitHub."
  fi
else
  echo "No commit message given — skipping git, running lftp deploy only."
fi

# Deploy to DreamHost
echo "Deploying to DreamHost..."
lftp -c "
  set sftp:auto-confirm yes
  set net:max-retries 3
  set mirror:set-permissions off
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

# Fix permissions on the server:
#   files → 644 (owner rw, group/world r)
#   dirs  → 755 (owner rwx, group/world rx)
# Apache runs as a different user and needs read access.
echo "Setting file permissions on server..."
sshpass -p "$DH_PASS" ssh -o StrictHostKeyChecking=no "$DH_USER@$DH_HOST" \
  "find '$DH_DIR' -type f -not -path '*/zotero/*' -not -path '*/webdav/*' -exec chmod 644 {} \; && find '$DH_DIR' -type d -not -path '*/zotero*' -not -path '*/webdav*' -exec chmod 755 {} \;" \
  2>/dev/null \
  || ssh -o StrictHostKeyChecking=no "$DH_USER@$DH_HOST" \
       "find '$DH_DIR' -type f -not -path '*/zotero/*' -not -path '*/webdav/*' -exec chmod 644 {} \; && find '$DH_DIR' -type d -not -path '*/zotero*' -not -path '*/webdav*' -exec chmod 755 {} \;"

echo "Done. Site is live."
