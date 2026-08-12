# 🚀 Polyglot Microservices DevSecOps Platform (`polyglot-microservices-devsecops`)

A production-grade, multi-language microservices architecture built for enterprise cloud-native deployment, CI/CD pipelines, container security scanning, and DevSecOps training.

---

## 🏗️ Architecture Overview

```text
               +-----------------------------------+
               |     React Frontend (Port 3000)   |
               | (cloudnative-micro-platform 20.9MB)|
               +-----------------+-----------------+
                                 |
                                 v
               +-----------------+-----------------+
               |    Express API Gateway (Port 8000)|
               | (cloudnative-micro-gateway 87.5MB)|
               +--------+--------+--------+--------+
                        |        |        |
         +--------------+        |        +--------------+
         |                       v                       |
         v               +-------+-------+               v
+--------+--------+      |  Product Svc  |      +--------+--------+
|  Auth Svc (Go)  |      | (Python FastAPI)|     | Payment Svc(Node|
|   (Port 8001)   |      |  (Port 8002)  |      |   (Port 8003)   |
| (auth 27.9MB)   |      | (product 293MB)|     | (payment 87.7MB)|
+--------+--------+      +-------+-------+      +--------+--------+
         |                       |                       |
         v                       +----------+------------+
+--------+--------+                         |
| MySQL DB (3306) |                         v
|  (auth-data)    |               +---------+---------+
+-----------------+               | PostgreSQL (5432) |
                                  |  (postgres-data)  |
                                  +-------------------+
```

---

## 📊 Docker Container Image Size Metrics

All Dockerfiles use multi-stage builds, non-root security execution (`appuser`), and stripped runtimes to minimize disk footprint and decrease container attack surfaces:

| Image Name | Microservice | Tech Stack | Base Image | Container Size | Compressed Registry Size | Security Vulnerabilities |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cloudnative-micro-platform` | Frontend UI | React 18 / Nginx | `nginx:alpine` | **20.9 MB** ⭐ | **~8 MB** | **0 Critical / 0 High** |
| `cloudnative-micro-auth` | Auth Service | Go 1.22 | `alpine:3.20` | **27.9 MB** ⭐ | **~10 MB** | **0 Critical / 0 High** |
| `cloudnative-micro-gateway` | API Gateway | Node.js / NCC | `alpine:3.20` | **91.4 MB** | **~28 MB** | **0 Critical** |
| `cloudnative-micro-payment` | Payment Service | Node.js / NCC | `alpine:3.20` | **91.6 MB** | **~28 MB** | **0 Critical** |
| `cloudnative-micro-product` | Product Catalog | Python 3.11 FastAPI | `python:3.11-alpine` | **211 MB** (⬇️ **82 MB smaller!**) | **~55 MB** | **0 Critical** |

---

## 💾 Persistent Storage Setup (Named Volumes)

Database storage is attached via Docker Named Volumes so your data (users, products, and payment transactions) **persists across container restarts and updates**:

* **`mysql-data`**: Mounts to `/var/lib/mysql` inside `mysql-db`.
* **`postgres-data`**: Mounts to `/var/lib/postgresql/data` inside `postgres-db`.

---

## 🚀 Step-by-Step Deployment Guide

### Option 1: Deploying with Docker Compose (Recommended)

Run the entire polyglot stack, persistent volumes, and custom `cloudnative` network with a single command:

```bash
# 1. Build and start all 7 microservice containers in background mode
docker-compose up -d --build

# 2. Check running container status
docker-compose ps

