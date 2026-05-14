# PNC Bank RFP — Strategic Answer Rewrites

**Context:** PNC GenAI Ops Suite observability tool RFP. The existing draft answers are fine for boilerplate compliance questions. Below are the 6 questions where the current answers either undersell Akka's differentiated capabilities or miss a clear competitive opening. Rewrite these before submission.

---

## 9.6.4 — Recovery Time Objective (RTO)

**Current answer (problem):** Says "6 hours or fewer" — which reads as a mediocre vendor BCP commitment and buries what is actually a world-class platform capability.

**Issue:** The question asks about RTO for the product/service. The existing answer conflates Akka's *internal vendor BCP* (how long before Akka's own operations recover from a catastrophic internal incident) with the *platform's delivered RTO to PNC* (how long before PNC's deployed applications recover from an infrastructure failure). These are two different things and the latter is Akka's strongest differentiator.

**Recommended answer:**

> Akka delivers two distinct and contractually backed recovery commitments that are relevant to PNC:
>
> **Platform RTO — what Akka delivers to PNC's deployed applications:**
> Sub-1 minute Recovery Time Objective with a zero-byte Recovery Point Objective. Akka's platform runs in active-active configuration across multiple availability zones and regions. Failover is automatic and transparent — no data is lost and no manual intervention is required. This is a contractual commitment backed by indemnities, not a best-effort target. PNC's agentic AI applications built on Akka inherit this guarantee.
>
> **Vendor BCP RTO — Akka's own internal recovery posture:**
> In the event of a significant internal disruption to Akka's operations (loss of key personnel, data center catastrophe, etc.), Akka's Business Continuity Plan targets recovery of client-supporting services within 6 hours or fewer.
>
> The platform-level RTO — sub-1 minute, zero byte RPO — is the commitment most relevant to PNC's operational risk evaluation. Specific SLA terms and indemnity structure are available in our SLA documentation at https://trust.akka.io.

---

## 9.7.2 — Strategic Direction of Products/Services

**Current answer (problem):** Generic and defensive — mentions "expanding capabilities" and "deeper integration with enterprise observability tooling" without articulating what makes Akka's roadmap compelling or unique for a regulated financial institution.

**Recommended answer:**

> Akka's strategic direction is to be the only agentic AI platform that makes governance and reliability non-negotiable properties of every AI deployment — not optional add-ons that compliance teams chase after the fact.
>
> **Short-term (next 12 months):** We are delivering the Akka Governance Platform as a first-class product surface — enabling financial institutions like PNC to classify AI systems against applicable regulatory frameworks (including DORA, SR 11-7, NIST AI RMF, and the EU AI Act), execute multi-persona attestation workflows through a declarative recipe engine, and seal the result as a tamper-evident Governance Posture Package before any AI system reaches production. This directly addresses the pre-deployment governance requirements that financial regulators are beginning to enforce.
>
> **Medium-term:** Deepening financial services-specific capabilities: expanded causal analysis for AI decision explainability in credit, underwriting, and fraud contexts; enhanced human-in-the-loop override and audit trail tooling aligned with Federal Reserve SR 11-7 model risk management guidance; and sovereign deployment options for US regulatory data residency requirements.
>
> **Long-term:** Akka's vision is a platform that makes the question "can we prove what our AI decided and why?" answerable in real time — for every interaction, every agent, every deployment — as a built-in property of the platform, not a post-hoc investigation. For PNC, this means AI systems that are auditable by design, not auditable by effort.
>
> Akka currently holds 19+ InfoSec certifications including SOC 2 Type II, ISO 27001, and certifications aligned with the EU AI Act and Singapore Agent Framework. DORA-aligned operational resilience capabilities are actively being strengthened with financial services customers in mind.

---

## 14.1.2 — Automated Provisioning / Auto-Scaling

**Current answer (problem):** Correctly says "yes, auto-scaling on all major clouds" but doesn't differentiate. Every cloud-native SaaS says the same thing. The answer misses the shared compute model and scale-to-zero — both of which have direct cost implications for PNC.

**Recommended answer:**

