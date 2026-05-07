# Sales & Partner Battlecard: Akka Service Tiers & TCO Positioning

**For:** Akka global sales teams and reseller partners
**Use:** Internal enablement for positioning the right Akka service tier and driving TCO conversations with enterprise prospects
**Last updated:** 2026-04-15

---

## TL;DR — The Five Tiers at a Glance

| Tier | Where It Runs | QoS | Best For | TCO Headline |
|------|---------------|-----|----------|--------------|
| **Starter** | Akka's public cloud | Fully resilient, 24/7 SRE | Customers who want a running production workload without the BYOC commitment | Monthly billing, no POs, no invoices — spend scales with usage |
| **Sandbox** | Customer's own VPC | Non-resilient, 9x5 support, no SLA | Customers who want to build and evaluate in their own environment before committing | Lowest possible cloud footprint — ~5 platform cores vs 20–25 for production tiers |
| **Day 2 Ops** | Customer's own VPC | Fully resilient, 24/7 SRE | Customers running real workloads that don't yet need cross-region failover | Consolidates orchestration, memory, streaming, evals, guardrails, logging, and governance onto shared compute — up to 90% infrastructure reduction plus avoided eval-tool spend |
| **Business Continuity** | Customer's own VPC | Fully resilient + active-active HA/DR | Workloads that cannot tolerate a regional outage | Managed HA/DR with sub-1 min RTO and zero-byte RPO — no customer-built failover infrastructure |
| **Sovereign Cloud** | Customer's own VPC, country-isolated | Fully resilient + HA/DR + local SREs | Regulated industries, data residency mandates, sovereign requirements | Full feature parity with commercial tiers — no lagged capabilities or restricted model access |

---

## 1. The Two Starting Paths

Every deal starts by answering one question: **does the customer want Akka-hosted or their-cloud-hosted?** The answer routes them to one of two on-ramps.

### Path A: Starter (Akka's Cloud)

A fully resilient Akka region installed in Akka's public cloud, with a private data link back to the customer's environment. Monthly billing in arrears. No POs, no invoices, no procurement cycle. The customer never installs anything.

**Who it's for:**
- Customers with a real workload but no appetite for a BYOC commitment yet
- Customers who haven't built cloud infrastructure maturity in-house
- Fast-moving lines of business that need to ship something without waiting on central IT
- Proofs-of-value where the success criterion is "did the workload run?"

**TCO talk track:** *"You're not buying infrastructure — you're buying a running Akka region, billed monthly for what you actually use. No invoicing cycle, no capex, no cloud architecture review before you start. When you're ready to bring it in-house, you can migrate to Day 2 Ops, but until then the cost of standing still is zero."*

### Path B: Sandbox (Customer's VPC)

A single Akka region installed in the customer's own cloud, deliberately configured for low overhead. No HA/DR. 9x5 support. Not SLA-backed. Designed as a low-friction on-ramp for customers who want to evaluate Akka in their own environment without committing to a production footprint.

**Who it's for:**
- Engineering teams who want Akka in their cloud before committing to a production tier
- Enterprises whose procurement process requires a successful in-house pilot before larger contracts
- Customers who need to see Akka running alongside their existing cloud services
- Architecture teams doing fit-for-purpose evaluation

**The critical talk point — migration is a rebuild, not an upgrade.** Sandbox is intentionally cheap because it strips the resilience infrastructure. Moving to a higher tier is a rebuild from scratch. The word "Sandbox" does this positioning work for you — it signals "throwaway, experimental, not the destination." Set this expectation at sign-up, not at upgrade time.

**TCO talk track:** *"Sandbox is the lowest possible way to run Akka in your own cloud — roughly a quarter of the platform-core footprint of a production-grade region. You're paying for evaluation, not for production. When you outgrow it, you'll rebuild on Day 2 Ops or Business Continuity with a tier that's engineered for the workload you've actually proven out."*

---

## 2. Quality of Service: The Sandbox vs Production Distinction

**This is the most important conversation to have on every deal.** Customers who misunderstand it buy Sandbox for production workloads and then blame Akka when something fails.

