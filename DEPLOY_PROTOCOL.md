# Deploy Protocol — patrickthoffman.com

## Rule: Google Drive → GitHub → DreamHost. All three stay in sync at all times.

### Correct deploy command (run from Patrick's Mac terminal):

```bash
cd ~/Library/CloudStorage/GoogleDrive-patrick.t.hoffman@gmail.com/.shortcut-targets-by-id/12feBbSibj4mrHIQJb5tYcL_PBYCtSfRY/patrick/websites/patrickthoffman.com && bash deploy_v3.sh "your commit message"
```

### What deploy_v3.sh does:
1. `git add .` — stages all changes
2. `git commit` — commits with your message
3. `git push` → GitHub via SSH (git@github.com:arcktip/patrickthoffman.com.git)
4. `lftp` mirror → DreamHost

### What is excluded (never pushed to GitHub or DreamHost):
- `_kdp/` — contains Amazon KDP print PDF and EPUB (self-publishing files, not web content)
  - Excluded from GitHub via `.gitignore`
  - Excluded from DreamHost via `--exclude-glob _kdp` and `--exclude-glob _kdp/` in `deploy_v3.sh` lftp mirror
  - KDP files: `product-manager-interior.pdf`, `product-manager.epub`, `product-manager-print-cover.pdf` — ALL go in `_kdp/`, nowhere else
- `*.sh` — shell scripts (security risk if served publicly); excluded from lftp
- `*.docx` — working documents (e.g. book-marketing-strategy.docx); excluded from lftp
- `*.md` — internal docs (e.g. DEPLOY_PROTOCOL.md); excluded from lftp
- `.env.deploy` — DreamHost credentials; excluded from both git and lftp
- `.git/`, `.DS_Store`

### IMPORTANT — lftp mirror does NOT delete remote files:
`lftp mirror --reverse` only adds/updates files. It does NOT remove files already on DreamHost
that have been deleted locally or added to excludes. To remove a file from DreamHost you must
delete it manually via the DreamHost file manager or SSH.

### Files manually deleted from DreamHost (do not re-add):
- `deploy_v2.sh`, `deploy_v3.sh`, `pull_books.sh` — shell scripts; security risk
- `DEPLOY_PROTOCOL.md` — internal doc
- `book-marketing-strategy.docx` — working document
- `books/product-manager-v2/` — old version of book; redirect in .htaccess handles old URLs

### DO NOT blanket-exclude *.pdf from lftp:
`teaching/assets/` and `writing/` contain PDFs that ARE legitimate web content and must deploy.
Only `_kdp/` PDFs are excluded (via the `_kdp/` folder exclusion).

### If git push fails:
Remote uses SSH (`git@github.com:arcktip/patrickthoffman.com.git`) — auth is via SSH key, not a PAT.
GitHub account email is `arcktip@gmail.com` (not patrick.t.hoffman@gmail.com).
SSH key: `~/.ssh/id_ed25519` — generate with `ssh-keygen -t ed25519 -C "arcktip@gmail.com"`
Check key is loaded: `ssh -T git@github.com`
If not loaded: `ssh-add ~/.ssh/id_ed25519`
Never switch to HTTPS — fine-grained PATs conflict across repos.

### Checking files on DreamHost:
- File manager hides dotfiles by default — look for a "Show hidden files" toggle
- To use SSH: DreamHost panel → Manage Users → set user type to Shell (SSH), not FTP-only
- SSH command: `ssh DH_USER@patrickthoffman.com "ls -la ~/patrickthoffman.com/"`
- `Connection closed` on SSH = user is FTP-only; enable Shell access in DreamHost panel first

### Claude sandbox cannot deploy:
The sandbox has no outbound network access to GitHub or DreamHost. Always hand the deploy command to Patrick to run on his Mac.

---

## Book Project — Product Manager?

### Build scripts (in /tmp/ on sandbox, must be re-created each session if lost):
- `build_interior.py` — WeasyPrint PDF (6×9in KDP interior)
- `build_epub.py` — EPUB for KDP ebook

### Standing rule: rebuild PDF + EPUB + copy to `_kdp/` after EVERY content change.

```bash
cd /sessions/clever-gracious-maxwell/mnt/patrickthoffman.com && \
python3 /tmp/build_interior.py && python3 /tmp/build_epub.py && \
cp /sessions/.../outputs/product-manager-interior.pdf _kdp/ && \
cp /sessions/.../outputs/product-manager.epub _kdp/
```

### Key layout rules:
- `ul, ol { page-break-inside: avoid }` in WeasyPrint — cannot be overridden with inline styles
- `p.calendar-day` CSS exists in BOTH `build_interior.py` AND `style.css` (must stay in sync)
- Stray `<hr>` before a heading inside a closing `</div>`: build script won't auto-remove it — delete from HTML source manually
- To control which page a figure lands on: reorder the `<figure>` element in the HTML source relative to surrounding paragraphs

### Legacy URL redirects:
- `/books/product-manager-v2/*` → `/books/product-manager/*` (301, in .htaccess)
