# STAGE 1: Build Stage (Node.js)
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package descriptors for layer caching
COPY package*.json ./

# Install dependencies cleanly
RUN npm install

# Copy source code and build static production assets
COPY . .
RUN npm run build

# STAGE 2: Production Stage (Nginx Alpine Unprivileged)
FROM nginxinc/nginx-unprivileged:alpine-slim AS runner

# Copy custom Nginx configuration
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

# Explicitly Enforce Non-Root Execution (unprivileged 'nginx' user UID 101)
USER 101

# Expose unprivileged port 8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]