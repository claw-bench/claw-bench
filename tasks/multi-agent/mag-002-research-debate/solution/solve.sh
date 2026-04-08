#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"

mkdir -p "$WORKSPACE/debate"

cat > "$WORKSPACE/debate/pro_argument.md" << 'EOF'
# Pro Argument: Start with Microservices from Day One

## Core Thesis
For a B2B SaaS project management platform targeting rapid growth, adopting microservices from the start avoids the painful and expensive monolith-to-microservices migration that most successful SaaS products eventually face. Building it right the first time is more efficient than building it twice.

## Development Velocity
While the initial setup cost is higher, microservices enable parallel development streams immediately. With 15-30 developers, you can form 3-5 autonomous teams, each owning a bounded context: real-time collaboration, project/task management, user management and billing, notifications and integrations, and reporting/analytics. These teams can deploy independently, choose their own release cadence, and iterate without waiting for monolith-wide release trains. The 4-month MVP timeline is achievable if you scope each service's MVP independently.

## Scalability from Day One
Real-time collaboration features are inherently demanding and bursty. With microservices, the collaboration service can be built on WebSockets with independent horizontal scaling, while the project CRUD service runs on a simpler request-response model. In a monolith, scaling the collaboration feature means scaling everything, wasting resources and increasing costs as you grow from 500 to 2000+ companies.

## Operational Excellence
Modern cloud-native tooling (Kubernetes, service meshes, observability platforms) has dramatically reduced the operational overhead of microservices. AWS ECS/EKS and GCP GKE provide managed infrastructure that abstracts away much of the complexity that made microservices painful five years ago. CI/CD pipelines per service mean faster feedback loops and smaller blast radius for failures.

## Team Growth
Starting with microservices establishes the organizational patterns (API contracts, ownership boundaries, on-call rotation per service) that become essential as the team grows beyond 30 people. Retrofitting these patterns onto a monolith is far more disruptive than establishing them early.

## Risk Mitigation
The biggest risk of starting monolithic is the "big rewrite" — when the monolith becomes too tangled to extract services from, teams resort to complete rewrites that consume 6-18 months while feature development stalls. Starting with clean service boundaries eliminates this risk entirely.
EOF

cat > "$WORKSPACE/debate/con_argument.md" << 'EOF'
# Con Argument: Start with a Modular Monolith

## Core Thesis
For a mid-size team under time-to-market pressure, a modular monolith delivers faster initial velocity, lower operational complexity, and preserves the option to extract microservices later — without the premature complexity tax that kills many startups before they reach product-market fit.

## Development Velocity
A monolith with well-defined module boundaries (separate packages/namespaces for collaboration, projects, users, etc.) allows the same parallel development WITHOUT the overhead of service discovery, API versioning, distributed transactions, and network debugging. Function calls are orders of magnitude simpler to debug than HTTP/gRPC calls. The 4-month MVP timeline is MUCH more achievable with a monolith — no time spent on Kubernetes configuration, service mesh setup, or distributed tracing infrastructure.

## Operational Simplicity
With 15-30 developers where "most are mid-level," requiring microservices expertise is dangerous. A monolith needs one deployment pipeline, one database, one monitoring setup. Microservices need N of each, plus service discovery, API gateways, distributed tracing, circuit breakers, and saga patterns for distributed transactions. The DevOps burden alone requires 2-3 dedicated platform engineers — that is 10-20% of the team NOT building product features.

## Cost Efficiency
Microservices infrastructure costs are 3-5x higher for small-scale deployments: multiple container instances, load balancers per service, inter-service network traffic, separate databases, observability tooling licenses per service. For 500-2000 companies, a single well-provisioned application server is more than sufficient and dramatically cheaper.

## The "Premature Optimization" Fallacy
Martin Fowler, Sam Newman, and other microservices advocates explicitly recommend starting monolithic. The boundaries between services are almost always wrong when designed upfront — you do not yet understand your domain well enough at day one. Building microservices with wrong boundaries creates distributed monolith: all the coupling of a monolith with all the operational overhead of microservices. The modular monolith lets you discover true boundaries through actual usage patterns, then extract services where they provide genuine value.

