<h1 align="center">Mahmoud Youssef</h1>
<h3 align="center">Backend Engineer · Spring Boot · Distributed Systems</h3>

<p align="center">
  <a href="https://www.linkedin.com/in/mahmoud-youssef-ba30723bb/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="mailto:mahmoudyoussed29@gmail.com">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
</p>

---

Backend engineer focused on building **production-grade systems** — not CRUD apps.  
I care about **concurrency**, **data consistency**, **failure handling**, and **clean domain modeling**.

<p align="center">
  <img src="https://img.shields.io/badge/200%2B%20concurrent%20req%2Fsec-sub--150ms-3fb950?style=flat-square" />
  &nbsp;
  <img src="https://img.shields.io/badge/5K%2B%20URL%20creations%2Fsec-zero%20collisions-58a6ff?style=flat-square" />
  &nbsp;
  <img src="https://img.shields.io/badge/Freelance-Jan%202025%20–%20Present-a371f7?style=flat-square" />
</p>

---

## 🔧 Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=java,spring,postgresql,mysql,redis,docker,git,github,maven,idea&perline=5" />
</p>

| Layer | Technologies |
|---|---|
| **Language & Framework** | Java 21 · Spring Boot 3 · Spring Security |
| **Data** | PostgreSQL · MySQL · Spring Data JPA · Hibernate · Raw JDBC |
| **Caching & Idempotency** | Redis (Cache-Aside · Lua Scripts · Rate Limiting · SET NX · ID Generation) |
| **Security** | JWT · Refresh Token Rotation · RBAC · HMAC Webhook Verification |
| **Payments** | Stripe Checkout · Webhook Ingestion |
| **DevOps** | Docker · Docker Compose |
| **Docs & Testing** | SpringDoc OpenAPI · JUnit 5 · Mockito · JMeter |

---

## 💼 Work Experience

### Freelance Backend Engineer — LogiBridge (B2B Logistics Platform) `Jan 2025 – Present`

> Sole backend engineer on a delivery coordination platform: companies create orders → delivery providers accept and fulfill them

- Sole backend engineer; architected and deployed end-to-end **Java / Spring Boot 3** order-management system on Railway with **15+ RESTful endpoints** and live **Swagger / OpenAPI** documentation
- Implemented multi-role **RBAC** via **Spring Security** `@PreAuthorize`, enforcing role-scoped access across all endpoints with zero privilege escalation incidents
- Enforced exactly-once order state transitions via **dual-layer idempotency** (PostgreSQL unique constraint + Redis SET NX) and **PESSIMISTIC_WRITE** locking with `@Version` optimistic locking, eliminating lost updates under concurrent requests
- Implemented **JWT refresh token rotation** with reuse detection; enforced atomic rate limiting per IP via **Redis Lua script**, eliminating TOCTOU race conditions
- Load-tested with JMeter sustaining **200+ concurrent requests at sub-150ms** avg latency; validated retry and concurrency correctness via **JUnit 5** unit and integration tests

---

## 📌 Projects

### [E-Commerce Backend — Full Commerce Lifecycle](https://github.com/MahmoudYoussef-web/ecommerce-backend)

> Auth → Catalog → Cart → Orders → Stripe Payments → Inventory → Reporting

- Designed full e-commerce **RESTful API** with **Spring Boot 3**, **Spring Data JPA**, and **Hibernate** across **30+ endpoints** using event-driven architecture (OrderCreatedEvent, PaymentCompletedEvent)
- Prevented duplicate payment execution via idempotent **Stripe webhook** ingestion with dual-signature verification (Stripe-Signature + HMAC) — exactly-once side effects under replay attacks
- Eliminated overselling using two-phase inventory reservation with optimistic locking; reduced read latency **~40%** via **Redis** cache-aside with consistent invalidation
- Built **double-entry bookkeeping** with Hibernate JPA and SQL aggregation queries for real-time revenue reporting and admin dashboard metrics

`Spring Boot 3` `MySQL` `Redis` `Stripe` `Spring Data JPA` `Docker`

---

### [Distributed URL Shortener](https://github.com/MahmoudYoussef-web/url-shortener-system)

> 5K+ URL creations/sec · Zero collisions · Graceful degradation on Redis failure

- Engineered distributed ID generation via **Redis INCR + Base62** encoding, handling **5K+ URL creations/sec** with zero collisions; AtomicLong fallback activates automatically on Redis failure
- Implemented deterministic **database sharding** (hashCode % N) — no routing table, no cross-shard coordination; **atomic rate limiting** via Redis Lua script eliminating TOCTOU race conditions

`Spring Boot 3` `MySQL` `Redis` `Raw JDBC` `Docker`

---

### [Calorie Tracker — AI-Powered Nutrition Backend](https://github.com/MahmoudYoussef-web/calorie-tracker-backend)

> 4-stage CV pipeline: Mask R-CNN → YOLO-CSP → Volume Estimation → USDA Calorie Lookup

- Built nutrition **RESTful API** with **Spring Boot** integrating a 4-stage CV pipeline (Mask R-CNN segmentation → YOLO-CSP classification → volume estimation → USDA calorie lookup) for automatic food detection from photos
- Enforced **JWT-based RBAC** via **Spring Security** with per-user data isolation; integrated MapStruct to eliminate DTO boilerplate across 10+ entity-DTO pairs, reducing manual code by **~200 lines**

`Spring Boot` `MySQL` `JWT` `YOLO` `MapStruct` `Docker`

---

## 🧠 What I Focus On

```text
Concurrency         →  Pessimistic locking, optimistic locking, atomic operations
Consistency         →  Idempotency keys, state machines, transaction boundaries
Failure Handling    →  Token reuse detection, retry safety, graceful degradation
Security            →  JWT rotation, RBAC, rate limiting, webhook verification
System Design       →  Sharding, caching strategies, distributed ID generation
```
