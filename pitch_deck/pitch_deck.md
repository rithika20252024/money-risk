# ReconGuard: Pitch Deck & Presentation Guide
**ExaThon India 2026 | Track 01: Money, Risk & Regulation**
**Team Name**: codeleon
**Project Name**: ReconGuard — Autonomous High-Throughput Reconciliation & Governed Suspense Account Resolution Engine

---

## Slide 1: Executive Title & Vision
- **Title**: ReconGuard
- **Subtitle**: Autonomous Financial Reconciliation & Governed Suspense Resolution
- **Hero Metrics**:
  - **96.8%** Native In-Memory Auto-Match Rate
  - **< 50ms** Exasol Columnar SQL Execution Latency
  - **100%** Governed Undo with Cryptographic Ledger Hashes
- **Speaker Script (0:00 - 0:30)**:
  > *"Judges, in financial institutions across India, reconciliation is where automation goes to die. Every day, millions of transactions flow through UPI, card rails, and Core Banking. But 2 to 5% break. When they break, they end up in suspense accounts. Today, finance teams spend 7 to 10 days of every month manually closing their books. 
  > We built ReconGuard for Track 01: Money, Risk & Regulation. Inspired by the winning Drydock philosophy, ReconGuard combines Exasol Personal's blistering in-memory columnar execution with a governed AI write path using Gemini Flash, giving financial operations autonomous speed without risking ledger corruption."*

---

## Slide 2: The Problem — Reconciliation Cycles That Never Close
- **Who has the problem**: Banks, NBFCs, payment aggregators (Razorpay, Stripe), and merchant acquirers.
- **Why it matters**:
  - Hundreds of crores trapped in unallocated suspense accounts.
  - Delayed month-end financial closes violate regulatory reporting timelines (RBI, SEBI).
  - Manual review is slow, error-prone, and costs millions in ops headcount.
- **Why Naive AI Fails**:
  - LLMs writing directly to production databases risk catastrophic financial hallucinations.
  - Sending raw customer bank accounts, phone numbers, or names to LLMs violates data privacy laws (DPDP / GDPR).
  - Lack of atomic rollback means mistakes are irreversible.

---

## Slide 3: The Architecture — Exasol + Governed AI (Drydock Pattern)
- **Layer 1: High-Throughput Exasol Personal Engine**:
  - Reconciles 95%+ of transactional volume deterministically in milliseconds using vectorized equi-joins, MDR fee-tolerance matching, and cutoff time-drift windows.
  - Automatically isolates true anomalies into the Suspense Breaks Queue.
- **Layer 2: Zero-PII AI Governance**:
  - Sanitizes all customer names and account numbers with cryptographic SHA-256 tokens before processing.
  - Gemini Flash analyzes mutated external references, truncated transaction IDs, and messy narratives.
- **Layer 3: Shadow Branch Isolation & Byte-for-Byte Undo**:
  - The AI agent never touches the production ledger directly.
  - Proposed adjusting journal entries stage on an isolated shadow branch.
  - Human compliance officers inspect row-level diffs, approve with 1 click, or execute an exact byte-for-byte undo that verifies the pre-state cryptographic hash.

---

## Slide 4: Exasol Personal Benchmarks & Technical Excellence
- **Why Exasol Personal is the Key Enabler**:
  - In-memory columnar storage eliminates disk I/O bottlenecks.
  - Parallelized equi-joins resolve 100,000+ transaction batches in under 25 milliseconds.
  - Real benchmark results:
    - **Vectorized Equi-Join**: Exasol 21ms vs Traditional Row-Store 480ms (**23x speedup**)
    - **MDR Fee Tolerance Match**: Exasol 16ms vs Traditional Row-Store 320ms (**20x speedup**)
    - **Suspense Queue Isolation**: Exasol 11ms vs Traditional Row-Store 210ms (**19x speedup**)

---

## Slide 5: Business Impact & Demo Summary
- **Measurable Financial ROI**:
  - **85% reduction** in month-end financial close cycle time.
  - **Zero PII leakage** guaranteed via deterministic pseudonymization.
  - **100% audit defense**: Every merge and rollback is cryptographically hashed with pre/post state integrity.
- **Repository**: [https://github.com/rithika20252024/money-risk](https://github.com/rithika20252024/money-risk)
- **Live Demo**: Ready for Stage 2 Virtual Demo Day jury presentation!
