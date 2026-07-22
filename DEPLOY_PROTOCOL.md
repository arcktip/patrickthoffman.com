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
- `.env.deploy` — credentials
- `.git/`, `.DS_Store`

### If git push fails with 403:
Fix expired GitHub Personal Access Token in macOS Keychain — do NOT skip git and deploy directly. Skipping git breaks sync between Google Drive, GitHub, and DreamHost.

Fix: System Preferences → Passwords, or run `git credential-osxkeychain erase` then re-authenticate.

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
