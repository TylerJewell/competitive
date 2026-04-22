# Social Proofing Agent

An AI-powered social proofing service built on Akka SDK. Generates contextual social proof messages for retail product pages (e.g., "47 people are viewing this right now", "Bought 12 times in the last hour") using an AI agent that selects the most effective strategy based on real-time signals.

The service tracks pre-aggregated view counts and order events, periodically triggers an AI agent to select the best social proof strategy (urgency, validation, scarcity, or trending), and serves pre-computed cached messages with no LLM on the read path.

## Quick Start

```bash
# Set your Gemini API key
export GOOGLE_AI_GEMINI_API_KEY=your-key-here

# Compile and run
mvn compile exec:java
```

Open http://localhost:9000/ to see the demo UI. Use the gear icon at the bottom to add products and send events.

Verify the API:

```bash
# Create a product
curl -X PUT http://localhost:9000/products/ps6-console \
  -H "Content-Type: application/json" \
  -d '{"name": "PlayStation 6", "category": "Electronics & Tech", "stockLevel": 3}'

# Send views
curl -X POST http://localhost:9000/ingestion/ps6-console/views \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'

# Get social proof (after aggregation period)
curl http://localhost:9000/social-proof/ps6-console
```

## Usage

### Product Endpoint

**PUT /products/{productId}** — Create or update product catalog info

```bash
curl -X PUT http://localhost:9000/products/ps6-console \
  -H "Content-Type: application/json" \
  -d '{"name": "PlayStation 6", "category": "Electronics & Tech", "stockLevel": 3}'
```

```json
{"productId": "ps6-console", "name": "PlayStation 6", "category": "Electronics & Tech", "stockLevel": 3}
```

### Ingestion Endpoint

**POST /ingestion/{productId}/views** — Record a batch of product views

```bash
curl -X POST http://localhost:9000/ingestion/ps6-console/views \
  -H "Content-Type: application/json" \
  -d '{"count": 47}'
```

```json
{"viewCount": 142}
```

**POST /ingestion/{productId}/orders** — Record a product order

```bash
curl -X POST http://localhost:9000/ingestion/ps6-console/orders \
  -H "Content-Type: application/json" \
  -d '{}'
```

```json
{"orderCount": 12}
```

### Social Proof Endpoint

**GET /social-proof/{productId}** — Get pre-computed social proof message

```bash
curl http://localhost:9000/social-proof/ps6-console
```

```json
{"productId": "ps6-console", "message": "Only 3 left — selling fast!", "strategy": "SCARCITY", "generatedAt": "2026-04-10T14:30:00Z"}
```

**GET /social-proof/products** — List all products with social proof

```bash
curl http://localhost:9000/social-proof/products
```

**GET /social-proof/stream** — SSE stream of social proof updates

```bash
curl http://localhost:9000/social-proof/stream
```

### Demo UI

Open http://localhost:9000/ in a browser. The main view shows a product grid with live social proof messages updated via SSE. Click the gear icon to access administration (add products, send events).

### Traffic Simulation (Gatling)

Generate realistic traffic across 4 demo products with varying profiles (hot, medium, cold). Designed to stay within Gemini 2.0 Flash free tier rate limits (15 RPM). Requires the service to be running.

```bash
# Start the service first, then in a separate terminal:
mvn gatling:test
```

The simulation runs three phases:
1. **Warm-up** — creates 4 products via PUT and sends an initial burst of views/orders
2. **Steady state** — continuous traffic at ~10 events/sec for 60 seconds
3. **Peak burst** — simulates a product launch (PS6 goes viral)

To target a deployed service instead of localhost:

```bash
mvn gatling:test -DbaseUrl=https://your-service.akka.app
```

### Load Testing (Throughput Validation)

Validates throughput requirements with individual view events (count=1) at high rates. Use the stub model provider to avoid LLM rate limits and costs:

```bash
# Start service with stub model (no LLM calls)
MODEL_PROVIDER=stub mvn compile exec:java

# Run load test (in separate terminal)
mvn gatling:test -Dgatling.simulationClass=com.example.socialproofing.simulation.LoadTestSimulation
```

Phases:
1. **Setup** — creates 100 products
2. **Sustained write** — 500 req/sec for 30 seconds
3. **Peak write burst** — ramps to 5,000 req/sec for 10 seconds
4. **Sustained read** — 700 req/sec for 30 seconds
5. **Peak read** — ramps to 3,000 req/sec for 10 seconds

All rates are configurable via `-D` params for scaling up on cloud:

```bash
mvn gatling:test -Dgatling.simulationClass=com.example.socialproofing.simulation.LoadTestSimulation \
  -DbaseUrl=https://your-service.akka.app \
  -DproductCount=1000 \
  -DwriteRate=500 \
  -DpeakWriteRate=50000 \
  -DreadRate=700 \
  -DpeakReadRate=7000
```

