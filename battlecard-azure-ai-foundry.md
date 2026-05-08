# Competitive Battlecard: Akka vs. Microsoft Azure AI Foundry

**For:** NTT Data — Enterprise Agentic Grid sales teams
**Use:** Customer-facing competitive positioning when Azure AI Foundry is the incumbent or alternative
**Last updated:** 2026-04-24

---

## TL;DR — Why Akka Wins

| Dimension | Azure AI Foundry | Akka |
|-----------|-----------------|------|
| **Infrastructure cost** | 6-8 separately billed services; egress fees, PTU minimums, per-GB logging | Shared compute model — up to 90% lower infrastructure cost |
| **HA/DR** | No SLA on Agent Service; no automatic failover; total state loss on region failure | 99.9999% availability; active-active HA/DR; sub-1 min RTO, zero byte RPO |
| **Lock-in** | Tight coupling to Azure identity, compute, orchestration, and data services | Deploy on any cloud, on-prem, or Akka's cloud; no proprietary lock-in |
| **Sovereign cloud** | Feature-lagged, limited AI service availability, control plane metadata may leave region | Full-parity sovereign cloud with data isolation, networking isolation, local SREs |
| **Governance / EU AI Act** | Fragmented across 5+ services; no inline explainability; no human override dashboard; no pre-deployment classification | Embedded runtime governance + full pre-production governance platform: classify against 175 frameworks, multi-persona sign-offs, Governance Posture Packages |

---

## 1. Infrastructure Cost: 70-90% Cheaper with Akka

### The Azure Hidden Cost Problem

Enterprise agentic AI on Azure requires stitching together 6-8 separately billed services, each with its own pricing model:

| Azure Service | Role | Cost Trap |
|---------------|------|-----------|
| Azure OpenAI Service | LLM inference | Per-token billing or PTU commitments (~$73k/mo minimum for provisioned throughput) |
| Azure Cosmos DB | Agent state / memory | Per-RU billing; multi-region writes multiply cost; ~200ms latency for memory |
| Azure AI Search | RAG retrieval | $250-$2,000+/mo per tier; semantic ranking is an add-on |
| Azure Event Hubs | Event-driven orchestration | Per-throughput-unit billing |
| Azure API Management | Gateway / governance | $700-$2,800/mo per unit |
| Azure Monitor / App Insights | Observability | $2.76/GB ingestion; verbose agent tracing causes cost to balloon |
| Azure Content Safety | Guardrails | Separate per-call billing |
| Private Endpoints | Security | ~$7.30/mo each + data processing charges |

**Plus hidden fees:**
- **Egress charges**: ~$0.087/GB after first 100GB/mo — adds up fast in multi-region or hybrid deployments
- **Premium support**: Unified Support starts ~$50k/yr — required for production AI SLAs
- **Storage transactions**: Read/write operations charged separately from capacity

### Why Akka Is 70-90% Cheaper

Akka runs orchestration, agents, memory, streaming, and APIs on **shared compute** — one platform, one bill. There are no separate charges for memory, streaming, observability, or governance because they are all part of the platform.

**Talk track:** *"With Azure, you're paying 6-8 separate cloud bills that compound unpredictably. With Akka's shared compute model, your orchestration, agents, memory, streaming, APIs, and governance all run on the same compute — cutting infrastructure costs by 70-90%. And Akka scales to zero when idle, so you only pay for what you use."*

---

## 2. HA/DR: Akka Has It Now — Azure Says 2-3 Years

### Azure AI Foundry Has No HA/DR

This is not speculation — it is stated in Microsoft's own documentation:

> **"Agent Service has no availability or state durability Service Level Agreement (SLA)."**
> — [Microsoft Learn: HA/DR for Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/high-availability-resiliency)

> **"Foundry itself doesn't provide automatic failover or disaster recovery."**

> **"Agent Service doesn't provide built-in disaster recovery capabilities. It doesn't replicate state, create backups, or support point-in-time restore."**

> **"The recovery point for stateful content can be total loss."**

| Metric | Azure AI Foundry | Akka |
|--------|-----------------|------|
| Availability SLA | **No SLA** (Agent Service); 99.9% (Azure OpenAI only) | **99.9999%** — contractual, backed by indemnities |
| HA/DR mode | Active-passive, manual failover only | **Active-active**, automatic |
| RTO | 30+ minutes per project (manual reconstruction) | **Sub-1 minute** |
| RPO | **Total state loss possible** | **Zero byte** |
| Multi-region | **"No supported method for active-active multi-region replication"** | Active-active across 20+ regions |
| State during failover | All agent state is lost; state created during failover is lost on failback | Fully preserved |

