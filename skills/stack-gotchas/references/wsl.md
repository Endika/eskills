# WSL and the host OS — gotchas

## Verify mobile/responsive rendering in WSL (no sudo)

- **Symptom:** you need to _see/measure_ real mobile widths but there's no Linux browser;
  Windows Edge headless **clamps window width to ~500px** (screenshots <450px render a wider
  layout cropped — misleading), and puppeteer can't drive the Windows `.exe` from WSL (stdio
  pipe breaks; its CDP debug port is unreachable over NAT).
- **Means:** you need a _native Linux_ Chromium, but the one puppeteer downloads is missing
  `libnss3`/`libnspr4`/`libasound2` and there's no passwordless sudo.
- **Fix (all without root):**
  ```
  npx -y @puppeteer/browsers install chrome@stable        # native linux chromium
  apt-get download libnss3 libnspr4 libasound2t64         # download .deb, no sudo
  for d in *.deb; do dpkg -x "$d" root; done              # extract libs locally
  # run with: LD_LIBRARY_PATH=$PWD/root/usr/lib/x86_64-linux-gnu  <chrome> …
  ```
  Drive via `puppeteer-core` (`executablePath` = that chrome; `LD_LIBRARY_PATH` in the env).
  Then `setViewport({ width, deviceScaleFactor: 2, isMobile: true })` at any width, measure
  `scrollWidth`/`getBoundingClientRect`, **bisect** overflow by toggling `display:none` per
  child, and confirm a fix by injecting the style and re-measuring before editing. Keep the
  env until done — don't re-download the ~150MB browser mid-task.
- **Before re-debugging a "still broken" UI report:** confirm the user isn't on a **stale
  deploy or cached PWA** (check the live tag + that `autoUpdate` activated). Much of this
  class of confusion is version lag, not a bug.

## Docker on WSL: images or containers that "disappeared"

- **Symptom:** `docker images` / `docker ps` in WSL doesn't list what Docker Desktop shows
  (or the reverse) — an image you just built is invisible, a container you know is up isn't
  there.
- **Means:** two different daemons. The native engine inside WSL keeps its own
  `/var/lib/docker` store; Docker Desktop keeps another inside its VM. The CLI answers for
  whichever the current context points at, and neither can see the other's images.
- **Fix:** `docker context ls` (and `docker context show`) before concluding anything was
  lost; build and run through the same engine. See
  `stacks/references/docker/toolchain-images.md`.

## The WSL disk never shrinks

- **Symptom:** freeing tens of gigabytes inside WSL leaves the `.vhdx` exactly as large as
  before; `fstrim` returns nothing.
- **Means:** the disk is in sparse mode, and sparse mode disables the compaction path —
  `diskpart` refuses to work on it.
- **Fix:** `wsl --manage <distro> --set-sparse false`, then compact with
  `diskpart`'s `compact vdisk`. Order matters; without the first step the second is a no-op.

## `reg.exe` output decoded from WSL comes out mangled

- **Symptom:** a loop reading the Windows registry from WSL breaks halfway, leaving the
  registry partially written.
- **Means:** `reg.exe` emits **cp850**, not UTF-8. Decoding as UTF-8 throws mid-iteration,
  after some writes have already happened.
- **Fix:** decode as cp850 explicitly, and make the loop safe to re-run — a half-applied
  registry change is the failure mode to design against.