> Yes. Akka's platform supports fully automated, on-demand (24/7) resource provisioning and elastic scaling without any vendor intervention, available on all major cloud providers (GCP, AWS, Azure, and others) at PNC's discretion.
>
> Two capabilities distinguish Akka's approach from standard cloud autoscaling:
>
> **Scale-to-zero:** Akka's shared compute model scales active workloads to zero when idle, meaning PNC pays only for compute that is actively running. This is architecturally significant for agentic AI workloads, which are often bursty — high volume during business hours, near-zero overnight. Point-solution AI platforms (including Azure AI Foundry, Temporal, and LangChain) typically bill for reserved capacity regardless of utilization.
>
> **Shared compute model:** Orchestration, agents, memory, streaming, and APIs all run on shared compute — not separate provisioned services. This eliminates the need to size, scale, and manage multiple independent infrastructure components. Customers consistently report 70-90% reduction in infrastructure cost versus assembling equivalent capabilities from point solutions.
>
> For PNC's deployment, the specific cloud provider and geographic region are PNC's choice. Akka Automated Operations (AAO) is our enterprise offering that installs inside PNC's own VPC — providing full infrastructure isolation, PNC-controlled scaling automation, and active-active HA/DR across regions, all under PNC's cloud account and governance.

---

## 14.1.3 — Multi-Tenant vs. Single-Tenant / Customer Isolation

**Current answer (problem):** Mentions "logical isolation" for multi-tenant and "dedicated single-tenant deployments available" but doesn't develop the single-tenant option, which is almost certainly what a large bank will want.

**Recommended answer:**

