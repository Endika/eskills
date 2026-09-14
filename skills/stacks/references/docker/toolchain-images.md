# Toolchain images — a container as a pinned tool, not a home

The dominant use here: a compiler, formatter or linter I don't want installed on the host,
frozen at a known version. `local/flipper-ci`, `clangfmt`, `cppcheck213`, `cc213`,
`cctools`, `golang` all exist for this. The container is disposable; the repo on the host
is the only thing that persists.

## The shape of the call

```bash
docker run --rm \
  -v "$PWD:/src" -w /src \
  -u "$(id -u):$(id -g)" \
  local/flipper-ci:1 make linter
```

Four things, each earning its place:

- **`--rm`** — the container is a process, not a machine. Nothing to clean up later.
- **`-v "$PWD:/src"` + `-w /src`** — the source stays on the host; only the toolchain is
  in the image.
- **`-u "$(id -u):$(id -g)"`** — **the one that bites if you skip it.** Without it the
  process runs as root and every file it writes (build output, generated sources, a
  formatter rewriting in place) comes back owned by root. You then need sudo to clean your
  own working tree, and a later non-root run fails on permissions instead of on merit.
- **A pinned tag** — `:1`, `213`, a version, never `:latest`. The point of the image is
  that the toolchain does not move under you; `:latest` throws that away. `clangfmt:latest`
  and `cctools:latest` here are the ones still to fix.

## Keep the image boring

Build these from a small Dockerfile in the repo that uses them, pin the base image by
version, and install only the tool. An image that also carries editors, shells and helpers
is an image you will eventually have to debug.

## Which engine am I even on

Under WSL the native Ubuntu engine and Docker Desktop are **two different daemons with
separate image stores**. An image built in one is invisible to the other, and `docker ps`
answers for whichever the current context points at. `docker context ls` before concluding
that an image or container vanished.
