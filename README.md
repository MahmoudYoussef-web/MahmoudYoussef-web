<h1 align="center">Mahmoud Youssef</h1>
<h3 align="center">Backend Engineer · Spring Boot · Distributed Systems</h3>

<p align="center">
  <a href="https://www.linkedin.com/in/mahmoud-youssef-dev/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="mailto:mahmoudyoussed29@gmail.com">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
</p>

---

Backend engineer focused on building **production-grade systems** — not CRUD apps.  
I care about **concurrency**, **data consistency**, **failure handling**, and **clean domain modeling**.

---

## 🔧 Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=java,spring,postgresql,mysql,redis,docker,git,github,maven,idea&perline=5" />
</p>

| Layer | Technologies |
|---|---|
| **Language & Framework** | Java 21 · Spring Boot 3 · Spring Security |
| **Data** | PostgreSQL · MySQL · Spring Data JPA · Hibernate · Raw JDBC |
| **Caching & Messaging** | Redis (Cache-Aside · Rate Limiting · Idempotency · ID Generation) |
| **Security** | JWT · Refresh Token Rotation · RBAC · HMAC Webhook Verification |
| **Payments** | Stripe Checkout · Webhook Ingestion |
| **DevOps** | Docker · Docker Compose |
| **Docs & Testing** | SpringDoc OpenAPI · JUnit 5 · Mockito |

---

## 📌 Pinned Projects

### [LogiBridge — Delivery Integration Platform](https://github.com/MahmoudYoussef-web/logibridge-backend)
> Companies create delivery orders → delivery providers accept and fulfill them

- JWT with **refresh token rotation** and reuse detection  
- **Dual-layer idempotency** — DB-backed + Redis-backed  
- **Pessimistic + optimistic locking** for concurrent order mutations  
- Domain-driven **state machine** with enforced transitions  
- Rate limiting per IP with atomic check-and-record  

`Spring Boot` `PostgreSQL` `Redis` `Spring Security` `Docker`

---

### [URL Shortener — Distributed System Design](https://github.com/MahmoudYoussef-web/url-shortener-system)
> Shorten URLs with sub-millisecond redirects and real-time click tracking

- **Distributed ID generation** via Redis INCR + AtomicLong fallback  
- **Deterministic sharding** (hashCode % N) — no routing table  
- **Cache-aside pattern** with TTL derived from DB expiration  
- **Atomic rate limiting** via Redis Lua script (no race conditions)  
- Raw JDBC — no ORM, full control over query execution  

`Spring Boot` `MySQL` `Redis` `Raw JDBC` `Docker`

---

### [E-Commerce Backend — Full Commerce Lifecycle](https://github.com/MahmoudYoussef-web/ecommerce-backend)
> Auth → Catalog → Cart → Orders → Stripe Payments → Inventory → Reporting

- **Stripe Checkout** with HMAC webhook verification  
- **Event-driven inventory**: reservation on order → commit on payment  
- **Scheduled cleanup** of expired reservations  
- **Double-entry bookkeeping** with journal entries  
- Multi-device session management with selective token revocation  

`Spring Boot` `MySQL` `Redis` `Stripe` `MapStruct` `Docker`

---

## 🧠 What I Focus On

```text
Concurrency         →  Pessimistic locking, optimistic locking, atomic operations
Consistency         →  Idempotency keys, state machines, transaction boundaries
Failure Handling    →  Token reuse detection, retry safety, graceful degradation
Security            →  JWT rotation, RBAC, rate limiting, webhook verification
System Design       →  Sharding, caching strategies, distributed ID generation
