# Dev environments — the app itself in a container

The case where the project runs inside Docker rather than merely being built by it: a
compose stack on the other machine, or a repo whose dependencies are too heavy to install
on the host. None of the web apps here need this — they run on Vite against Supabase — so
reach for it when the dependency graph, not the habit, demands it.

## One Dockerfile, several stages

```dockerfile
FROM node:22.12-alpine3.20 AS deps        # pinned base, never :latest
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS dev                          # hot reload, dev tooling present
WORKDIR /app
COPY . .
CMD ["npm", "run", "dev"]

FROM deps AS build
WORKDIR /app
COPY . .
RUN npm run build

FROM node:22.12-alpine3.20 AS production  # nothing from the build toolchain
WORKDIR /app
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app
COPY --from=build --chown=app:app /app/dist ./dist
ENV NODE_ENV=production
```

The production stage copies artifacts, never the builder. Non-root there is not ceremony:
it is the difference between a container escape landing on a user and landing on root.

## Compose for development

- **`target: dev`** so the dev stage is what runs locally.
- **Bind-mount the source, anonymous-volume `node_modules`** — `- .:/app` then
  `- /app/node_modules`. Without the second line the host's (possibly empty, possibly
  wrong-platform) `node_modules` shadows the one installed in the image.
- **`depends_on: condition: service_healthy`** for anything with a real healthcheck; plain
  `depends_on` waits for the container to exist, not for the database to accept
  connections.
- **Override files** — `docker-compose.override.yml` is picked up automatically for local
  settings; keep anything production-shaped in an explicitly named file so it can never be
  the default.
- **`server.host: true` in `vite.config.ts`** when a Vite dev server runs in a container:
  Vite binds localhost by default, which is unreachable from outside it.

## .dockerignore

Mirror `.gitignore` and then some: `node_modules`, `dist`, `.git`, `.env*`. It is a build
speed lever (less context shipped to the daemon) and a leak guard (`.env` cannot be copied
into a layer it never reached).
