<!-- Layout credit: the animated-SVG card layout is adapted from Avi Vashishta's profile README.
     Every card here is drawn by scripts/render_readme_cards.py from my own data and my own
     portrait, and refreshed daily by .github/workflows/update-profile-art.yml. Hand-written
     content lives in the PROFILE block at the top of that script. Spacing is baked into the
     SVGs, so keep this block free of blank lines and keep each row on one line with no spaces
     between the images. -->
<div align="center">
<a href="https://mahmoud-youssef.vercel.app"><img src="./cards/hero.svg" width="100%" alt="Mahmoud Youssef. Backend Engineer, Java 21 and Spring Boot 3." /></a><br>
<img src="./cards/heatmap.svg" width="100%" alt="Mahmoud's contribution graph, in blue, refreshed daily" /><br>
<img src="./cards/activity.svg" width="100%" alt="Contributions in the last 12 months by month, with current streak, active days and busiest day" /><br>
<a href="https://github.com/MahmoudYoussef-web?tab=repositories"><img src="./cards/repos.svg" width="33.333%" alt="GITHUB: public repositories" /></a><a href="https://github.com/MahmoudYoussef-web?tab=repositories&amp;sort=stargazers"><img src="./cards/stars.svg" width="33.333%" alt="GITHUB: stars across my repositories" /></a><a href="https://github.com/MahmoudYoussef-web/MahmoudYoussef-web/blob/main/data/tests.json"><img src="./cards/tests.svg" width="33.333%" alt="TESTING: verified tests" /></a><br>
<picture><source media="(prefers-color-scheme: dark)" srcset="./cards/title-projects-dark.svg" /><img src="./cards/title-projects-light.svg" width="100%" alt="What I'm building" /></picture><br>
<a href="https://github.com/MahmoudYoussef-web/logibridge-backend"><img src="./cards/repo-logibridge-backend.svg" width="33.333%" alt="logibridge-backend: delivery platform linking companies and providers" /></a><a href="https://github.com/MahmoudYoussef-web/url-shortener-system"><img src="./cards/repo-url-shortener-system.svg" width="33.333%" alt="url-shortener-system: distributed URL shortener with MySQL sharding and Redis" /></a><a href="https://github.com/MahmoudYoussef-web/bloodbridge-api"><img src="./cards/repo-bloodbridge-api.svg" width="33.333%" alt="bloodbridge-api: urgent blood-request matching" /></a><br>
<a href="https://github.com/MahmoudYoussef-web/calorie-tracker-backend"><img src="./cards/repo-calorie-tracker-backend.svg" width="33.333%" alt="calorie-tracker-backend: AI nutrition tracking with HuggingFace" /></a><a href="https://github.com/MahmoudYoussef-web/attendance-management-api"><img src="./cards/repo-attendance-management-api.svg" width="33.333%" alt="attendance-management-api: QR check-in with HMAC-signed sessions" /></a><a href="https://github.com/MahmoudYoussef-web/ecommerce-backend"><img src="./cards/repo-ecommerce-backend.svg" width="33.333%" alt="ecommerce-backend: multi-tenant store with Stripe webhooks" /></a>
</div>

<p align="center">
<a href="https://mahmoud-youssef.vercel.app">portfolio</a> &nbsp;/&nbsp; <a href="https://linkedin.com/in/mahmoud-youssef-dev/">linkedin</a> &nbsp;/&nbsp; <a href="mailto:mahmoudyoussed29@gmail.com">email</a> &nbsp;/&nbsp; open to remote and international opportunities
</p>

**Backend Engineer — Java 21 · Spring Boot 3** · Cairo, Egypt. B.Sc. Computer Science, El Shorouk Academy (graduated July 2026). Backend engineering with a focus on concurrency control, transactional consistency, distributed architecture, and secure API design.

## Tech Stack

| Area | Tools |
|---|---|
| Backend | Java 21 · Spring Boot 3 · Spring Security |
| Data | PostgreSQL · MySQL · Spring Data JPA · Hibernate · Raw JDBC |
| Caching | Redis (Cache-Aside · Rate Limiting · Atomic ID Generation) |
| Payments | Stripe Checkout · Webhook Ingestion (HMAC-verified) |
| Infrastructure | Docker · Docker Compose · GitHub Actions CI/CD |
| Testing & Docs | JUnit 5 · Mockito · Testcontainers · SpringDoc OpenAPI |
| Auth & Identity | Keycloak · JWT · RBAC · Token Rotation |
| Migrations | Flyway |

## Expertise

- Distributed Systems
- Concurrency Control (Pessimistic / Optimistic Locking)
- Transactional Consistency & Idempotency
- Authentication & Authorization (JWT, RBAC, Token Rotation)
- Event-Driven Architecture
- Caching & Rate Limiting
- Payment Integration
- API Design

## Engineering Principles

- Design for correctness before optimization.
- Keep business logic independent from infrastructure.
- Prefer explicit consistency over hidden side effects.
- Build systems that remain predictable under concurrent workloads.

<details id="test-counts-by-project">
<summary>Test counts by project</summary>

Counted on the default branch of each repository: `@Test`, `@ParameterizedTest`, `@RepeatedTest` and `@TestFactory` methods, unit and integration counted once. BloodBridge is the Surefire figure from a clean `mvn test` run. These are the five projects I verified; this is **not** a total for every repository on my account.

| Project | Repository | Tests | Status |
|---|---|---:|---|
| E-commerce Backend | [ecommerce-backend](https://github.com/MahmoudYoussef-web/ecommerce-backend) | 112 | verified |
| WhatsApp Clone API | [whatsapp-clone-realtime-api](https://github.com/MahmoudYoussef-web/whatsapp-clone-realtime-api) | 84 | verified |
| BloodBridge | [bloodbridge-api](https://github.com/MahmoudYoussef-web/bloodbridge-api) | 128 | verified (Surefire: 128 run, 1 skipped, 0 failures; the old 169 claim is wrong) |
| Sofra | [restaurant-reservation-system](https://github.com/MahmoudYoussef-web/restaurant-reservation-system) | 79 | verified |
| TaskFlow | [TaskFlow](https://github.com/MahmoudYoussef-web/TaskFlow) | 11 | verified (7 unit + 4 integration) |
| **Total** |  | **414** | |

</details>
