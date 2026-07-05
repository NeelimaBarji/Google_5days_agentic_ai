# Running DevLoop App Locally

**Stack:** Spring Boot 3.2.5 (Java 21) + React 18 + H2 in-memory DB  
**Prerequisites:** Java 21, Maven 3.9.6, Node.js 18+

---

## 1. Backend (Spring Boot)

### First-time setup
Make sure `application.properties` exists at:
```
backend/src/main/resources/application.properties
```

It must contain (already done — do not delete):
```properties
spring.jpa.defer-datasource-initialization=true
spring.sql.init.mode=always
spring.jpa.hibernate.ddl-auto=create-drop
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

> **Why:** Spring Boot 3.x runs `data.sql` before JPA creates tables by default.
> `defer-datasource-initialization=true` fixes the `Table "PRODUCT" not found` error.

### Start backend
```bash
cd /Users/sunilkumargorle/Desktop/Neelima/AI/Google_agentic_ai_5day_course/CapstoneProject/devloop/backend

~/apache-maven-3.9.6/bin/mvn spring-boot:run
```

### Verify
```bash
# Should return JSON list of 7 products
curl http://localhost:8080/api/products

# H2 database console (browser)
open http://localhost:8080/h2-console
# JDBC URL: jdbc:h2:mem:devloopdb
# Username: sa  |  Password: (blank)
```

### Stop
`Ctrl+C` in the terminal running the backend.

---

## 2. Frontend (React)

### First-time setup (if node_modules missing or corrupted)
```bash
cd /Users/sunilkumargorle/Desktop/Neelima/AI/Google_agentic_ai_5day_course/CapstoneProject/devloop/frontend

# If you see EINVALIDTAGNAME or any npm errors, clean install:
rm -rf node_modules package-lock.json
npm install
```

> **Why:** A partial or interrupted `npm install` can corrupt `package-lock.json`
> causing `npm error code EINVALIDTAGNAME`. Fresh install always fixes it.

### Start frontend
```bash
cd /Users/sunilkumargorle/Desktop/Neelima/AI/Google_agentic_ai_5day_course/CapstoneProject/devloop/frontend

npm start
```

Opens automatically at **http://localhost:3000**

> **Note:** Backend must be running on :8080 first — frontend proxies API calls to it via `"proxy": "http://localhost:8080"` in `package.json`.

### Verify
- Browser opens http://localhost:3000
- Product list loads with 7 products
- Discount column visible on each product

### Stop
`Ctrl+C` in the terminal running the frontend.

---

## 3. Run Both Together (Quick Start)

Use the launcher script to start backend + frontend in one command:

```bash
cd /Users/sunilkumargorle/Desktop/Neelima/AI/Google_agentic_ai_5day_course/CapstoneProject

bash run-devloop.sh
```

This script:
1. Starts Spring Boot backend, waits until `:8080` is healthy
2. Runs `npm install` if `node_modules` is missing
3. Starts React frontend, waits until `:3000` is healthy
4. Then runs `python devloop.py run PROD-1` (the agent pipeline)

To stop both:
```bash
# PIDs are printed at end of script output
kill <BACKEND_PID> <FRONTEND_PID>
```

---

## 4. Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Table "PRODUCT" not found` | `data.sql` runs before JPA creates tables (Spring Boot 3.x) | Add `spring.jpa.defer-datasource-initialization=true` to `application.properties` |
| `npm error EINVALIDTAGNAME "#"` | Corrupted `package-lock.json` | `rm -rf node_modules package-lock.json && npm install` |
| `Could not find index.html in public/` | `public/` folder missing | File exists at `frontend/public/index.html` (already created) |
| `Port 8080 already in use` | Previous backend still running | `lsof -ti:8080 \| xargs kill` |
| `Port 3000 already in use` | Previous frontend still running | `lsof -ti:3000 \| xargs kill` |
| `JAVA_HOME not set` | Java 21 not on PATH | `export JAVA_HOME=$(/usr/libexec/java_home -v 21)` |

---

## 5. API Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products |
| GET | `/api/products?category=ELECTRONICS` | Filter by category |
| GET | `/api/products/{id}` | Get single product |
| POST | `/api/products` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| GET | `/api/products/low-stock?threshold=10` | Low stock alert |

**Example — create product with discount:**
```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "Testing discount field",
    "price": 49.99,
    "discount": 0.20,
    "category": "ELECTRONICS",
    "stock": 50,
    "sku": "TEST-001",
    "status": "ACTIVE"
  }'
```
