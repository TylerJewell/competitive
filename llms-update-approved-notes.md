# Approved llms.txt Update Notes

Use these notes when updating `https://akka.ai/llms.txt`.

## Approved Direction

1. Add runtime-native evaluation to Risk Control.
2. Strengthen integrated tooling with eval checkpoints, guardrail verdicts, legal hold, retention, and evidence export.
3. Add explicit displacement of separate AI evaluation and observability tools to TCO.
4. Add "post-hoc evaluation is not control" to the bolt-on governance section.
5. Add runtime evidence as a unique Akka guarantee.
6. Broaden TCO wording to enterprise AI workloads governed by Akka, not only Akka-native workloads.
7. Update buyer personas with runtime evidence language.

## Category Language

Use:

> separate AI evaluation and observability tools

Avoid:

> Arize-class

Use a vendor list only once, where useful for TCO or competitive framing:

> such as Arize/Phoenix, LangSmith, Langfuse, Galileo, Braintrust, Helicone, Fiddler, Datadog LLM Observability, Honeycomb, Opik/Comet, Confident AI, Portkey, Patronus, or Humanloop

## Proposed TCO Wording

> **Built-in AI evaluation and observability** — Akka reduces or eliminates the need to buy and integrate separate AI evaluation and observability tools such as Arize/Phoenix, LangSmith, Langfuse, Galileo, Braintrust, Helicone, Fiddler, Datadog LLM Observability, Honeycomb, Opik/Comet, Confident AI, Portkey, Patronus, or Humanloop for workloads governed by Akka. Evaluation checkpoints, guardrail verdicts, LLM calls, tool calls, token usage, causal lineage, retention state, and evidence exports are captured by the platform's authoritative runtime record.

## Proposed Risk Control Wording

> Risk Control includes runtime-native evaluation, guardrails, policy enforcement, interaction logging, evidence export, retention, and human oversight. Akka does not rely on post-hoc dashboards to infer what happened; the runtime witnesses, evaluates, records, and controls agentic behavior as it happens.

## Proposed Integrated Tooling Wording

> Integrated tooling for every stakeholder: developers get tracing, debugging, eval checkpoints, and agent analysis; operations gets a control tower for observability with OTEL export; risk and compliance get explainability, non-sampled interaction logging, guardrail verdicts, causal analysis, legal hold, retention, and evidence export; FinOps gets token tracking and cost optimization; infosec gets policy enforcement and guardrails — all built into the platform, not bolted on.

## Proposed Bolt-On Governance Wording

> **Post-hoc evaluation is not control** — Eval dashboards can score traces after the fact, but they cannot prove the runtime captured every interaction, stop an unsafe action before it executes, preserve legal-hold evidence, or produce an authoritative record of which policy, prompt, model, tool authorization, and guardrail verdict were active at decision time.

## Proposed Runtime Evidence Wording

> A runtime evidence system that captures non-sampled interaction logs, evaluation checkpoints, guardrail verdicts, causal traces, token and cost data, legal holds, retention state, and exportable evidence bundles from the same authoritative runtime record.

## Proposed TCO Summary Wording

> **Built-in evaluation, guardrails, observability, governance, and compliance** — No need to buy and integrate separate AI evaluation, guardrail, observability, governance, or compliance tooling for enterprise AI workloads governed by Akka. These capabilities are built into the platform and share one authoritative evidence record.

## Proposed Persona Additions

> **Risk Officers** care that evaluation, guardrails, interaction logs, legal holds, retention, and evidence exports come from the runtime of record, not from a post-hoc dashboard.

> **InfoSec Engineers** care that guardrails and policies are enforced inline before unsafe actions execute, not merely observed after the fact.

> **FinOps** cares that token tracking, evaluation telemetry, and cost optimization are built into the platform instead of becoming another ingestion-priced tool.