> Akka offers two deployment models; the right choice depends on PNC's security and isolation requirements:
>
> **Multi-tenant (Akka-hosted):** PNC's environment runs on Akka's shared cloud platform. Customers are strongly isolated via dedicated namespaces, access controls, and data partitioning. Akka's SOC 2 Type II audit covers tenant isolation controls. This is the fastest path to production and the right model for teams in early adoption phases.
>
> **Single-tenant, PNC VPC (recommended for a financial institution of PNC's scale):** Akka Automated Operations (AAO) installs a private, dedicated Akka runtime inside PNC's own cloud account (AWS, GCP, Azure, or other). PNC owns and controls the cloud infrastructure; Akka manages the platform layer above it. This means:
> - All compute, storage, and network traffic stays within PNC's security boundary
> - No shared infrastructure with any other Akka customer
> - PNC retains full control over data residency — all data stays in US-based regions
> - PNC's existing cloud security controls (IAM, network policies, SIEM, DLP) apply directly to the Akka runtime
> - Active-active HA/DR across two or more PNC-controlled regions
>
> For a regulated financial institution subject to OCC third-party risk management guidance and DORA-aligned operational resilience requirements, the VPC-isolated deployment model eliminates the shared-infrastructure risk entirely while preserving all of Akka's platform capabilities and SLAs.

---

## 14.8.1 — Generative AI in Solution / LLMs in Use

**Current answer (problem):** This is the single most important question in the entire RFP for Akka's differentiated positioning — and the current answer is a bland list of LLM integrations. PNC is evaluating an AI observability/governance tool. This is where Akka should lead with everything that makes it unique.

**Recommended answer:**

> Yes. Akka is purpose-built as an enterprise agentic AI platform. Generative AI is not a feature of our product — it is the product's subject matter. Akka provides the runtime, orchestration, governance, and observability layer for enterprise AI agent deployments. This gives PNC a critical distinction: Akka is not an AI tool that added observability; it is an observability-and-governance platform built from the ground up around agentic AI systems.
>
> **LLM and SLM integrations:** Akka integrates natively with models from Anthropic (Claude 3.x/4.x), OpenAI (GPT-4o, o1/o3 series), Google (Gemini 1.5/2.0 series), Meta (Llama 3.x), Mistral, and others via the model-agnostic provider abstraction layer. PNC selects which model(s) are used; Akka imposes no model lock-in. Models can be swapped, versioned, or run in parallel within a single deployment.
>
> **What makes Akka's approach to AI governance unique for a financial institution:**
>
> *Inline governance — not bolt-on:* Akka's policy enforcement engine is embedded directly in the runtime. Guardrails, LLMs-as-judge evaluators, sanitizers, and policy checks execute inline with every AI interaction — before a response is returned, not in a separate audit pass afterward. This is the technical requirement for the EU AI Act's real-time enforcement provisions and is directly relevant to OCC and Federal Reserve model risk management expectations under SR 11-7.
>
> *Immutable interaction ledger:* Every agent interaction — input, output, tool calls, authorizations, model version, policy evaluation result — is recorded immutably by the Akka runtime at the moment of execution. This is not a log that can be modified after the fact; it is a cryptographically witnessed record. For PNC's AI risk management, model validation, and examiner-facing documentation, this means every AI decision is provable, not just summarized.
>
> *Human intervention capability:* Akka provides a built-in control dashboard that allows authorized humans to pause, override, redirect, or discontinue any running AI agent process in real time. This is a technical implementation of the human oversight requirements that regulators increasingly expect for high-risk AI applications in financial services.
>
> *Decision explainability:* Akka's self-explanation capability produces a human-readable account of why an AI system made a given decision — inline at the time of the decision, with PII scrubbed — meeting the Right to Explain requirements that financial services regulators are applying to automated decision-making under FCRA, ECOA, and emerging AI-specific guidance.
>
> *Pre-deployment governance:* Before any AI system reaches PNC's production environment, Akka's governance platform enables classification against applicable regulatory frameworks (SR 11-7, NIST AI RMF, DORA, and others), execution of multi-persona attestation workflows (risk officers, model validators, technology owners), and generation of a tamper-evident Governance Posture Package — a sealed audit artifact that documents every review and approval decision that preceded the deployment.
>
> **In short:** Akka gives PNC's model risk, technology risk, and audit teams a complete, provable record of what every AI system was authorized to do, what it actually did, and who approved it — before and after deployment. No other agentic AI platform provides this end-to-end governance lifecycle in a single system.

---

## 13.1.44 — Real-Time Fraud Surveillance for Financial Transactions

**Current answer (problem):** "Akka's platform does not directly process financial transactions" is technically accurate but reads as a capability gap. This question is an opportunity to explain how Akka's runtime monitoring and agent interaction logging are directly applicable to fraud detection at the AI layer.

**Recommended answer:**

> Akka's platform does not function as a financial transaction processing system — that layer sits in PNC's core banking infrastructure. However, Akka's runtime capabilities are directly applicable to AI-layer fraud surveillance, which is increasingly where the risk surface lives for GenAI deployments:
>
> **Real-time policy enforcement at the AI layer:** Akka's embedded policy engine evaluates every AI agent interaction against configurable guardrails and risk rules before a response is executed. For GenAI applications that touch financial decisions — loan recommendations, payment instructions, account inquiries — this means anomalous AI behaviors (out-of-scope requests, prompt injection attempts, unexpected tool calls) are detected and blocked inline, not flagged after the fact.
>
> **Agent interaction audit trail:** Every AI agent action — including tool calls, data lookups, authorizations exercised, and decisions made — is logged immutably in real time. For PNC's fraud and model risk teams, this provides a complete, tamper-evident record of AI behavior that can be queried forensically if suspicious activity is suspected.
>
> **Human intervention and containment:** Akka's control dashboard enables authorized personnel to pause or terminate any AI agent process in real time if anomalous behavior is identified — before a transaction is completed or a fraudulent instruction is acted upon.
>
> If PNC's deployment involves AI agents that interact with financial transaction workflows, Akka can configure specific monitoring rules, anomaly detection thresholds, and escalation paths tailored to PNC's fraud risk appetite. We recommend discussing this in detail during the technical evaluation phase.

---

## Summary: Questions to Leave Unchanged

All questions in Sections 8, 9.1–9.5, 9.8–9.9, 13.1 (infosec checkboxes), 14.3–14.7, and 15 (accessibility) have defensible answers that don't benefit from strategic reframing. The six questions above are where Akka's differentiation is material.

**Highest priority to fix before submission:**
1. **14.8.1** — This is the product pitch. The current answer is a missed opportunity.
2. **9.6.4** — The RTO answer undersells the platform's sub-1 minute guarantee and may confuse evaluators.
3. **9.7.2** — Strategic direction is where financial services evaluators look for DORA/SR 11-7 alignment signals.