| Dimension | Sandbox | Day 2 Ops, BC, Sovereign |
|-----------|---------|--------------------------|
| HA/DR | None | Day 2 Ops: none. BC + Sovereign: active-active |
| Rolling updates | None — platform downtime during updates | No-downtime rolling updates |
| SRE coverage | 9x5 monitoring | 24/7 SRE monitoring and management |
| SLA | Not SLA-backed | Contractual 99.9999% availability, backed by indemnities |
| CVE patching | Requires downtime | Live CVE patching, no downtime |
| Platform core footprint | ~5 platform cores | ~20–25 per region (varies by tier) |
| Intended workloads | Evaluation, learning, early development | Production, customer-facing systems, anything that matters |
| Upgrade path | Rebuild on a higher tier | In-place progression to higher tiers |

**Talk track for positioning:** *"Sandbox and our production tiers are not versions of the same thing at different price points. They're different quality-of-service tiers built on different infrastructure configurations. Sandbox strips out the resilience layer so you can start building with minimal overhead. Our production tiers — Day 2 Ops and above — include fully resilient infrastructure, 24/7 SRE, and no-downtime operations because that's what running something real demands. The question isn't which one is 'better' — it's which one matches what you're trying to do right now."*

---

## 3. Platform Cores vs Service Cores: The TCO Transparency Argument

**If you teach one thing on this battlecard, teach this.** The platform-core / service-core distinction is the single most important TCO transparency story Akka has. It's also the one that, if mishandled, creates sticker shock at contract time.

### The Two Core Types

| Core Type | What It Runs | Who Pays |
|-----------|--------------|----------|
| **Platform cores** | Akka's own runtime, clustering, resilience layer, data sharding, traffic steering, zero-trust networking | Customer, as part of their own cloud infrastructure bill — Akka does NOT charge a license fee for platform cores |
| **Service cores** | The customer's agentic workloads — their agents, workflows, endpoints, entities, views | Customer, as part of their Akka license — Akka charges per service core |

### Why This Matters

**Resilience isn't free.** A fully resilient Akka region in the customer's VPC needs platform cores to run clustering, active-active replication, zero-trust networking, and the resilience layer that delivers Akka's 99.9999% availability guarantee. Those platform cores run on cloud infrastructure the customer provisions — they're part of the customer's cloud bill, not the Akka license.

**Sandbox is cheap because it has fewer platform cores.** That's literally the engineering tradeoff: strip the resilience infrastructure, drop the platform core count, cut the customer's cloud footprint by roughly 4-5x. The customer's total cost drops not because the license is cheaper, but because their cloud infrastructure bill drops.

**The TCO argument this unlocks:** Akka is the only agentic platform that separates and discloses this. Every other platform hides infrastructure overhead inside a single opaque price, or forces customers to stand up separate services (vector DB, memory layer, streaming, evaluation, guardrails, logging, governance) each with their own infrastructure bill. Akka discloses platform-core overhead up front, charges license fees only for service cores, and runs orchestration + memory + streaming + evaluation + guardrails + logging + governance + APIs on shared compute.

### Discovery Questions to Expose the TCO Gap

Ask these on any deal where the customer is comparing Akka against Azure AI Foundry, LangChain, Temporal, or a DIY stack:

1. *"How many separately billed services are you stitching together today, and what's the combined monthly spend on them?"* → Exposes Azure's 6-9 service sprawl
2. *"What are you paying for agent memory today, and what's the read/write latency?"* → Exposes the ~200ms bolt-on memory penalty
3. *"What's your cloud spend on observability and tracing for your AI workloads?"* → Exposes App Insights / Datadog cost balloon
4. *"Are you budgeting for Arize, LangSmith, Phoenix, or another eval/observability product?"* → Exposes duplicated evaluation, trace storage, and audit-reconciliation cost
5. *"When a regulator or customer asks why an agent made a decision, which system is the evidence of record?"* → Exposes the gap between post-hoc dashboards and runtime-native interaction logs
6. *"When you need to patch a CVE in your runtime, how much downtime does that cost you?"* → Exposes the lack of live CVE patching
7. *"Have you priced out what it would cost to build active-active HA/DR yourself?"* → Exposes the hidden cost of DIY failover