# 3. View real-time logs across all services
docker-compose logs -f
```

---

### Option 2: Deploying with Standalone Terminal Commands (No Docker Compose)

If you prefer launching containers step-by-step using terminal commands:

#### Step 1: Create Custom Network & Volumes
```bash
docker network create cloudnative 2>/dev/null || true
docker volume create mysql-data 2>/dev/null || true
docker volume create postgres-data 2>/dev/null || true
```

#### Step 2: Build All 5 Container Images
```bash
docker build -t cloudnative-micro-platform:v1.0.0 ./frontend
docker build -t cloudnative-micro-auth:v1.0.0 ./services/auth-service
docker build -t cloudnative-micro-product:v1.0.0 ./services/product-service
docker build -t cloudnative-micro-payment:v1.0.0 ./services/payment-service
docker build -t cloudnative-micro-gateway:v1.0.0 ./gateway
```

#### Step 3: Run Databases with Persistent Storage
```bash
# Start MySQL DB with mysql-data volume
docker run -d --name mysql-db --network cloudnative -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=auth_db \
  mysql:8.0

# Start PostgreSQL DB with postgres-data volume
docker run -d --name postgres-db --network cloudnative -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=product_db \
  postgres:16-alpine
```

#### Step 4: Run Microservices, Gateway & Frontend
```bash
# Start Auth Service
docker run -d --name auth-service --network cloudnative -p 8001:8001 \
  -e PORT=8001 -e MYSQL_HOST=mysql-db -e MYSQL_PORT=3306 \
  -e MYSQL_DATABASE=auth_db -e MYSQL_USER=root -e MYSQL_PASSWORD=rootpassword \
  -e JWT_SECRET=supersecretjwtkey123 \
  cloudnative-micro-auth:v1.0.0

# Start Product Service
docker run -d --name product-service --network cloudnative -p 8002:8002 \
  -e PORT=8002 -e POSTGRES_PRODUCT_HOST=postgres-db -e POSTGRES_PRODUCT_PORT=5432 \
  -e POSTGRES_PRODUCT_DB=product_db -e POSTGRES_PRODUCT_USER=postgres -e POSTGRES_PRODUCT_PASSWORD=postgres \
  cloudnative-micro-product:v1.0.0

# Start Payment Service
docker run -d --name payment-service --network cloudnative -p 8003:8003 \
  -e PORT=8003 -e POSTGRES_PAYMENT_HOST=postgres-db -e POSTGRES_PAYMENT_PORT=5432 \
  -e POSTGRES_PAYMENT_DB=product_db -e POSTGRES_PAYMENT_USER=postgres -e POSTGRES_PAYMENT_PASSWORD=postgres \
  cloudnative-micro-payment:v1.0.0

# Start API Gateway
docker run -d --name api-gateway --network cloudnative -p 8000:8000 \
  -e PORT=8000 -e AUTH_SERVICE_URL=http://auth-service:8001 \
  -e PRODUCT_SERVICE_URL=http://product-service:8002 -e PAYMENT_SERVICE_URL=http://payment-service:8003 \
  cloudnative-micro-gateway:v1.0.0

# Start Frontend Application UI
docker run -d --name frontend-app --network cloudnative -p 3000:80 \
  cloudnative-micro-platform:v1.0.0
```

---

## 🔍 How to Inspect Database Data

### 1. Inspect MySQL Data (`auth_db`)
```bash
docker exec -it mysql-db mysql -u root -prootpassword auth_db -e "SELECT * FROM users;"
```

### 2. Inspect PostgreSQL Data (`product_db`)
```bash
# Check Products Table
docker exec -it postgres-db psql -U postgres -d product_db -c "SELECT * FROM products;"

# Check Payments Table
docker exec -it postgres-db psql -U postgres -d product_db -c "SELECT * FROM payments;"
```

---

## 🧪 Testing API Endpoints

```bash
# 1. API Gateway Health Check
curl http://localhost:8000/health

# 2. Login via Auth Microservice
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}'

# 3. Get Product Catalog via Product Microservice
curl http://localhost:8000/api/products

# 4. Process Payment via Payment Microservice
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "productId": 2, "amount": 49.50}'

# 5. Access Frontend UI
open http://localhost:3000
```

---

## 🧹 Cleanup Instructions

```bash
# Stop and remove containers (keeps data safe in volumes)
docker-compose down

# Stop and remove containers AND delete data volumes
docker-compose down -v
```
