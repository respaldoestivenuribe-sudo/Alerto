# ── Build stage ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# BACKEND_URL is consumed by vite.config.js at build time to configure the
# proxy target used by `vite preview`.  Railway injects this as a build arg.
ARG BACKEND_URL=http://localhost:8000
ENV BACKEND_URL=${BACKEND_URL}

RUN npm run build

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --omit=dev

# Copy the production build and vite config (needed for preview proxy)
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/vite.config.js ./vite.config.js

# BACKEND_URL must also be available at runtime so `vite preview` can read it
# from vite.config.js when the container starts.
ARG BACKEND_URL=http://localhost:8000
ENV BACKEND_URL=${BACKEND_URL}

EXPOSE 3000

CMD ["npm", "run", "preview"]