**Talk track:** *"Most platforms give you one opaque price and you discover the real cloud bill after you've signed. Akka discloses two things separately: the license for your service cores, and the platform core overhead you'll provision in your own VPC. You see the full picture before you commit. And because evaluation checkpoints, guardrail verdicts, interaction logging, legal hold, retention, and evidence export are built into the runtime, you don't need to buy an Arize-class product just to create an after-the-fact evidence plane."*

---

## 4. Matching the Customer to the Right Tier

A five-step decision tree for discovery calls:

**Step 1. Where do they want Akka to run?**
- Akka's public cloud → **Starter**
- Their own VPC → continue to Step 2

**Step 2. Are they running something real, or exploring?**
- Exploring, learning, proving fit → **Sandbox**
- Running something real → continue to Step 3

**Step 3. Can their workload tolerate a regional outage?**
- Yes → **Day 2 Ops**
- No → continue to Step 4

**Step 4. Do they need country-level data isolation for regulatory or sovereign reasons?**
- No → **Business Continuity**
- Yes → **Sovereign Cloud**

**Step 5. Confirm the upgrade path before closing.**
- If they landed on Sandbox, set the rebuild expectation before signature
- If they landed on Day 2 Ops, frame the progression to BC as a business-continuity conversation they should have within 12 months
- If they landed on BC or Sovereign, position TAM/FDE as the lever that shortens their time-to-production

---

## 5. TCO Arguments by Tier

### Starter

**Primary argument: time-to-value and procurement friction.** Customers choose Starter when the cost of *not starting* is higher than the per-month run rate. There is no procurement cycle, no PO, no architecture review, no cloud infrastructure project — they're buying a running workload.

**TCO angle:** Avoided costs dominate. No capex, no cloud architecture project, no multi-month deployment timeline. The business case is "we're shipping in days instead of quarters."

### Sandbox

**Primary argument: lowest-friction evaluation in the customer's own environment.** Sandbox exists to make the cost of *trying Akka in your own cloud* smaller than the cost of *not trying.* Customers who evaluate Akka in their own VPC before committing to production convert at much higher rates than customers who evaluate from documentation alone.

**TCO angle:** Opportunity cost reduction. The customer gets hands-on with Akka running alongside their existing cloud services, reduces architecture uncertainty, and builds internal conviction before a larger commitment. Compare this to the cost of a failed production rollout after a doc-based decision.

### Day 2 Ops

**Primary argument: shared compute + live CVE patching + rolling updates + runtime evidence.** This is where the core Akka TCO story lands. Customers running real workloads on Day 2 Ops replace 6-9 separately billed services (orchestration + memory + streaming + APIs + evaluation + guardrails + logging + governance + observability) with a single platform running on shared compute.

**TCO angle:** Up to 90% infrastructure cost reduction vs a stitched stack on Azure AI Foundry, LangChain, or Temporal. No maintenance windows, no downtime during patching, no lost revenue during deployments, and no required Arize-class eval/observability purchase for Akka workloads.

### Business Continuity

**Primary argument: managed HA/DR with contractual guarantees.** Customers on BC are avoiding the cost of building and operating their own failover infrastructure — which for most enterprises is a multi-million-dollar, multi-year project that is never actually complete.

**TCO angle:** Avoided cost of DIY failover. Compare BC's fully managed active-active HA/DR (sub-1 min RTO, zero-byte RPO, backed by indemnities) against the headcount, infrastructure, and operational complexity of building it in-house — or worse, running on a platform like Azure AI Foundry where Microsoft's own documentation states that total state loss is a planned-for scenario.

### Sovereign Cloud

**Primary argument: full feature parity in a country-isolated configuration.** Competing sovereign offerings (Azure Government, Azure China, EU Data Boundary) lag commercial offerings by 3-6 months and restrict AI service availability. Akka's Sovereign Cloud delivers full feature parity with no lagged capabilities, no restricted model access, and a private federation plane with local SREs.

**TCO angle:** Avoided compliance remediation cost. Inherit Akka's 19+ compliance certifications (EU AI Act, ISO 42001, SOC 2, Singapore Agent Framework, and more) rather than building your own compliance posture from scratch. Runtime-native interaction logs, evaluation checkpoints, guardrail verdicts, legal hold, retention, and evidence export make Akka the evidence of record. Every EU AI Act violation is up to 7% of global annual turnover — the cost of getting governance wrong dwarfs the cost of getting it right.