Assertions: p95 < 500ms, >99% success rate. In-memory throttling (`PERSIST_INTERVAL`) keeps journal writes bounded regardless of ingestion rate.

### Configuration

All settings have defaults in `application.conf` and can be overridden via environment variables.

| Env Var | Default | Description |
|---------|---------|-------------|
| `MODEL_PROVIDER` | `googleai-gemini` | Model provider — set to `stub` for load testing |
| `GOOGLE_AI_GEMINI_API_KEY` | — | Google Gemini API key |
| `GEMINI_MODEL_NAME` | `gemini-2.5-flash-lite` | Gemini model to use |
| `GEMINI_MAX_RETRIES` | `0` | Retry count on model failure |
| `STUB_DELAY_MS` | `50` | Simulated processing delay for stub model (ms) |
| `PERSIST_INTERVAL` | `5s` | How often to flush in-memory counters to journal |
| `AGENT_TRIGGER_INTERVAL` | `15s` | How often to trigger the AI agent with aggregated signals |
| `MIN_VIEWS` | `1` | Minimum view count before social proof is shown |
| `MIN_ORDERS` | `0` | Minimum order count before social proof is shown |

> **Stub model provider:** Set `MODEL_PROVIDER=stub` to replace the LLM with a deterministic stub that returns fixed social proof messages after a configurable delay (`STUB_DELAY_MS`). This is useful for load testing and local development without a Gemini API key or rate limit concerns. No `GOOGLE_AI_GEMINI_API_KEY` is needed when using the stub provider.

## Architecture

### Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| ProductEntity | Event Sourced Entity | Tracks view/order counters, stores cached social proof (~920 bytes per product) |
| SocialProofAgent | Agent | Selects strategy (urgency/validation/scarcity/trending) and generates copy via Gemini |
| SocialProofConsumer | Consumer | Reacts to SignalsAggregated events, triggers agent, caches result |
| SocialProofView | View | Projects products for listing and SSE streaming (streamUpdates) |
| ProductEndpoint | HTTP Endpoint | PUT /products — catalog management |
| IngestionEndpoint | HTTP Endpoint | POST /ingestion — view counts and orders |
| SocialProofEndpoint | HTTP Endpoint | GET /social-proof — cached messages, product list, SSE stream |
| DemoUIEndpoint | HTTP Endpoint | Serves static demo UI |

### How It Works

1. **Ingest**: View counts and orders arrive via HTTP and accumulate in the ProductEntity
2. **Aggregate**: When the bucket period elapses, the entity emits a `SignalsAggregated` event with current counters, then rotates (current becomes previous, current resets to zero)
3. **Generate**: The SocialProofConsumer picks up the aggregation event, calls the AI agent with the signals
4. **Cache**: The agent selects a strategy, generates copy, and the result is cached in the entity
5. **Serve**: Product page reads the cached message directly from the entity — no LLM call on the read path
6. **Stream**: The SocialProofView projects all updates and streams them to the UI via SSE

### Data Model

- **ProductState**: productId, name, category, stockLevel, currentViewCount, previousViewCount, currentOrderCount, previousOrderCount, cachedMessage, lastAggregatedAt, recentViewKeys, recentOrderKeys
- **ProductSignals**: productId, viewCount, orderCount, trendDirection, trendMultiplier
- **CachedSocialProof**: message, strategy, generatedAt
- **Strategy**: URGENCY, VALIDATION, SCARCITY, TRENDING, NONE

### Diagrams

#### User Journey Map

```mermaid
flowchart TD
    S2([P1: Ingest Product View Counts])
    S3([P1: Ingest Order Events])
    S1([P1: View Social Proof on Product Page])
    S4([P2: AI-Powered Strategy Selection])
    S5([P2: Simulated Event Generator])
    S7([P2: Multi-Region Deployment])
    S6([P3: Demo Web UI])

    S2 -->|"provides view signals"| S1
    S3 -->|"provides order signals"| S1
    S2 -->|"feeds signals to"| S4
    S3 -->|"feeds signals to"| S4
    S4 -->|"selects strategy for"| S1
    S5 -->|"generates traffic for"| S2
    S5 -->|"generates traffic for"| S3
    S6 -->|"displays"| S1
    S7 -->|"replicates"| S1

    style S1 fill:#2196F3,color:#fff
    style S2 fill:#2196F3,color:#fff
    style S3 fill:#2196F3,color:#fff
    style S4 fill:#FF9800,color:#fff
    style S5 fill:#FF9800,color:#fff
    style S7 fill:#FF9800,color:#fff
    style S6 fill:#4CAF50,color:#fff
```

#### Actor-Goal Overview

