FROM node:20-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
COPY asset/Logo ./public/logo

CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0 --port ${PORT:-3000}"]