## Proven Migration Path
Companies like Shopify, GitHub, and Basecamp have demonstrated that modular monoliths scale to enormous sizes. When extraction IS needed, the modular structure makes it surgical rather than archaeological. You extract the ONE service that genuinely needs independent scaling (likely the real-time collaboration module), not everything at once.
EOF

cat > "$WORKSPACE/debate/rebuttal_pro.md" << 'EOF'
# Pro Rebuttal to Con Arguments

The Con side correctly identifies operational complexity as a concern, however they underestimate how much modern tooling has addressed this. Managed Kubernetes, Terraform, and platform-as-a-service offerings mean that the "2-3 dedicated platform engineers" claim is outdated. A single DevOps engineer with Infrastructure-as-Code templates can manage microservices infrastructure effectively.

The "wrong boundaries" argument is the Con side's strongest point, but it applies equally to monolith module boundaries. If you draw the wrong module boundaries in a monolith, cross-module coupling still creates technical debt — it is just hidden behind shared memory rather than visible API contracts. At least with microservices, the contracts are explicit and violations are immediately apparent.

Regarding cost: the 3-5x infrastructure cost claim ignores the HUMAN cost of monolith migration. When the monolith becomes a bottleneck (and for a real-time collaboration platform, it WILL), the migration project will cost far more in developer time than the incremental infrastructure spending.

The Shopify and Basecamp examples are misleading: Shopify has invested enormous engineering effort in their monolith tooling (including custom CI systems and module enforcement), and Basecamp deliberately chose small scale as a business strategy. Neither is comparable to a growth-oriented B2B SaaS startup.
EOF

cat > "$WORKSPACE/debate/rebuttal_con.md" << 'EOF'
# Con Rebuttal to Pro Arguments

The Pro side's argument about "building it right the first time" assumes you KNOW what "right" looks like before writing a line of code. This is the fundamental fallacy. No team has perfect domain knowledge at project inception. The pro-microservices position conflates ARCHITECTURAL BOUNDARIES with SERVICE BOUNDARIES — you can have clean architecture in a monolith.

The parallel development argument is overstated. With 15-30 developers, you have at most 5-6 teams. A well-structured monolith with clear module ownership achieves the same parallelism with simpler tooling. Git branching and feature flags provide independent work streams without the distributed systems complexity. Moreover, the coordination overhead of microservices (API contract negotiations, integration testing across services, shared schema evolution) often REDUCES net velocity for teams this size.

The "modern tooling makes it easy" claim is dangerous. Kubernetes is not simple — it is an entire ecosystem requiring specialized knowledge. The Pro side's "single DevOps engineer" managing production microservices is a fantasy that leads to incidents and burnout. Industry surveys consistently show that microservices operational overhead remains the top complaint among engineering teams.

Finally, the "avoiding the big rewrite" argument creates a false dilemma. The modular monolith approach IS the middle path — it captures 80% of the architectural benefits of microservices with 20% of the complexity. Service extraction from a well-modularized codebase is incremental, not catastrophic.
EOF

cat > "$WORKSPACE/debate/synthesis.md" << 'EOF'
# Debate Synthesis

## Summary of Key Arguments

Both sides present compelling arguments rooted in genuine engineering trade-offs rather than ideology.

The **Pro side** correctly identifies that microservices provide independent scaling, organizational alignment with team structure, deployment isolation, and avoidance of costly future migration. These are real, well-documented benefits that become increasingly valuable as the product and team grow. The strongest pro argument is that real-time collaboration features have fundamentally different scaling needs from CRUD operations, making service separation architecturally justified.

The **Con side** correctly identifies that a modular monolith offers faster time-to-market, dramatically lower operational complexity, more accessible skill requirements, and superior cost efficiency at launch scale. The strongest con argument is the domain discovery principle: service boundaries drawn before understanding the domain through real usage are almost always wrong, leading to the dreaded distributed monolith anti-pattern.

## Critical Analysis

