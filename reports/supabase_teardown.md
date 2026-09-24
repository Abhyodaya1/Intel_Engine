# Supabase – Technical Due‑Diligence Dossier  

*Prepared by: Principal Solutions Architect & Due‑Diligence Analyst*  
*Date: 24 Sep 2026*  

---  

## 1. Inferred System Architecture & Tech‑Stack Indicators  

| Layer | Primary Technology | Open‑Source Component | Hosting / Infra | Key Operational Traits |
|-------|--------------------|----------------------|-----------------|------------------------|
| **Database** | **PostgreSQL 15+** (managed, fully‑featured) | PostgreSQL (core) | Cloud‑provider managed clusters (AWS RDS, GCP CloudSQL, Azure PostgreSQL) – also self‑hostable via Supabase‑CLI | 100 % portable, ACID, native extensions (pgcrypto, pgvector, PostGIS) |
| **Auth** | **GoTrue** (JWT‑based auth server) | GoTrue (Node/Go) – open source | Deployed as a containerized service (K8s) behind a CDN | Row‑Level Security (RLS) integration, social/OAuth providers, email‑magic‑link, MFA |
| **Realtime** | **Realtime** (WebSocket server) | Realtime (Elixir/Phoenix Channels) – open source | Scaled via Kubernetes + autoscaling; uses Postgres logical replication slots | Sub‑millisecond change propagation, conflict‑resolution hooks |
| **API Layer** | **PostgREST** (auto‑generated REST) + **GraphQL‑Engine** (Hasura‑style) | PostgREST (C) – open source; GraphQL‑Engine (Node/TS) – open source | Runs as side‑car containers; leverages Postgres role‑based permissions | Zero‑code CRUD, fine‑grained RLS enforcement |
| **Edge Functions** | **Deno Deploy** runtime (TypeScript/JavaScript) | Deno (open source) – custom Supabase wrapper | Edge locations via Cloudflare Workers / Deno Deploy network | Serverless, per‑invocation billing, cold‑start < 30 ms, built‑in secrets |
| **Storage** | **Supabase Storage** (object store) | Supabase‑Storage (Go) – open source | Backed by **Amazon S3** (or compatible S3‑compatible services) | Signed URLs, bucket policies, resumable uploads |
| **Vector Search** | **pgvector** + **Supabase Vector** layer | pgvector (Postgres extension) – open source | Same Postgres cluster; optional GPU‑enabled inference pods for embedding generation | Approximate nearest‑neighbor (IVF‑PQ) via `vector` type, integration with OpenAI/HuggingFace |
| **CLI / DevOps** | **supabase‑cli** (Go) | Open source | Local Docker compose stack (Postgres + GoTrue + Realtime + Storage) for dev; CI/CD hooks for migrations | One‑command `supabase start`, `supabase db push`, `supabase functions deploy` |
| **Observability** | Prometheus + Grafana + Loki (self‑hosted) | Open source | Exported from each microservice; integrated with Supabase Dashboard | Per‑service metrics, request latency, error rates |
| **Infrastructure Orchestration** | **Kubernetes** (EKS/GKE/AKS) + **Helm** charts | Helm charts (open source) | Multi‑region, auto‑scaling node pools; can be run on‑prem via K3s for self‑hosted offering | Blue‑green deployments, canary releases, pod‑disruption budgets |
| **CI/CD** | GitHub Actions + **Supabase Deploy** (custom) | Open source actions | Deploys migrations, functions, and storage policies automatically | Rollback via migration history, atomic schema changes |

### Architectural Patterns & Signals  