---

## 6. Objection Handling

### "Sandbox looks cheap — can we just run production on it?"

*"Sandbox is deliberately stripped of the resilience layer. There's no HA/DR, no 24/7 SRE, no SLA, and platform updates require downtime. If your workload has any production characteristics — customers depending on it, data that matters, revenue tied to uptime — you need Day 2 Ops at minimum. Sandbox is there to let you evaluate Akka in your own cloud at the lowest possible cost. It is not a production tier, and moving off it is a rebuild."*

### "Why is there no in-place upgrade from Sandbox?"

*"Sandbox is cheap because it runs on a fundamentally different infrastructure configuration — fewer platform cores, no resilience layer, no HA/DR primitives. Upgrading in place would mean retrofitting all of that onto a running environment, which would either force the same cloud footprint as our production tiers (defeating the purpose of Sandbox) or create an unreliable upgrade path customers can't trust. The rebuild is a feature, not a limitation. You build in Sandbox, prove out your design, then stand up the production tier you actually need."*

### "Why are you charging me for platform cores on top of the license?"

*"We're not — platform cores are part of your own cloud infrastructure bill, not an Akka license fee. We charge you for the service cores your workloads run on. Platform cores are what we disclose up front so you see the full picture before you commit. Most platforms hide this inside an opaque price. We break it out so you know exactly what Akka costs vs what your cloud footprint costs."*

### "Azure AI Foundry has everything included in one bill — isn't that simpler?"

*"Azure AI Foundry is 6-9 separately billed services underneath a single brand — Azure OpenAI, Cosmos DB, AI Search, Event Hubs, API Management, App Insights, Content Safety, Private Endpoints, and often a separate eval/observability product. Each has its own pricing model, its own scaling dynamics, and its own cost traps. You see the full bill at the end of the month after consumption has already happened. Akka runs orchestration, agents, memory, streaming, APIs, evaluation checkpoints, guardrails, interaction logging, and governance on one platform with shared compute — and we disclose platform-core overhead before you commit. Simpler isn't one bill, simpler is one platform."*

### "We already use Arize for evals and AI observability"

*"Keep Arize for legacy workloads if it is already embedded, but don't budget it as required for Akka. Akka's runtime captures non-sampled interaction logs, evaluation checkpoints, guardrail verdicts, LLM calls, tool calls, token cost, authority snapshots, causal lineage, legal holds, retention, and evidence exports. The question is whether the customer wants to pay for a second evidence plane and then reconcile it with the runtime of record."*

### "Can we start with Starter and migrate to Day 2 Ops later?"

*"Yes — Starter is designed as an on-ramp. When you're ready to bring Akka into your own cloud, we can help you migrate to Day 2 Ops with continuity of your workload. The common pattern is: prove the business case on Starter for one or two quarters, then bring it in-house when your architecture, security, and procurement teams have signed off."*

### "We're not sure we need 24/7 SRE on day one"

*"Every tier above Sandbox includes 24/7 SRE because production-grade infrastructure without 24/7 coverage is a contradiction. If a customer-facing workload goes down at 2am, you need someone watching. If you genuinely don't need 24/7 coverage, you're telling us the workload isn't production — which means Sandbox is the right fit, and the price reflects that."*

### "Why is TAM/FDE included in higher tiers but not lower ones?"

*"TAM/FDE is time with an Akka expert who helps you succeed — architecture reviews, operational readiness, upgrade planning, incident postmortems. At the Starter and Sandbox level, customers are typically proving fit and don't need dedicated personnel — our self-service documentation and support channels are sufficient. At Day 2 Ops and above, customers are running production workloads and the cost of TAM/FDE time pays back many times over in avoided incidents and faster time-to-value."*

### "Can a partner resell Starter?"

*"Starter is designed for low-friction direct billing and is typically sold direct. Partners who want to package Akka for their customers typically start with Day 2 Ops or above, where the TAM/FDE allocation gives both the partner and the end customer an Akka expert inside the engagement. Talk to your Akka partner manager about the right motion for your customer base."*

---

## 7. What NOT to Say