### Real-World Azure AI Outages

- **Jan 27, 2026**: Azure OpenAI Sweden Central — 7-hour outage. EU customers with GDPR-mandated single-region deployment had **zero failover options**.
- **Mar 9-10, 2026**: Azure OpenAI GPT-5.2 — 20-hour outage across **7 regions simultaneously**. Azure's own telemetry failed, compounding the impact.
- **Oct 29, 2025**: Azure Front Door global outage — 7 hours, affecting Copilot and AI services globally.

**Talk track:** *"Microsoft's own documentation says their AI Agent Service has no SLA, no automatic failover, and that total data loss is a planned-for scenario. We've heard from accounts like Manulife that Microsoft has told them AI HA/DR is 2-3 years out on their roadmap. Akka delivers 99.9999% availability with active-active HA/DR today — sub-1 minute RTO, zero byte RPO, backed by contractual indemnities."*

### Manulife: Microsoft's Largest Canadian Customer Chose Akka

Manulife — the #1 life insurance company for AI maturity and Microsoft's largest Canadian customer — evaluated Azure AI Foundry and chose Akka for their enterprise agentic AI platform. The deciding factors: Akka's cost effectiveness and production-ready HA/DR. Manulife selected Akka to operationalize agentic AI for customer and colleague decision-making at enterprise scale. ([akka.io/blog/manulife-selects-akka-to-operationalize-agentic-ai](https://akka.io/blog/manulife-selects-akka-to-operationalize-agentic-ai))

**Why this matters in every deal:** If Microsoft cannot retain their own largest Canadian customer for agentic AI, what does that say about Azure AI Foundry's readiness? Manulife had every reason to stay on Azure — existing EA, deep Microsoft relationship, significant Azure investment. They chose Akka anyway because Azure could not deliver on cost or HA/DR.

**Talk track:** *"Manulife is Microsoft's largest Canadian customer. They evaluated Azure AI Foundry for their agentic AI platform and chose Akka — because Azure couldn't match our cost model or deliver HA/DR. If Microsoft's own top customer chose us, that tells you everything about the production readiness gap."*

---

## 3. No Lock-In: Akka Is Portable, Azure Is Not

### Azure Lock-In Is Structural

Azure AI Foundry creates lock-in at every layer:

- **Identity**: Requires Azure Entra ID — not portable
- **Orchestration**: Prompt Flow uses Azure-proprietary YAML format — rewrite required to move
- **Compute**: Managed endpoints use Azure-specific MLflow extensions
- **Data**: Once data lands in Cosmos DB + AI Search indexes, migration incurs egress fees and full index rebuilds
- **Models**: Fine-tuned models on Azure OpenAI cannot be exported
- **Governance**: Purview, Content Safety, API Management — all Azure-only

### Akka Runs Anywhere

- Akka's cloud
- Your hyperscaler VPC (AWS, Azure, GCP)
- Your own Kubernetes infrastructure
- On-premises

No proprietary APIs. No vendor-specific identity requirements. No data gravity traps.

**Talk track:** *"Azure locks you in at the identity, orchestration, compute, data, and governance layers. Moving off Azure means rewriting your agent orchestration, rebuilding your data indexes, and re-implementing your governance stack. Akka deploys on any cloud, on-prem, or our cloud — same platform, same APIs, same guarantees everywhere."*

---

## 4. Sovereign Cloud: Full Parity, Not Feature-Lagged

### Azure Sovereign Cloud Limitations

- Azure Government, Azure China (21Vianet), and EU Data Boundary all **lag 3-6 months** behind commercial Azure in feature availability
- AI Foundry availability in sovereign regions is limited
- **Control plane metadata may still flow outside the region** — the EU Data Boundary is a data residency commitment, not full isolation
- Model availability and PTU capacity are restricted in sovereign regions

### Akka Sovereign Cloud

- Country-isolated configuration — **all traffic and data stays in-region**
- Data isolation, networking isolation, and a private federation plane
- Local SREs in each sovereign region
- Supported regions: China, EU, Singapore, UK, Japan, Australia, and more
- **Full feature parity** — no lagged capabilities, no restricted model access

**Talk track:** *"Azure's sovereign clouds are feature-lagged versions of commercial Azure with restricted AI service availability — and control plane metadata may still leave the region. Akka's sovereign cloud is a fully isolated deployment with local SREs, full feature parity, and a private federation plane. All traffic and data stays in-region, period."*

