# Stage 1: Single-file JS compilation stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY src ./src
RUN npx @vercel/ncc build src/server.js -o dist

# Stage 2: Production Runner Stage
FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /app/dist/index.js ./index.js

USER appuser

EXPOSE 8000

CMD ["node", "index.js"]