**Avoid these framings — they create confusion or undermine the positioning:**

- ❌ *"Sandbox is a cheap version of production"* — It's a different QoS tier, not a discounted production tier. Use "low-overhead evaluation environment" instead.
- ❌ *"You can upgrade from Sandbox in place"* — It's a rebuild. Say so up front.
- ❌ *"Platform cores are something Akka charges for"* — They're customer-provisioned infrastructure, not a license line item. Frame platform core disclosure as a transparency feature.
- ❌ *"Starter is a trial"* — It's a production tier, just hosted in Akka's cloud. Customers run real workloads on it.
- ❌ *"Day 2 Ops is the entry point to production"* — It's *an* entry point. Starter is also a production tier, just a different path.
- ❌ *"Sovereign is only for China / EU"* — It's for any regulated or sovereign requirement. Australia, Singapore, UK, Japan, Canada all have customers on Sovereign.

---

## 8. Partner Enablement Notes

**For Akka resellers and integration partners:**

- **Starter is typically sold direct.** Its monthly billing model and low-friction procurement don't fit most partner resale motions. Partners can still influence Starter deals through technical selection and architecture advice.
- **Sandbox is an evaluation on-ramp, not a revenue motion.** Partners should use Sandbox to let customers build confidence in Akka inside their own environment before a larger engagement. Don't expect Sandbox to generate partner margin — expect it to shorten sales cycles for the production tiers.
- **Day 2 Ops, BC, and Sovereign are the partner sweet spot.** These tiers include TAM/FDE allocations that pair well with partner services — the partner and Akka both have skin in the customer's success.
- **TAM/FDE coordination is critical.** When a partner is already embedded in a customer account, coordinate the TAM/FDE allocation with the partner's own delivery team to avoid duplication. Talk to your Akka partner manager before the deal closes to agree on roles.
- **EU AI Act readiness is a partner-led conversation in regulated industries.** Partners with compliance-led sales motions should lead with the governance story (see the Azure AI Foundry battlecard for detailed article-by-article positioning).
- **Evaluation-tool displacement is a TCO wedge.** When an account is already budgeting for Arize, LangSmith, Phoenix, Datadog AI observability, or a custom eval stack, quantify the avoided license, ingestion, storage, and integration work. Akka should be positioned as the runtime of record, not another dashboard next to the runtime.

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **Akka region** | A deployment unit of Akka — a single installation running on either Akka's cloud (Starter) or the customer's VPC (all other tiers) |
| **Platform core** | Cloud CPU capacity that runs Akka's own infrastructure — clustering, resilience, networking, sharding. Customer-provisioned, not license-billed |
| **Service core** | Cloud CPU capacity that runs the customer's agentic workloads. License-billed by Akka |
| **TAM/FDE** | Technical Account Manager / Field Delivery Engineer — dedicated Akka personnel included at the Day 2 Ops tier and above |
| **QoS (Quality of Service)** | The SLA, support tier, and resilience posture of a service tier. Sandbox is a distinct QoS from the production tiers |
| **HA/DR** | High Availability / Disaster Recovery. Only Business Continuity and Sovereign Cloud include active-active HA/DR |
| **RTO / RPO** | Recovery Time Objective / Recovery Point Objective. Akka's BC and Sovereign tiers deliver sub-1 minute RTO and zero-byte RPO |
| **In-place upgrade** | Moving from one tier to the next without rebuilding. Available between Day 2 Ops, BC, and Sovereign. **Not** available from Sandbox |

---

## 10. Where to Go for More

- **For competitive positioning against Azure AI Foundry:** See `battlecard-azure-ai-foundry.md`
- **For detailed TCO modeling:** See `akka-tco-analysis.md`
- **For partner-led engagement motions:** See `partner-enablement-brief.html`
- **For customer-facing product overview:** See `llms.txt` at `akka.ai/llms.txt`
- **For pricing guidance:** Contact your Akka field CTO or partner manager — pricing is not included in this document and should be discussed within the Akka sales channel

---

*Prepared for Akka global sales teams and reseller partners. Internal enablement document — do not share externally without review. No pricing information is included in this battlecard by design; discuss pricing through your Akka field CTO or partner manager.*