---

## 5. EU AI Act Governance: Embedded vs. Bolt-On

### Why This Matters: The Penalties Are Severe

| Violation | Maximum Fine |
|-----------|-------------|
| Prohibited AI practices (Article 5) | **EUR 35 million or 7% of global annual turnover** |
| High-risk AI obligations (Articles 9-15) | **EUR 15 million or 3% of global annual turnover** |
| Supplying incorrect information to authorities | **EUR 7.5 million or 1.5% of global annual turnover** |

Enforcement is active now — prohibited practice penalties have been enforceable since February 2025; high-risk obligations since August 2025.

### Azure's Governance Is Fragmented and Insufficient

Azure's governance is spread across **5+ separate services** at different architectural layers:

| Requirement | Azure Approach | Gap |
|-------------|---------------|-----|
| Real-time policy enforcement | Content Safety (separate API call, 100-300ms latency) + API Management gateway policies | **Fragmented** — multiple enforcement points, no unified policy engine |
| Decision explainability | Responsible AI Dashboard, evaluation suite | **Post-hoc only** — no real-time "why did the AI make this decision" |
| Immutable interaction logging | Standard Azure Monitor / Purview audit logs | **Not inherently immutable** — standard audit logs, not a purpose-built ledger |
| Human intervention (pause/override) | No built-in capability | **Does not exist** — no "pause this agent" dashboard or real-time human override |
| Authorization capture | Entra sign-in logs + RBAC logs + API Management logs | **No consolidated snapshot** — must correlate 3+ log sources to reconstruct |
| PII scrubbing + explainability | PII detection exists; no scrub-with-explain pipeline | **Unsolved** — GDPR/AI Act tension left to customer |
| Pre-deployment classification | No AI system classification against regulatory frameworks | **Does not exist** — no obligation derivation, no framework mapping |
| Sign-off workflows | No multi-persona attestation capability | **Does not exist** — no change governance engine |
| Governance Posture Package | No sealed audit artifact for regulatory handoff | **Does not exist** — compliance documentation assembled manually |

### Why Bolt-On Governance Fails the EU AI Act

Microsoft has made **no article-by-article compliance mapping** for Azure AI Foundry. Their compliance story relies on Purview Compliance Manager templates (self-assessment checklists), not built-in technical controls.

Five critical failures of bolt-on governance:

1. **Immutable records**: A log message from a third-party runtime is a claim — there is no way to prove it wasn't modified, delayed, or selectively omitted. Only a system inline to the runtime can witness and encode every interaction immutably.

2. **Human intervention**: The EU AI Act requires humans can pause, discontinue, override, review, or nudge an ongoing agentic process. Azure has no built-in capability for this. A governance layer that only reads logs cannot stop or redirect a running process.

3. **Authorization capture**: The EU AI Act requires recording which authorizations and tools were in use at the time of every interaction. Azure requires correlating 3+ separate log sources to reconstruct this — and their AI Gateway documentation explicitly states it does not log tool traces.

4. **PII scrubbing with Right to Explain**: PII must be scrubbed, but decisions must still be explainable. Azure has no solution for this tension. Only the agentic runtime itself can make the decision, enforce scrubbing, and produce the explanation in a single atomic operation.

5. **Pre-deployment classification and attestation**: Azure has no answer for the governance that must happen before an AI system ships. There is no capability to classify systems against regulatory frameworks, route change approvals to the right personas with the right evidence, or produce a sealed audit artifact that proves the system was reviewed appropriately before deployment. Akka's governance platform covers this entire lifecycle — from obligation derivation through multi-persona attestation to a signed deployment bundle — as a first-class product surface.

### Akka's Embedded Governance

Akka's policy enforcement engine is **embedded directly in the runtime** — not a bolt-on, not a gateway interceptor, not a log reader:

- **Real-time policy enforcement**: Guardrails, policies, LLMs-as-a-judge, and sanitizers execute inline within the runtime
- **Self-explanation**: Every deployment produces decision explanations as a property of the runtime
- **Self-containment**: Failures are contained as they happen, not detected after the fact
- **Human intervention**: Humans can pause, discontinue, override, review, or nudge an ongoing agentic process
- **Immutable interaction logging**: The runtime witnesses and records every interaction
- **PII scrubbing with explainability**: The runtime makes the decision, scrubs PII, and produces the explanation atomically
- **Pre-deployment classification**: Classify AI systems against 175 regulatory frameworks and 600 controls to derive the exact obligation set before a single line of production code ships
- **Multi-persona sign-off workflows**: Declarative recipe engine routes change events to the right reviewers with dossiers, carry-forward rules, and quorum logic — not email chains and spreadsheets
- **Governance Posture Package**: Every deployment produces a tamper-evident audit artifact containing the full record of every classification decision, sign-off, and approval — ready for regulatory handoff without scrambling
- **19+ compliance certifications** including EU AI Act, ISO 42001, SOC 2