```mermaid
flowchart LR
    subgraph actors["Actors"]
        Customer([Customer])
        Demo([Demo Presenter])
    end

    subgraph system["Social Proofing Service"]
        G1[See social proof on product page]
        G2[Ingest view counts and orders]
        G3[AI selects best strategy and generates copy]
        G4[Browse product grid with live updates]
        G5[Populate demo with synthetic traffic]
    end

    subgraph ext["External / Out of Scope"]
        Analytics([Analytics Platform])
        LLM([LLM Provider])
    end

    Customer -->|"views product"| G1
    Demo -->|"opens UI"| G4
    Demo -->|"starts simulator"| G5
    Analytics -.->|"sends pre-aggregated counts"| G2
    G2 -->|"feeds signals to"| G3
    G3 -->|"caches message for"| G1
    G3 -.->|"prompts"| LLM

    style Customer fill:#4CAF50,color:#fff
    style Demo fill:#4CAF50,color:#fff
    style G1 fill:#2196F3,color:#fff
    style G2 fill:#2196F3,color:#fff
    style G3 fill:#FF9800,color:#fff
    style G4 fill:#4CAF50,color:#fff
    style G5 fill:#FF9800,color:#fff
    style Analytics stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
    style LLM stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
```

#### Entity Relationship Map

```mermaid
flowchart TD
    P([Product])
    SPM([Social Proof Message])
    DPC([Demo Product Catalog])

    P -->|"accumulates signals, produces"| SPM
    DPC -->|"defines"| P

    style P fill:#2196F3,color:#fff
    style SPM fill:#FF9800,color:#fff
    style DPC fill:#4CAF50,color:#fff
```

#### Component Dependencies

```mermaid
flowchart TD
    subgraph ext["External / Out of Scope"]
        GS([Gatling Simulation])
        LLM([LLM Provider])
        Browser([Browser])
    end

    subgraph api["API Layer"]
        PE_EP[ProductEndpoint]
        IE[IngestionEndpoint]
        SP_EP[SocialProofEndpoint]
        UI_EP[DemoUIEndpoint]
    end

    subgraph application["Application Layer"]
        PE[ProductEntity]
        AG[SocialProofAgent]
        CO[SocialProofConsumer]
        VW[SocialProofView]
    end

    GS -.->|"① PUT /products"| PE_EP
    GS -.->|"② POST /ingestion"| IE
    PE_EP -->|"③ updateProduct"| PE
    IE -->|"④ recordViews / recordOrder"| PE
    PE -->|"⑤ events"| CO
    PE -->|"⑤ events"| VW
    CO -->|"⑥ generateMessage"| AG
    AG -->|"⑦ @FunctionTool getProductDetails"| PE
    AG -.->|"⑧ prompt + signals"| LLM
    CO -->|"⑨ cacheSocialProof"| PE
    Browser -.->|"⑩ GET /social-proof"| SP_EP
    SP_EP -->|"⑪ getSocialProof"| PE
    SP_EP -->|"⑪ list + stream"| VW
    Browser -.->|"GET /"| UI_EP

    linkStyle 0,1 stroke:#2196F3,stroke-width:2px
    linkStyle 2,3 stroke:#2196F3,stroke-width:2px
    linkStyle 4,5 stroke:#FF9800,stroke-width:2px
    linkStyle 6,7,8,9 stroke:#FF9800,stroke-width:2px
    linkStyle 10,11,12,13 stroke:#4CAF50,stroke-width:2px

    style GS stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
    style LLM stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
    style Browser stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
```

#### Sequence Diagram

