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

# ---------------------------------------------------------------------------
# Step 1: Git — stage, commit, push
# GIT_TERMINAL_PROMPT=0 makes git fail fast with a clear error instead of
# silently hanging on a credential/keychain prompt you can't see.
# ---------------------------------------------------------------------------
echo "[1/3] Git: staging and committing..."
cd "$SCRIPT_DIR"
git add .
if git diff --cached --quiet; then
  echo "Nothing to commit, skipping git step."
else
  git commit -m "$MSG"
  echo "[1/3] Git: pushing to GitHub..."
  if ! GIT_TERMINAL_PROMPT=0 timeout 60 git push; then
    echo ""
    echo "ERROR: git push failed or timed out after 60s."
    echo "This usually means git needs you to (re)authenticate — e.g. an"
    echo "expired credential or SSH key. Try running 'git push' by itself"
    echo "in this folder to see the real prompt/error, fix auth, then re-run"
    echo "this script (it will skip the commit step since it's already made)."
    exit 1
  fi
  echo "Pushed to GitHub."
fi

# ---------------------------------------------------------------------------
# Step 2: Deploy to DreamHost via lftp
# Added connection/net timeouts so a flaky connection fails instead of
# hanging indefinitely.
# ---------------------------------------------------------------------------
echo "[2/3] Deploying to DreamHost..."
timeout 300 lftp -c "
  set sftp:auto-confirm yes
  set net:max-retries 3
  set net:timeout 20
  set net:reconnect-interval-base 5
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
    --exclude-glob deploy_v2.sh \
    $SCRIPT_DIR/ $DH_DIR
  quit
" || { echo "ERROR: lftp mirror failed or timed out after 5 min. Files may be partially uploaded — safe to re-run."; exit 1; }

# ---------------------------------------------------------------------------
# Step 3: Fix permissions on the server
#   files -> 644 (owner rw, group/world r)
#   dirs  -> 755 (owner rwx, group/world rx)
# Apache runs as a different user and needs read access.
#
# This step requires sshpass to run non-interactively. If it's not
# installed, we skip it cleanly with instructions rather than silently
# falling through to a bare `ssh` call that sits waiting for a password
# you can't see (this was almost certainly the earlier "lockup").
# ---------------------------------------------------------------------------
echo "[3/3] Setting file permissions on server..."
if command -v sshpass >/dev/null 2>&1; then
  if timeout 60 sshpass -p "$DH_PASS" ssh -o StrictHostKeyChecking=no -o BatchMode=no -o ConnectTimeout=15 "$DH_USER@$DH_HOST" \
    "find '$DH_DIR' -type f -not -path '*/zotero/*' -not -path '*/webdav/*' -exec chmod 644 {} \; && find '$DH_DIR' -type d -not -path '*/zotero*' -not -path '*/webdav*' -exec chmod 755 {} \;"; then
    echo "Permissions fixed."
  else
    echo "WARNING: permission-fix step failed or timed out. Site files are uploaded; you may need to fix permissions manually via SFTP or SSH."
  fi
else
  echo "NOTE: 'sshpass' isn't installed, so skipping the automatic permission fix"
  echo "(this is what likely caused the earlier hang — a bare 'ssh' call was"
  echo "silently waiting for your DreamHost password)."
  echo ""
  echo "To enable this step, install sshpass, e.g.:"
  echo "  brew install hudochenkov/sshpass/sshpass"
  echo ""
  echo "Or fix permissions manually right now by running:"
  echo "  ssh $DH_USER@$DH_HOST \"find '$DH_DIR' -type f -exec chmod 644 {} \\; && find '$DH_DIR' -type d -exec chmod 755 {} \\;\""
fi

echo ""
echo "Done. Site is live."
