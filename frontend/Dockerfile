# Development image for the React frontend. Not intended for production.

FROM node:22-bookworm-slim

ENV PNPM_HOME=/pnpm \
    PATH="/pnpm:$PATH"

RUN corepack enable && corepack prepare pnpm@10.15.0 --activate

WORKDIR /app

# Install dependencies in a layer that survives source changes.
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 5173

# Vite must bind to all interfaces to be reachable through the published port.
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