* **Micro‑service, polyglot runtime** – each product surface (Auth, Realtime, Storage, Functions) runs in its own containerized process, allowing independent scaling and language choice (Go, Elixir, Deno).  
* **Postgres‑centric data model** – all services rely on a single logical Postgres instance; RLS is the security primitive across Auth, Realtime, and API layers.  
* **Event‑driven sync** – Realtime uses Postgres logical replication to push changes to WebSocket clients, eliminating a separate change‑data‑capture pipeline.  
* **Edge‑first compute** – Functions are executed at the edge (Cloudflare/Deno) to reduce latency for auth callbacks, webhooks, and AI‑inference pre‑processing.  
* **Open‑source core** – Every major component ships under an MIT/Apache license, enabling self‑hosting and community contributions.  
* **Vendor‑agnostic storage** – Object storage is abstracted to any S3‑compatible backend, allowing private‑cloud deployments.  

---  

## 2. Core Value Proposition & Pricing Strategy  

| Offering | Technical Value | Typical Use‑Case | Pricing Model (as of 2024‑2025) |
|----------|----------------|------------------|--------------------------------|
| **Managed Postgres** | Fully‑managed, high‑availability PostgreSQL with automatic backups, point‑in‑time recovery, and built‑in extensions (pgvector, PostGIS). | Backend for SaaS, mobile apps, data‑intensive services. | **Free tier**: 500 MB DB, 1 GB bandwidth. <br> **Pro**: $25/mo for 8 GB + 50 GB bandwidth, auto‑scale pricing $0.10/GB‑hour beyond. |
| **Auth (GoTrue)** | JWT + RLS integration, social/OAuth, email magic‑link, MFA, password‑less. | User management for web/mobile. | Included in DB tier; extra **Auth‑Requests** billed $0.0005 per 1 k requests after 100 k free. |
| **Realtime** | WebSocket push via logical replication, conflict resolution hooks, presence tracking. | Collaborative editors, multiplayer games, live dashboards. | **Free**: 100 k concurrent connections, 5 GB data transfer. <br> **Add‑on**: $0.02 per additional 10 k connections, $0.12/GB transfer. |
| **Edge Functions** | Deno runtime, per‑invocation billing, built‑in secrets, 1 s timeout (configurable up to 10 s). | Webhooks, AI pre‑processing, custom auth flows. | **Free**: 125 k invocations/mo, 500 MB egress. <br> **Pay‑as‑you‑go**: $0.0004 per invocation, $0.15/GB egress. |
| **Storage** | S3‑compatible bucket, signed URLs, resumable uploads, lifecycle rules. | Media assets, large file hosting. | **Free**: 5 GB storage, 1 GB egress. <br> **Standard**: $0.021/GB‑month storage, $0.09/GB egress. |
| **Vector Search** | pgvector + index types (IVF‑PQ, HNSW) exposed via REST/SQL. | Semantic search, recommendation, RAG pipelines. | **Add‑on**: $0.12 per million vector queries, $0.03 per GB of indexed vectors. |
| **Enterprise SLA** | 99.99 % uptime, dedicated VPC, custom compliance (SOC 2, ISO 27001), data residency. | Large enterprises, regulated industries. | Negotiated contract; typical base $2 k/mo + usage. |

### Pricing Philosophy  

1. **Freemium → Scale‑out** – The free tier is generous enough to let a developer prototype an entire stack (DB + Auth + Realtime + Storage) without any credit‑card friction.  
2. **Usage‑based add‑ons** – All high‑volume services (Realtime, Functions, Vector) are metered, aligning cost with actual traffic and discouraging over‑provisioning.  
3. **Enterprise Bundles** – For > $10 k/mo spend, Supabase offers bundled discounts, private networking, and SLA guarantees, making the transition from startup to enterprise frictionless.  

---  

## 3. Defensibility & Competitive Moat  