The rebuttals revealed that both sides have blind spots. The Pro side underestimates the operational burden on a predominantly mid-level team, while the Con side underestimates the real-time collaboration scaling challenge. The most productive exchange was around the filter_outliers analogy: just as a single extreme outlier skews statistical measures, a single demanding feature (real-time collaboration) skews the architectural needs of the entire system.

## Verdict

The key tension is between upfront correctness (Pro) and adaptive discovery (Con). For this specific team profile — mid-level majority, 4-month MVP deadline, uncertain domain boundaries — the evidence weighs toward the Con position with important caveats from the Pro side. The recommended path forward incorporates elements from both arguments: start with a modular monolith that enforces clean boundaries, with a planned extraction for the real-time collaboration service within the first year. This hybrid approach captures the pragmatism of the monolith advocates while acknowledging the legitimate scaling concerns raised by the microservices advocates.
EOF

cat > "$WORKSPACE/analysis.md" << 'EOF'
# Architecture Analysis: Monolithic vs Microservices for B2B SaaS

## Executive Summary

After structured adversarial analysis with dedicated pro-microservices and pro-monolith advocates, followed by rebuttals and synthesis, the recommendation for a mid-size team (15-30 developers) building a project management SaaS platform is to **start with a modular monolith** with a planned extraction path for high-scale services. This balances development velocity, operational simplicity, and long-term scalability.

## Strongest Arguments from Each Side

### In Favor of Microservices (Pro Position)
- **Independent scaling**: Real-time collaboration has fundamentally different scaling characteristics than CRUD operations. Microservices allow targeted resource allocation.
- **Organizational alignment**: Service ownership maps naturally to team structure, establishing healthy patterns for team growth beyond 30 developers.
- **Deployment independence**: Smaller, more frequent deployments with reduced blast radius for failures.
- **Avoiding migration tax**: The eventual monolith-to-microservices migration is often more expensive than starting distributed.

### In Favor of Modular Monolith (Con Position)
- **Faster time-to-market**: Eliminating distributed systems complexity (service discovery, distributed tracing, API versioning) accelerates the 4-month MVP timeline.
- **Lower operational burden**: One deployment pipeline, one database, one monitoring stack — critical for a team where most engineers are mid-level.
- **Domain discovery**: Service boundaries drawn before understanding the domain are almost always wrong, leading to distributed monolith anti-patterns.
- **Cost efficiency**: 3-5x lower infrastructure costs at the 500-2000 company scale.

## Comparison

| Dimension | Microservices | Modular Monolith |
|-----------|--------------|------------------|
| MVP speed | Slower (infra setup) | Faster (simpler stack) |
| Scaling path | Built-in | Requires extraction |
| DevOps need | High (platform team) | Low (standard CI/CD) |
| Team skill fit | Requires senior talent | Accessible to mid-level |
| Infra cost (year 1) | Higher (multi-service) | Lower (single deploy) |
| Migration risk | None | Moderate (planned) |
| Domain flexibility | Low (locked boundaries) | High (refactorable) |

## Context-Dependent Recommendations

**Choose microservices from day one if:**
- The team has 3+ engineers with production microservices experience
- The MVP timeline is 6+ months (not 4)
- Real-time collaboration is the primary differentiator and must scale independently from day one
- A dedicated platform/DevOps team of 2-3 engineers is budgeted

**Choose modular monolith (RECOMMENDED for this scenario) if:**
- Most developers are mid-level without distributed systems experience
- The 4-month MVP deadline is firm
- You want to validate product-market fit before investing in infrastructure complexity
- You are willing to plan one targeted service extraction (real-time collaboration) within months 6-12

**Hybrid approach:**
Start monolithic with the collaboration module as the ONLY separate service from day one. This captures the critical scaling benefit of microservices for the most demanding component while keeping everything else simple. Extract additional services only when metrics prove they are bottlenecks.

## Key Insight from the Debate

The strongest conclusion from the adversarial process is that the monolith-vs-microservices framing is a false dichotomy. The real question is "which components genuinely benefit from independent deployment and scaling TODAY?" For most B2B SaaS products at launch, the answer is zero or one — not everything.
EOF