```mermaid
sequenceDiagram
    participant GS as Gatling
    participant PE_EP as ProductEndpoint
    participant IE as IngestionEndpoint
    participant PE as ProductEntity
    participant CO as SocialProofConsumer
    participant AG as SocialProofAgent
    participant LLM as LLM Provider
    participant VW as SocialProofView
    participant SP as SocialProofEndpoint
    participant UI as Browser

    rect rgb(33,150,243)
        Note over GS,PE: Product Setup
        GS ->> PE_EP: PUT /products/ps6-console {name, category, stockLevel}
        PE_EP ->> PE: updateProduct()
        PE -->> PE_EP: Done
    end

    rect rgb(33,150,243)
        Note over GS,PE: Signal Ingestion
        GS ->> IE: POST /ingestion/ps6-console/views {count: 50}
        IE ->> PE: recordViews(50)
        PE -->> IE: viewCount: 247
    end

    rect rgb(255,152,0)
        Note over PE,LLM: Aggregation + Agent Processing
        Note over PE: Bucket period elapsed
        PE -->> CO: SignalsAggregated event (views=247, orders=31)
        PE -->> VW: SignalsAggregated event (updates view row)
        CO ->> AG: generateMessage(signals)
        AG ->> PE: @FunctionTool getProductDetails(ps6-console)
        PE -->> AG: {name, category: Electronics, stockLevel: 3}
        AG ->> LLM: system prompt + signals + product details
        LLM -->> AG: "Only 3 left - selling fast!"
        AG -->> CO: {message, strategy: SCARCITY}
    end

    rect rgb(255,152,0)
        Note over CO,PE: Cache Result
        CO ->> PE: cacheSocialProof(message, SCARCITY)
        PE -->> VW: SocialProofCached event (updates view row)
    end

    rect rgb(76,175,80)
        Note over UI,PE: Cached Read (no LLM)
        UI ->> SP: GET /social-proof/ps6-console
        SP ->> PE: getSocialProof()
        PE -->> SP: {message, strategy: SCARCITY}
        SP -->> UI: 200 {productId, message, strategy}
    end

    rect rgb(76,175,80)
        Note over UI,VW: Real-Time Streaming
        UI ->> SP: GET /social-proof/stream (SSE)
        SP ->> VW: streaming query (streamUpdates=true)
        VW -->> SP: updated row (ps6-console)
        SP -->> UI: SSE event: {productId, message, strategy}
    end
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Counter-based state (not time-bucketed lists) | Bounded state size (~920 bytes per product) regardless of traffic volume |
| Aggregation-triggered agent (not event-triggered) | Prevents excessive LLM calls during high-throughput ingestion |
| Cache in entity state (not separate cache) | Simplest approach — entity already holds signals, no extra component |
| Gatling for traffic simulation (not in-service generator) | Keeps service code focused on business logic, same simulation for demo + load testing |
| ProductEntity as agent @FunctionTool | Agent fetches catalog data (category, stock) from entity directly |
| Idempotency keys (last 10 per type) | Deduplication for retries without unbounded state growth |

## Testing

```bash
# Unit tests
mvn test

# Unit + integration tests
mvn verify
```

## Deployment

### Prerequisites

Create the `app-secret` with your configuration. Only `GOOGLE_AI_GEMINI_API_KEY` is required; all others are optional and fall back to defaults in `application.conf`.

```bash
# Create secret with API key (and optionally override any defaults)
akka secret create generic app-secret \
  --literal GOOGLE_AI_GEMINI_API_KEY=your-key-here \
  --literal MODEL_PROVIDER=googleai-gemini \
  --literal GEMINI_MODEL_NAME=gemini-2.5-flash-lite \
  --literal GEMINI_MAX_RETRIES=0 \
  --literal STUB_DELAY_MS=500 \
  --literal PERSIST_INTERVAL=5s \
  --literal AGENT_TRIGGER_INTERVAL=15s \
  --literal MIN_VIEWS=1 \
  --literal MIN_ORDERS=0
```

Only `GOOGLE_AI_GEMINI_API_KEY` is required; remove any `--literal` lines you don't need to override.

### Build and Deploy

```bash
# Build container image
mvn clean install -DskipTests

# Deploy using service descriptor (pushes image and applies config)
akka project apply -f service.yaml --push
```

To deploy with the CLI directly instead:

```bash
akka service deploy social-proofing-agent social-proofing-agent:tag-name --push \
  --secret-env GOOGLE_AI_GEMINI_API_KEY=app-secret/GOOGLE_AI_GEMINI_API_KEY
```

Refer to [Deploy and manage services](https://doc.akka.io/operations/services/deploy-service.html) for more information.

## Project Structure

```text
src/main/java/com/example/socialproofing/
├── domain/
│   ├── ProductState.java            # State: current/previous counters, cached message
│   ├── ProductEvent.java            # Events: ViewsRecorded, OrderRecorded, SignalsAggregated, SocialProofCached
│   └── CachedSocialProof.java       # Cached message record
├── application/
│   ├── ProductEntity.java           # ESE: signal aggregation + cached message storage
│   ├── SocialProofAgent.java        # AI agent: strategy selection + copy generation
│   ├── SocialProofConsumer.java     # Consumer: reacts to aggregation, triggers agent
│   └── SocialProofView.java         # View: product listing + SSE streaming
├── api/
│   ├── ProductEndpoint.java         # PUT /products
│   ├── IngestionEndpoint.java       # POST /ingestion
│   ├── SocialProofEndpoint.java     # GET /social-proof
│   └── DemoUIEndpoint.java          # Serves static UI

src/test/java/com/example/socialproofing/
├── domain/ProductStateTest.java
├── application/ProductEntityTest.java
├── application/SocialProofAgentTest.java
├── api/IngestionEndpointIntegrationTest.java
├── api/SocialProofEndpointIntegrationTest.java
└── simulation/SocialProofSimulation.java   # Gatling traffic simulation
```
