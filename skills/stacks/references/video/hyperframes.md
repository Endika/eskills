# Video with HyperFrames

HyperFrames renders HTML to video, frame by frame, from a paused timeline. The craft — the
render contract, scenes, captions, the registry, media — lives in the `hyperframes` plugin's
own skills. This file only holds how I run it.

## Enable it for the video, disable it after

The plugin's skill descriptions are paid on every turn, and videos are occasional.
It stays disabled between videos:

```bash
claude plugin enable hyperframes@claude-plugins-official   # before starting
claude plugin disable hyperframes@claude-plugins-official  # when the render is delivered
```

The same goes for `runway-api@claude-plugins-official`, only when a shot needs generated
footage. Restart the session after enabling so the skills load.

## Project layout

- One folder per video, outside any code repo: it holds media, renders and music that
  don't belong in git history.
- `npx hyperframes init <dir>` to start; the root `index.html` mounts one scene per file
  in `compositions/`.
- Source footage and photos stay where they are; copy into `assets/` only what the video
  uses.

## Before calling it done

- `npx hyperframes check --json` clean: it reports contract violations with the fix.
- Watch the full render once at real speed, with sound. Lint does not see a cut that lands
  off the beat or a caption that covers a face.
- Renders are heavy: never run one next to another GPU or disk-bound job.
