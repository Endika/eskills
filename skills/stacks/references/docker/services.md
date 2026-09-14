# Long-lived services — the ones that must survive a reboot

A container that stays up (the `anisette` provisioning server here, anything self-hosted
elsewhere) is infrastructure, not a command. It is judged on whether it comes back after a
reboot with its data intact, and on how much it could do if it were compromised.

The live example below is real: every claim about it was read off the running container,
and the gaps named are gaps it actually has.

## Pin what you depend on

`:latest` on a service is a silent upgrade at the worst possible moment — the next pull,
or the next time the host reboots. Pin the tag, and the digest for anything whose data you
care about. `dadoum/anisette-v3-server:latest` is the standing example: the FindMy history
leans on it, and `reports.db` is the only durable copy of that history.

## What a hardened service adds

```yaml
services:
  anisette:
    image: dadoum/anisette-v3-server:<tag> # today: :latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:6969:6969" # today: 6969 on 0.0.0.0 and ::
    volumes:
      - anisette-v3_data:/home/Alcoholic/.config/anisette-v3
    security_opt:
      - no-new-privileges:true # today: none set
    cap_drop:
      - ALL # today: nothing dropped
    healthcheck: # today: none
      test: ["CMD-SHELL", "curl -fsS localhost:6969 || exit 1"]
      interval: 30s
      timeout: 3s
      retries: 3

volumes:
  anisette-v3_data:
```

- **A named volume for state** — already right here: `anisette-v3_data` holds the config
  directory, so the container itself stays disposable. Anything outside a volume dies with
  the container.
- **`restart: unless-stopped` vs `always`** — this one runs `always`, which also restarts a
  container you stopped on purpose once the daemon comes back. `unless-stopped` keeps the
  reboot survival and respects a deliberate stop. Either is defensible; know which you chose.
- **`no-new-privileges` + `cap_drop: ALL`**, adding back only what the service proves it
  needs (`NET_BIND_SERVICE` only below port 1024). The image already runs as a non-root
  user, which is the bigger half — this is the cheap remainder.
- **A healthcheck that asks the service, not the process table.** "The container is up" and
  "the service answers" are different claims, and `depends_on: condition: service_healthy`
  means nothing without a real check.

## Exposure

Bind to `127.0.0.1:PORT:PORT` unless something off-box genuinely needs it. `6969` is
currently published on every interface, which on a laptop that joins other networks is a
wider door than the use case asks for.

## Secrets

Runtime environment or `env_file`, never baked into a layer — layers are distributable and
`docker history` reads them back. Keep the `.env` out of git.

## Origin

The hardening set (pinned tags, `no-new-privileges`, `cap_drop`, secrets kept out of image
layers) is adapted from ECC `skills/docker-patterns`. The live example is not: every claim
about the `anisette` container, and every gap named as still open, was read off the
container running on this machine.