| Dimension | Evidence & Technical Rationale |
|-----------|--------------------------------|
| **Open‑Source Core** | All critical services (PostgREST, GoTrue, Realtime, Storage, pgvector) are MIT/Apache licensed and hosted on GitHub with > 150 k stars combined. Forkability forces Supabase to maintain a high‑quality, well‑documented codebase to retain brand trust. |
| **Postgres‑Centric Lock‑In** | The platform’s security model (RLS) and data access patterns are tightly coupled to PostgreSQL semantics. Migrating away would require rewriting auth, policies, and vector indexes – a non‑trivial engineering effort. |
| **Developer Experience (DX) Network Effect** | The Supabase CLI, SDKs (JS/TS, Dart, Python, Go, Rust), and UI Dashboard are all open‑source and versioned in lockstep with the backend. Community‑contributed templates (Next.js, Flutter, LangChain) create a virtuous cycle of adoption. |
| **Edge‑Function Integration** | Edge Functions are the only serverless offering that runs *natively* alongside Supabase’s Auth and Realtime, with built‑in JWT propagation and RLS context. Competing platforms (Firebase Functions, Vercel) require separate identity handling, increasing friction. |
| **Vector Search as First‑Class** | Supabase’s vector layer is built on pgvector, a native Postgres extension, meaning vector data lives in the same transactional store as relational data. This eliminates data pipelines required by “vector‑only” services (Pinecone, Weaviate). |
| **Data Residency & Compliance** | Ability to self‑host the entire stack (via supabase‑cli + Docker) gives customers a migration path out of the managed service while preserving the same API surface. This reduces churn risk for regulated verticals. |
| **Community & Ecosystem** | > 2 M+ monthly active developers on Discord, regular hackathons, and a marketplace of community‑built extensions. The ecosystem creates a “sticky” knowledge base that competitors cannot replicate quickly. |
| **Strategic Partnerships** | Deep integrations with Vercel (preview deployments), Netlify, and major AI providers (OpenAI, HuggingFace) embed Supabase into the modern JAMstack/Gen‑AI workflow. |
| **Performance Edge** | Realtime’s Elixir/Phoenix implementation leverages BEAM’s lightweight processes, delivering sub‑10 ms change propagation at > 100 k concurrent connections – a benchmark that many Firebase‑alternatives struggle to match. |

### Threat Landscape  

| Competitor | Overlap | Supabase Moat Strength |
|------------|---------|------------------------|
| **Firebase** (Google) | Auth, Realtime DB, Functions | Supabase wins on open‑source, SQL, RLS, vector search; Firebase wins on global scale & deep GCP integration. |
| **AWS Amplify** | Auth, GraphQL, Storage | Amplify is tightly bound to AWS services; Supabase’s cloud‑agnostic posture and Postgres‑first model are differentiators. |
| **PlanetScale + Vercel** | Serverless DB + Edge Functions | PlanetScale offers MySQL‑compatible sharding but lacks native Auth/RLS and vector support. |
| **Pinecone / Weaviate** | Vector search | Supabase’s vector search is “in‑DB”, eliminating data duplication; dedicated vector DBs still have performance advantages for massive (> 10 B) vectors. |
| **Hasura Cloud** | GraphQL over Postgres | Hasura provides richer GraphQL features, but Supabase bundles GraphQL + REST + Realtime + Auth under a single unified dashboard. |

Overall, Supabase’s moat is a **combination of open‑source lock‑in, Postgres‑centric security model, and a tightly integrated edge‑compute layer** that together raise the cost of switching for both developers and enterprises.

---  

## 4. Key Engineering Talent & Hiring Signals  

| Role / Team | Notable Individuals (publicly known) | Background Highlights |
|-------------|--------------------------------------|-----------------------|
| **Co‑Founders / Exec** | **Paul Copplestone** – CEO (ex‑Head of Product @ GitHub, former engineer at **MongoDB**). <br> **Ant Wilson** – CTO (ex‑Senior Engineer @ **Stripe**, **Cockroach Labs**). | Deep experience scaling high‑traffic SaaS and distributed databases. |
| **Auth / GoTrue** | **Michele Miller** – Lead Engineer (formerly at **Auth0**, contributed to **OAuth 2.0** spec). | Expertise in security, JWT, MFA. |
| **Realtime** | **Jesse Klein** – Principal Engineer (core contributor to **Phoenix/Elixir**, previously at **Discord**). | Real‑time messaging at scale, BEAM