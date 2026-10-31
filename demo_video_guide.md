# ReconGuard: 3-Minute Demo Video Guide
**ExaThon India 2026 | Track 01: Money, Risk & Regulation**
**Team Name**: codeleon
**Target Video Duration**: 2 minutes 50 seconds (Under the 3-minute strict limit)

---

## Video Outline & Timestamped Screen Cues

| Timestamp | Visual / Screen Action | Narration & Audio Script |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Show Title Slide & Problem Context in Dashboard | *"Hello judges, welcome to ReconGuard, built by Team codeleon for Track 01: Money, Risk & Regulation. Every day, financial institutions process millions of transactions across UPI, card networks, and Core Banking. 2 to 5% break—due to gateway fee deductions, network timeouts, and truncated narrative strings. These breaks sit in suspense accounts, delaying month-end close by up to a week. ReconGuard solves this by uniting Exasol Personal's in-memory columnar engine with a governed AI write path."* |
| **0:30 - 1:05** | Click **"Ingest Live Feeds"** (5,000 txns) & **"Run Exasol Columnar SQL Recon"** | *"Watch this: We ingest 5,000 multi-rail transactions. With a single click, we fire Exasol's vectorized SQL matching engine. In just 24 milliseconds, Exasol executes parallel equi-joins, fee-tolerance reconciliation, and cutoff time-drift windows—resolving over 96% of volume natively at database speed. Notice the breakdown: clean 1:1 matches, gateway MDR fees accounted for, and residual anomalies isolated into the Suspense Breaks Queue."* |
| **1:05 - 1:40** | Switch to **Tab 2 (Suspense Breaks)** & **Tab 3 (Governed AI Agent)** | *"Now look at the remaining breaks. Under strict RBI and DPDP regulations, you cannot leak customer PII. ReconGuard automatically masks account numbers and customer names with cryptographic tokens. We now trigger Gemini Flash. Notice that our agent never touches the production database directly. Instead, it analyzes mutated references and merchant narratives, staging proposed adjusting journal entries onto an isolated shadow branch."* |
| **1:40 - 2:20** | Switch to **Tab 4 (Shadow Branch Diff & Byte-for-Byte Undo)** | *"Here in Tab 4, we see the Drydock-style governance layer. The compliance officer reviews row-level diffs, confidence scores, and natural language audit justifications. We can approve and merge all adjustments to production with a single click. Notice the cryptographic SHA-256 ledger hash update. And if an auditor or manager ever needs to roll back? Watch this: click 'Execute Byte-for-Byte Undo'—and the production ledger is instantly restored to its exact previous state with verified byte-level hash equivalence!"* |
| **2:20 - 2:50** | Switch to **Tab 5 (Audit Log)** & Closing slide | *"Every merge and undo action is cryptographically recorded in the immutable audit trail. ReconGuard reduces month-end close from 7 days to under 24 hours, eliminates PII leakage risk, and brings true enterprise governance to AI-assisted finance. Full code, Exasol DDL, and pitch deck are open-source on GitHub. Thank you!"* |

---

## Recording Tips for the Team
1. **Screen Resolution**: Record in 1080p (1920x1080) with browser zoom set to 100% or 110% for crisp text.
2. **Audio**: Use a clear USB microphone or headset in a quiet room.
3. **Pacing**: Speak at a steady, confident pace. Follow the timing cues above.
4. **Tool Recommendation**: Use Loom, OBS Studio, or QuickTime Screen Recording.