**Talk track:** *"Microsoft's governance is spread across five separate services — Content Safety, API Management, Purview, Monitor, and Entra — none of which talk to each other as a unified system. They have no real-time explainability, no human override capability, no immutable interaction ledger, and no solution for PII scrubbing with explainability. And before a system even ships, Azure has no way to classify it against applicable regulations, get the right people to sign off, or produce a sealed audit record. The EU AI Act requires all of these — and the fines are up to 7% of global revenue. Akka covers governance before deployment and in production: every classification decision recorded, every sign-off captured, every runtime interaction witnessed and explainable. It's the difference between governance that works and a compliance checkbox that won't survive an audit."*

---

## Objection Handling

### "But we're already on Azure"

*"Akka deploys inside your Azure VPC. You keep your Azure infrastructure, your Entra ID, your networking — Akka runs alongside it. You're not replacing Azure, you're adding the reliability, HA/DR, and governance layer that Azure AI Foundry doesn't have."*

### "Microsoft will catch up"

*"Microsoft's own documentation says their Agent Service has no SLA and no built-in DR — and their roadmap shows no HA/DR improvements. Even if they start building today, we've heard from multiple accounts that they've told customers this is 2-3 years out. The EU AI Act is enforceable now. Can you wait 2-3 years for governance that meets the requirements?"*

### "Azure has Content Safety built in"

*"Content Safety filters harmful content — that's one dimension of governance. The EU AI Act requires decision explainability, human intervention, immutable audit trails, authorization capture, and PII handling with explainability. Azure has no solution for any of those. Content filtering is table stakes, not compliance."*

### "We trust Microsoft on compliance"

*"Microsoft signed the EU AI Pact and published a Responsible AI Transparency Report — but they have not published an article-by-article mapping of which Azure features satisfy which EU AI Act requirements. Their compliance tooling is Purview Compliance Manager templates — self-assessment checklists you fill out yourself. Akka holds 19+ compliance certifications and embeds governance in the runtime so compliance is a property of every deployment, not a checklist exercise."*

### "Azure is cheaper because we have an EA"

*"Enterprise Agreements give you discounts on individual Azure services, but you're still paying for 6-8 separate services that compound. Akka's shared compute model means orchestration, agents, memory, streaming, APIs, and governance all run on one platform. Even with EA discounts, customers see 70-90% infrastructure cost reduction because the architecture is fundamentally different — shared compute vs. service-per-function."*

---

## Key Sources (Microsoft's Own Documentation)

Use these to substantiate claims in customer conversations:

- [Agent Service has no SLA](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/high-availability-resiliency) — "Agent Service has no availability or state durability Service Level Agreement"
- [No automatic failover](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/high-availability-resiliency) — "Foundry itself doesn't provide automatic failover or disaster recovery"
- [No built-in DR](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/agent-service-disaster-recovery?view=foundry-classic) — "Agent Service doesn't provide built-in disaster recovery capabilities"
- [No active-active](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/agent-service-disaster-recovery?view=foundry-classic) — "No supported method for active-active, multi-region replication"
- [Total state loss possible](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-platform-disaster-recovery) — "Recovery point for stateful content can be total loss"
- [AI Gateway does not log tool traces](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/governance) — Explicitly stated in MCP governance docs
- [Azure OpenAI SLA is 99.9% only](https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services?lang=1) — Availability only, no RTO/RPO
- [No article-by-article EU AI Act mapping](https://www.microsoft.com/en-us/trust-center/compliance/eu-ai-act) — General commitments, Purview templates for self-assessment
- [Sweden Central 7-hour outage](https://www.theregister.com/2026/01/28/azure_openai_service_sweden/) — EU customers had no failover
- [GPT-5.2 20-hour multi-region outage](https://azure.status.microsoft/en-us/status/history/) — 7 regions simultaneously

---

*Prepared for NTT Data Enterprise Agentic Grid sales teams. All Azure claims substantiated with Microsoft's own documentation.*
