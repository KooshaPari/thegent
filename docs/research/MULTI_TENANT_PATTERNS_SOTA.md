# Multi-Tenant Patterns SOTA Analysis

> **Version:** 1.0  
> **Last Updated:** 2026-04-04  
> **Status:** Draft  
> **Research Depth:** nanovms-level

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Multi-Tenancy Fundamentals](#2-multi-tenancy-fundamentals)
3. [SaaS Multi-Tenancy Architectures](#3-saas-multi-tenancy-architectures)
4. [Tenant Isolation Strategies](#4-tenant-isolation-strategies)
5. [Resource Allocation Approaches](#5-resource-allocation-approaches)
6. [Security Models](#6-security-models)
7. [Implementation Patterns](#7-implementation-patterns)
8. [Industry Case Studies](#8-industry-case-studies)
9. [Comparison Matrix](#9-comparison-matrix)
10. [Recommendations for thegent](#10-recommendations-for-thegent)
11. [References](#11-references)

---

## 1. Executive Summary

### 1.1 Research Scope

Multi-tenancy enables a single software instance to serve multiple customers (tenants) while maintaining isolation between them. This document analyzes:

- **Architectural patterns** for SaaS multi-tenancy
- **Isolation strategies** (data, compute, network)
- **Resource allocation** models
- **Security frameworks** for multi-tenant systems
- **Real-world implementations** from major cloud providers

### 1.2 Key Findings

| Finding | Impact | thegent Relevance |
|---------|--------|-------------------|
| **Cell-based isolation** is emerging | AWS, Stripe use cell architecture | Design tenant boundaries carefully |
| **Soft vs hard isolation** trade-off | Performance vs security | Offer tiered isolation |
| **Resource pooling** is standard | Kubernetes, Lambda patterns | Pool agent execution |
| **Identity is critical** | Zero trust architecture | Agent identity core to thegent |
| **Observability gaps** exist | Most platforms lack per-tenant metrics | Build tenant-aware monitoring |

### 1.3 Multi-Tenancy for Agent Platforms

Agent platforms present unique multi-tenancy challenges:

| Challenge | Traditional SaaS | Agent Platforms |
|-----------|-----------------|-----------------|
| Execution model | Request/response | Long-running, stateful |
| Resource variability | Predictable | Highly variable |
| Security boundaries | API/data | Code execution |
| State management | Database | Memory, context, knowledge |
| Cost allocation | Per-request | Per-execution-time |

---

## 2. Multi-Tenancy Fundamentals

### 2.1 Definitions

| Term | Definition |
|------|------------|
| **Tenant** | A customer or organization with isolated access to the system |
| **Cell** | A failure-isolated unit of deployment containing multiple tenants |
| **Shard** | A partition of data or compute assigned to a subset of tenants |
| **Pool** | Shared resources dynamically allocated to tenants |
| **Namespace** | Logical isolation boundary (K8s, Linux) |

### 2.2 Isolation Levels

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Isolation Level Spectrum                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Weak Isolation ◀─────────────────────────────────────▶ Strong Isolation│
│                                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Row-level │  │  Schema    │  │  Database  │  │   VM/      │        │
│  │  security  │  │  per tenant│  │  per tenant│  │   Process  │        │
│  │  (shared   │  │  (shared   │  │  (isolated │  │   isolation│        │
│  │   table)   │  │   DB)      │  │   DB)      │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
│       │               │               │               │                  │
│       ▼               ▼               ▼               ▼                  │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                    thegent Hybrid Model                      │      │
│   │                                                              │      │
│   │  Data Layer: Schema-per-tenant (with shared knowledge graph) │      │
│   │  Compute:    VM-per-tenant for execution                     │      │
│   │  Memory:     Tiered (local + shared + knowledge graph)       │      │
│   │  Network:    Isolated via namespace + policies               │      │
│   │                                                              │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  Trade-off: Performance vs Security vs Cost                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Economic Considerations

| Model | Cost per Tenant | Operational Complexity | Resource Efficiency |
|-------|-----------------|----------------------|---------------------|
| Single-tenant per instance | High | Low | Low |
| Shared compute, isolated data | Medium | Medium | High |
| Fully shared (row-level) | Low | High | Very High |
| Cell-based | Medium | Medium | High |
| Serverless/pooled | Variable | Low | Very High |

---

## 3. SaaS Multi-Tenancy Architectures

### 3.1 Architecture Patterns

#### Pattern 1: Shared Database, Shared Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Shared Database, Shared Schema                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Application Layer                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │
│  │  │ Tenant 1│  │ Tenant 2│  │ Tenant 3│  │ Tenant N│            │   │
│  │  │ (App)   │  │ (App)   │  │ (App)   │  │ (App)   │            │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │   │
│  │       │            │            │            │                   │   │
│  │       └────────────┴────────────┴────────────┘                   │   │
│  │                      │                                              │   │
│  │                      ▼                                              │   │
│  │  ┌───────────────────────────────────────────────────────────┐   │   │
│  │  │                    Database Layer                             │   │   │
│  │  │  ┌───────────────────────────────────────────────────────┐  │   │   │
│  │  │  │  Table: agents                                        │  │   │   │
│  │  │  │  ┌─────────┬─────────┬─────────┬─────────┬─────────┐   │  │   │   │
│  │  │  │  │ id      │tenant_id│ name    │ config  │ ...     │   │  │   │   │
│  │  │  │  ├─────────┼─────────┼─────────┼─────────┼─────────┤   │  │   │   │
│  │  │  │  │ 1       │ acme    │ agent1  │ {...}   │ ...     │   │  │   │   │
│  │  │  │  │ 2       │ acme    │ agent2  │ {...}   │ ...     │   │  │   │   │
│  │  │  │  │ 3       │ globex  │ agent1  │ {...}   │ ...     │   │  │   │   │
│  │  │  │  └─────────┴─────────┴─────────┴─────────┴─────────┘   │  │   │   │
│  │  │  │                                                      │  │   │   │
│  │  │  │  Query: SELECT * FROM agents WHERE tenant_id = ?     │  │   │   │
│  │  │  └───────────────────────────────────────────────────────┘  │   │   │
│  │  └───────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Characteristics:                                                       │
│  - Lowest resource overhead                                             │
│  - Highest tenant density                                               │
│  - Requires strict query filtering                                      │
│  - Risk of data leakage via bugs                                        │
│  - Best for: Low-cost, high-volume SaaS                                 │
│                                                                         │
│  Examples: Salesforce (early), Shopify, Many small SaaS                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Pros:**
- Maximum resource sharing
- Easiest schema migrations
- Lowest cost per tenant

**Cons:**
- Highest security risk
- Noisy neighbor issues
- Complex backup/restore per tenant
- Harder compliance (data residency)

---

#### Pattern 2: Shared Database, Schema-per-Tenant

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Shared Database, Schema-per-Tenant                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Application Layer                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │   │
│  │  │ Tenant 1│  │ Tenant 2│  │ Tenant 3│                          │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘                          │   │
│  │       │            │            │                                │   │
│  │       └────────────┴────────────┴───────────────────────────────┐│   │
│  │                      │                                         ││   │
│  │                      ▼                                         ││   │
│  │  ┌───────────────────────────────────────────────────────────┐│   │
│  │  │                    Database Layer                           ││   │
│  │  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐││   │
│  │  │  │ Schema: acme   │ │ Schema: globex  │ │ Schema: initech│││   │
│  │  │  │ ┌───────────┐  │ │ ┌───────────┐   │ │ ┌───────────┐ │││   │
│  │  │  │ │ agents    │  │ │ │ agents    │   │ │ │ agents    │ │││   │
│  │  │  │ │ runs      │  │ │ │ runs      │   │ │ │ runs      │ │││   │
│  │  │  │ │ memory    │  │ │ │ memory    │   │ │ │ memory    │ │││   │
│  │  │  │ └───────────┘  │ │ └───────────┘   │ │ └───────────┘ │││   │
│  │  │  └─────────────────┘ └─────────────────┘ └───────────────┘││   │
│  │  │                                                           ││   │
│  │  │  Connection: database/schema_name?tenant=acme            ││   │
│  │  └───────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Characteristics:                                                       │
│  - Better data isolation than shared schema                             │
│  - Easier per-tenant operations (backup, migration)                     │
│  - Moderate resource overhead                                           │
│  - Risk: Cross-schema queries via SQL injection                         │
│  - Best for: Medium-complexity SaaS                                     │
│                                                                         │
│  Examples: Zendesk, Freshdesk, Many B2B SaaS                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Pros:**
- Better data isolation
- Per-tenant schema customization
- Easier tenant-level operations

**Cons:**
- Schema migration complexity
- Database connection limits
- Cross-tenant analytics harder

---

#### Pattern 3: Database-per-Tenant

```
┌─────────────────────────────────────────────────────────────────────────┐
│              Database-per-Tenant                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Application Layer                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │   │
│  │  │ Tenant 1│  │ Tenant 2│  │ Tenant 3│                          │   │
│  │  │ Router  │  │ Router  │  │ Router  │                          │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘                          │   │
│  │       │            │            │                                │   │
│  │       └────────────┴────────────┴───────────────────────────────┐│   │
│  │                      │                                         ││   │
│  │                      ▼                                         ││   │
│  │  ┌───────────────────────────────────────────────────────────┐│   │
│  │  │                    Database Cluster                       ││   │
│  │  │                                                           ││   │
│  │  │  ┌──────────────────┐    ┌──────────────────┐              ││   │
│  │  │  │ Database: acme   │    │ Database: globex │              ││   │
│  │  │  │ ┌────────────┐   │    │ ┌────────────┐   │              ││   │
│  │  │  │ │ agents     │   │    │ │ agents     │   │              ││   │
│  │  │  │ │ runs       │   │    │ │ runs       │   │              ││   │
│  │  │  │ │ memory     │   │    │ │ memory     │   │              ││   │
│  │  │  │ └────────────┘   │    │ └────────────┘   │              ││   │
│  │  │  │ ┌────────────┐   │    │ ┌────────────┐   │              ││   │
│  │  │  │ │ knowledge  │   │    │ │ knowledge  │   │              ││   │
│  │  │  │ └────────────┘   │    │ └────────────┘   │              ││   │
│  │  │  └──────────────────┘    └──────────────────┘              ││   │
│  │  │                                                           ││   │
│  │  │  ┌──────────────────┐                                     ││   │
│  │  │  │ Database: initech│                                     ││   │
│  │  │  │ ┌────────────┐   │                                     ││   │
│  │  │  │ │ ...        │   │                                     ││   │
│  │  │  │ └────────────┘   │                                     ││   │
│  │  │  └──────────────────┘                                     ││   │
│  │  └───────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Characteristics:                                                       │
│  - Maximum data isolation                                               │
│  - Easiest compliance (data residency)                                  │
│  - Highest resource overhead                                            │
│  - Most expensive                                                       │
│  - Best for: Enterprise, regulated industries                           │
│                                                                         │
│  Examples: AWS RDS (option), Heroku Postgres, Enterprise SaaS         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Pros:**
- Maximum isolation
- Easiest compliance
- Independent scaling per tenant

**Cons:**
- High cost
- Connection management complexity
- Infrastructure overhead

---

#### Pattern 4: Cell-Based Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Cell-Based Multi-Tenant Architecture                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Global Control Plane                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Tenant     │  │   Routing    │  │   Global     │          │   │
│  │  │   Directory  │  │   Service    │  │   Config     │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Cell Boundary Layer                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │   │
│  │  │ Cell 1  │  │ Cell 2  │  │ Cell 3  │  │ Cell N  │              │   │
│  │  │ (us-east│  │ (us-west│  │ (eu-west│  │ (ap-south│              │   │
│  │  │  -1a)   │  │  -2b)   │  │  -1c)   │  │  -1a)   │              │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘              │   │
│  └───────┼────────────┼────────────┼────────────┼───────────────────┘   │
│          │            │            │            │                       │
│  ┌───────▼────────────▼────────────▼────────────▼───────────────────┐   │
│  │                    Cell Internals (Per Cell)                       │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐│   │
│  │  │  Tenants: 50-500 (per cell)                                ││   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            ││   │
│  │  │  │ Tenant A│ │ Tenant B│ │ Tenant C│ │ Tenant X│            ││   │
│  │  │  │(sharded)│ │(sharded)│ │(sharded)│ │(sharded)│            ││   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘            ││   │
│  │  │                                                              ││   │
│  │  │  Resources:                                                  ││   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         ││   │
│  │  │  │  Compute    │  │  Database   │  │   Cache     │         ││   │
│  │  │  │  Pool       │  │  Shard      │  │   Pool      │         ││   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘         ││   │
│  │  └──────────────────────────────────────────────────────────────┘│   │
│  │                                                                  │   │
│  │  Isolation:                                                      │   │
│  │  - Cell failure contains blast radius                          │   │
│  │  - Tenant data isolated within cell                              │   │
│  │  - Cross-cell traffic via control plane                          │   │
│  │                                                                  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Characteristics:                                                       │
│  - Failure isolation (cell blast radius)                                │
│  - Regional data residency (cells in specific regions)                  │
│  - Horizontal scalability (add cells)                                   │
│  - Complex routing layer                                                │
│  - Best for: Large-scale SaaS, global deployments                     │
│                                                                         │
│  Examples: AWS (internally), Stripe, Twilio, HubSpot                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Cell Assignment Strategies:**

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Geographic** | Cell based on region | Data residency, latency |
| **Load-based** | Cell based on capacity | Load balancing |
| **Tier-based** | Different cells for different tiers | Service levels |
| **Random** | Random assignment | Simplest implementation |
| **Sticky** | Tenant always in same cell | Session affinity |

---

## 4. Tenant Isolation Strategies

### 4.1 Isolation Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Multi-Layer Isolation Model                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 6: Application                                                   │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - Request authentication/authorization                           │   │
│  │  - Tenant context propagation                                       │   │
│  │  - Rate limiting per tenant                                         │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  Layer 5: API Gateway                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - API key validation                                               │   │
│  │  - Tenant routing                                                   │   │
│  │  - DDoS protection per tenant                                       │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  Layer 4: Compute                                                     │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - Process/container/VM isolation                                   │   │
│  │  - Resource quotas (CPU, memory)                                    │   │
│  │  - Network policies                                                  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  Layer 3: Data                                                        │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - Row-level security                                               │   │
│  │  - Schema/database separation                                       │   │
│  │  - Encryption per tenant                                            │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  Layer 2: Network                                                     │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - VPC/VNet isolation                                               │   │
│  │  - Network policies (Cilium/Calico)                                 │   │
│  │  - Service mesh (mTLS)                                              │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  Layer 1: Infrastructure                                            │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  - Physical/hardware isolation (dedicated)                         │   │
│  │  - VM isolation (virtualization)                                    │   │
│  │  - Storage encryption                                               │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  thegent Application:                                                   │
│  - Layer 6: Agent identity verification                                 │
│  - Layer 5: Tenant-scoped API keys                                      │
│  - Layer 4: VM-per-tenant execution (Firecracker)                     │
│  - Layer 3: Schema-per-tenant + shared knowledge graph                  │
│  - Layer 2: Namespace-based network isolation                           │
│  - Layer 1: Optional dedicated infrastructure (enterprise tier)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Compute Isolation Strategies

| Strategy | Isolation Level | Overhead | Best For |
|----------|-----------------|----------|----------|
| **Process** | Low | Minimal | Trusted tenants |
| **Container** | Medium | Low | Standard workloads |
| **gVisor** | High | Medium | Untrusted code |
| **VM** | Very High | Medium | Maximum security |
| **MicroVM** | Very High | Low | Serverless, multi-tenant |
| **Dedicated** | Complete | High | Enterprise |

### 4.3 Data Isolation Strategies

| Strategy | Isolation | Complexity | Performance |
|----------|-----------|------------|-------------|
| **Row-level security** | Low | Medium | High |
| **Schema separation** | Medium | Medium | Medium |
| **Database separation** | High | Low | Medium |
| **Shard per tenant** | Medium-High | High | Medium |
| **Cell per tenant** | Very High | High | Medium |
| **Encrypted per tenant** | High | Medium | Low |

---

## 5. Resource Allocation Approaches

### 5.1 Resource Models

#### Model 1: Fixed Allocation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Fixed Resource Allocation                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tenant A (Pro Plan):                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │    │
│  │  │   4 vCPUs   │ │   16 GB     │ │   100 GB    │               │    │
│  │  │   (fixed)   │ │   (fixed)   │ │   (fixed)   │               │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Tenant B (Basic Plan):                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │    │
│  │  │   1 vCPU    │ │   4 GB      │ │   10 GB     │               │    │
│  │  │   (fixed)   │ │   (fixed)   │ │   (fixed)   │               │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Characteristics:                                                       │
│  - Predictable billing                                                  │
│  - Guaranteed performance                                               │
│  - Lower utilization (unused capacity wasted)                             │
│  - Best for: Enterprise customers with steady workloads                 │
│                                                                         │
│  Examples: AWS EC2, Heroku dynos, Traditional hosting                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

#### Model 2: Pooled/Shared Allocation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Pooled Resource Allocation                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Resource Pool:                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────────────────────────────────────────────────┐     │    │
│  │  │              Shared Compute Pool                        │     │    │
│  │  │                                                         │     │    │
│  │  │    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │     │    │
│  │  │    │  Node 1 │  │  Node 2 │  │  Node 3 │  │  Node N │   │     │    │
│  │  │    │ (100    │  │ (100    │  │ (100    │  │ (100    │   │     │    │
│  │  │    │  vCPUs) │  │  vCPUs) │  │  vCPUs) │  │  vCPUs) │   │     │    │
│  │  │    └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │     │    │
│  │  │         └────────────┴────────────┴────────────┘        │     │    │
│  │  │                    │                                      │     │    │
│  │  │         ┌──────────▼──────────┐                           │     │    │
│  │  │         │   Kubernetes/       │                           │     │    │
│  │  │         │   Nomad Scheduler   │                           │     │    │
│  │  │         └──────────┬──────────┘                           │     │    │
│  │  └────────────────────┼─────────────────────────────────────┘     │    │
│  └────────────────────────┼───────────────────────────────────────────┘    │
│                          │                                              │
│  ┌───────────────────────▼──────────────────────────────────────────────┐   │
│  │                    Tenant Workloads                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐ │   │
│  │  │  Tenant A (bursty):  ████░░░░░░░░░░███░░░░░░░░░░███░░░░░░░  │ │   │
│  │  │  Actual usage: 0-50 vCPUs (variable)                           │ │   │
│  │  │  Billed: Per actual usage                                     │ │   │
│  │  ├──────────────────────────────────────────────────────────────┤ │   │
│  │  │  Tenant B (steady):  ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ │   │
│  │  │  Actual usage: 20 vCPUs (consistent)                          │ │   │
│  │  │  Billed: Per actual usage                                     │ │   │
│  │  ├──────────────────────────────────────────────────────────────┤ │   │
│  │  │  Tenant C (spiky):   ░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░  │ │   │
│  │  │  Actual usage: 0-80 vCPUs (rare spikes)                      │ │   │
│  │  │  Billed: Per actual usage (may have min commitment)          │ │   │
│  │  └──────────────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Characteristics:                                                       │
│  - High utilization (statistical multiplexing)                          │
│  - Cost efficiency                                                      │
│  - Risk of noisy neighbors                                              │
│  - Requires strong isolation                                            │
│  - Best for: Serverless, variable workloads                               │
│                                                                         │
│  Examples: AWS Lambda, Google Cloud Run, Modal, Fly.io Machines           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

#### Model 3: Quota-Based with Burst

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Quota-Based with Burst Allocation                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tenant Configuration:                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │    │
│  │  │   Base       │  │   Burst      │  │   Limit      │          │    │
│  │  │   Quota      │  │   Allowance  │  │   Ceiling    │          │    │
│  │  │  (guaranteed)│  │  (temporary) │  │  (hard max)  │          │    │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤          │    │
│  │  │   10 vCPUs   │  │   +20 vCPUs  │  │   30 vCPUs   │          │    │
│  │  │   10 GB RAM  │  │   +20 GB     │  │   40 GB      │          │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Usage Pattern:                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                                                                 │    │
│  │  Usage    ▲                                                     │    │
│  │           │           ╭───────╮                                 │    │
│  │  30 ──────┼───────────┤ Limit │←────────── Hard ceiling         │    │
│  │           │      ╭────┴──╯     │                                 │    │
│  │  20 ──────┼──────┤ Burst │←──────────────── Burst allowance      │    │
│  │           │ ╭────┴──╯    │     │                                 │    │
│  │  10 ──────┼─┤ Base  │←────────────────── Guaranteed quota        │    │
│  │           │─┘       │    │     │                                 │    │
│  │   0 ──────┴─────────┴────┴─────┴────────────────────────────    │    │
│  │           t1   t2   t3   t4   t5   t6   t7   t8   t9            │    │
│  │                                                                 │    │
│  │  Time:    Normal  Spike    Normal   Spike   Normal              │    │
│  │                                                                 │    │
│  │  Billing: Base quota + burst usage (premium rate)               │    │
│  │                                                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Characteristics:                                                       │
│  - Guaranteed baseline performance                                      │
│  - Ability to handle spikes                                             │
│  - Fair sharing of excess capacity                                      │
│  - More complex billing                                                   │
│  - Best for: Production workloads with variable demand                    │
│                                                                         │
│  Examples: AWS Fargate, Kubernetes ResourceQuotas, Google Cloud          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Scheduling Strategies

| Strategy | Description | Fairness | Efficiency | Latency |
|----------|-------------|----------|------------|---------|
| **FCFS** | First come, first served | Low | Low | High |
| **Round Robin** | Equal time slices | High | Medium | Medium |
| **Weighted Fair** | Proportional to priority | Configurable | Medium | Medium |
| **CFS** | Completely Fair Scheduler | High | High | Low |
| **EDF** | Earliest deadline first | High | High | Low |
| **Bin Packing** | Fill nodes efficiently | Low | Very High | Variable |

---

## 6. Security Models

### 6.1 Tenant Identity and Authentication

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Tenant Identity Architecture                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Request Flow:                                                          │
│                                                                         │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐        │
│  │  Client  │────▶│   API    │────▶│  Auth    │────▶│  Tenant  │        │
│  │          │     │  Gateway │     │ Service  │     │ Context  │        │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘        │
│       │                │                │                │              │
│       │                │                │                │              │
│       ▼                ▼                ▼                ▼                │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐        │
│  │ API Key  │     │ Rate     │     │ JWT      │     │ Tenant   │        │
│  │ or Token │     │ Limit    │     │ Validate │     │ ID       │        │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘        │
│                                                                         │
│  Tenant Context Propagation:                                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Request Context                                                  │    │
│  │  {                                                              │    │
│  │    "tenant_id": "acme-corp",                                    │    │
│  │    "tenant_tier": "enterprise",                                   │    │
│  │    "tenant_region": "us-east-1",                                  │    │
│  │    "cell_id": "cell-42",                                          │    │
│  │    "user_id": "user-123",                                         │    │
│  │    "permissions": ["agent:read", "agent:write"],                │    │
│  │    "quota": {"cpu": 10, "memory": 32, "agents": 100}             │    │
│  │  }                                                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Propagation:                                                           │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌────────┐│
│  │  API    │───▶│  App    │───▶│  Service│───▶│  Worker │───▶│  Data  ││
│  │  GW     │    │  Layer  │    │  Mesh   │    │  Pool   │    │  Layer ││
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └────────┘│
│      │             │             │             │             │          │
│      └─────────────┴─────────────┴─────────────┴─────────────┘          │
│                    │                                                    │
│                    ▼                                                    │
│           ┌─────────────────┐                                           │
│           │  Tenant Context │                                           │
│           │  (request-local)│                                           │
│           └─────────────────┘                                           │
│                                                                         │
│  Security Properties:                                                     │
│  - Context validated at each hop                                        │
│  - Tamper-evident (signed or encrypted)                                 │
│  - Short-lived (request-scoped)                                         │
│  - Auditable (logged with tenant_id)                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Zero Trust Architecture

| Principle | Implementation |
|-----------|----------------|
| **Never trust, always verify** | Every request authenticated |
| **Least privilege** | RBAC per tenant |
| **Assume breach** | Compartmentalization |
| **Verify explicitly** | mTLS, request signing |
| **Use least access** | Time-limited credentials |

---

## 7. Implementation Patterns

### 7.1 Request Routing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Tenant Request Routing                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Load Balancer                              │   │
│  │                   (Anycast / Global LB)                           │   │
│  └────────────────────────┬────────────────────────────────────────┘   │
│                           │                                             │
│              ┌────────────┼────────────┐                                 │
│              │            │            │                                 │
│  ┌───────────▼────┐ ┌──────▼──────┐ ┌───▼──────────┐                    │
│  │  Edge Location │ │ Edge Location│ │ Edge Location│                    │
│  │    (LAX)       │ │    (LHR)     │ │    (SIN)     │                    │
│  └───────┬────────┘ └──────┬───────┘ └──────┬───────┘                    │
│          │                 │                │                           │
│          └────────────────┴────────────────┘                           │
│                            │                                             │
│                 ┌──────────▼──────────┐                                 │
│                 │   Tenant Router     │                                 │
│                 │   (Global Plane)    │                                 │
│                 │                     │                                 │
│                 │  1. Extract tenant_id│                                 │
│                 │  2. Lookup tenant   │                                 │
│                 │     configuration   │                                 │
│                 │  3. Route to cell   │                                 │
│                 └──────────┬──────────┘                                 │
│                            │                                             │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                        Cell Router                                │   │
│  │                       (Cell Plane)                                │   │
│  │                                                                 │   │
│  │  Routing Decision:                                              │   │
│  │  - Is tenant in this cell? Yes/No                               │   │
│  │  - Which shard? Hash(tenant_id) % num_shards                     │   │
│  │  - Which pod? Consistent hashing                                │   │
│  │  - Local or remote? Prefer local                                │   │
│  │                                                                 │   │
│  └─────────────────────────┬───────────────────────────────────────┘   │
│                            │                                             │
│                 ┌──────────▼──────────┐                                 │
│                 │   Service Mesh      │                                 │
│                 │   (mTLS + Auth)     │                                 │
│                 └──────────┬──────────┘                                 │
│                            │                                             │
│                 ┌──────────▼──────────┐                                 │
│                 │   Application Pod   │                                 │
│                 │   (Tenant Context)    │                                 │
│                 └───────────────────────┘                                 │
│                                                                         │
│  Routing Table Example:                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  tenant_id │  cell_id  │  shard  │  tier      │  region         │   │
│  │  acme-corp │  cell-42  │  7      │ enterprise │  us-east-1      │   │
│  │  globex    │  cell-42  │  7      │ standard   │  us-east-1      │   │
│  │  initech   │  cell-99  │  3      │ basic      │  eu-west-1      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 7.2 Cross-Tenant Operations

| Operation | Pattern | Implementation |
|-----------|---------|----------------|
| **Analytics** | Federated query | Query each tenant, aggregate |
| **Backup** | Per-tenant export | Tenant-scoped dump |
| **Migration** | Online with dual-write | Write to old+new, verify |
| **Feature flags** | Tenant-scoped config | Database or config service |
| **Rate limiting** | Token bucket per tenant | Redis or in-memory |

---

## 8. Industry Case Studies

### 8.1 AWS Lambda

| Aspect | Implementation |
|--------|----------------|
| **Compute** | Firecracker MicroVMs |
| **Isolation** | VM-level per invocation |
| **Resource Model** | Pooled with burst |
| **Multi-tenancy** | Thousands per host |
| **Cold Start** | <125ms |
| **Billing** | Per 100ms execution |

### 8.2 Stripe

| Aspect | Implementation |
|--------|----------------|
| **Architecture** | Cell-based |
| **Data** | Shard per merchant |
| **Routing** | Merchant ID → cell → shard |
| **Isolation** | Database-level |
| **Scale** | Millions of merchants |

### 8.3 Salesforce

| Aspect | Implementation |
|--------|----------------|
| **Database** | Shared schema, row-level |
| **Apex Code** | Tenant-scoped execution |
| **Metadata** | Multi-tenant ORM |
| **Scale** | 150k+ customers |

### 8.4 Twilio

| Aspect | Implementation |
|--------|----------------|
| **Cells** | Per-region cells |
| **Routing** | Phone number → cell |
| **Isolation** | Cell + namespace |
| **Scale** | Billions of messages/month |

---

## 9. Comparison Matrix

### 9.1 Architecture Comparison

| Architecture | Isolation | Cost | Complexity | Scale | Flexibility |
|--------------|-----------|------|------------|-------|-------------|
| Shared DB/Schema | Low | Low | Low | High | High |
| Shared DB/Schema-per-tenant | Medium | Medium | Medium | High | Medium |
| DB-per-tenant | High | High | Low | Medium | Low |
| Cell-based | High | Medium | High | Very High | Medium |
| Serverless/Pooled | High | Variable | Medium | Very High | High |

### 9.2 Isolation Strategy Comparison

| Strategy | Security | Performance | Cost | Operational |
|----------|----------|-------------|------|-------------|
| Row-level | Medium | High | Low | Medium |
| Schema | Medium-High | Medium | Medium | Medium |
| Database | High | Medium | Medium-High | Low |
| VM | Very High | Medium | Medium | Medium |
| MicroVM | Very High | High | Low | Medium |

---

## 10. Recommendations for thegent

### 10.1 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Recommended thegent Multi-Tenancy                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Tier 1: Enterprise (Maximum Isolation)                                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  - Dedicated cell per enterprise tenant                           │    │
│  │  - Firecracker VM per agent execution                            │    │
│  │  - Database-per-tenant                                           │    │
│  │  - Dedicated VPC option                                          │    │
│  │  - SOC2 / ISO27001 compliance documentation                      │    │
│  │  - Custom SLA                                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Tier 2: Professional (Balanced)                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  - Shared cell with namespace isolation                          │    │
│  │  - Kata Containers with Firecracker                              │    │
│  │  - Schema-per-tenant                                             │    │
│  │  - Resource quotas with burst                                   │    │
│  │  - Standard SLA                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Tier 3: Starter (Cost-Optimized)                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  - Shared cell, shared compute pool                               │    │
│  │  - gVisor containers                                             │    │
│  │  - Shared schema with row-level security                        │    │
│  │  - Best-effort resources                                         │    │
│  │  - Community support                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Shared Services (All Tiers):                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  - Global knowledge graph (tenant-scoped views)                  │    │
│  │  - Unified agent registry (tenant-filtered)                      │    │
│  │  - Cross-tenant routing service                                  │    │
│  │  - Shared telemetry (aggregated, anonymized)                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Implementation Checklist

| Phase | Component | Priority | Timeline |
|-------|-----------|----------|----------|
| 1 | Tenant identity service | P0 | Q2 2026 |
| 1 | Request routing layer | P0 | Q2 2026 |
| 1 | Schema-per-tenant DB | P0 | Q2 2026 |
| 2 | Cell-based deployment | P1 | Q3 2026 |
| 2 | Firecracker integration | P1 | Q3 2026 |
| 2 | Resource quotas | P1 | Q3 2026 |
| 3 | Tenant-aware observability | P2 | Q4 2026 |
| 3 | Auto-scaling per tenant | P2 | Q4 2026 |

---

## 11. References

### 11.1 Industry Resources

1. "Multi-Tenant SaaS Architecture" - AWS Whitepaper (2023)
2. "Cell-Based Architecture" - AWS Builders' Library (2022)
3. "Designing Data-Intensive Applications" - Martin Kleppmann (2017)
4. "Multi-Tenant Data Architecture" - Microsoft Patterns & Practices
5. "The Architecture of Open Source Applications" - Various Authors

### 11.2 Company Engineering Blogs

1. **Stripe**: "Sharding at Stripe" - https://stripe.com/blog/sharding
2. **AWS**: "How AWS Lambda Works" - https://aws.amazon.com/blogs/compute/
3. **Salesforce**: "Multi-Tenant Architecture" - https://www.salesforce.com/
4. **Twilio**: "Cell-Based Architecture" - https://www.twilio.com/blog
5. **Netflix**: "Multi-Region Architecture" - https://netflixtechblog.com/

### 11.3 Academic Papers

1. "Scaling Multi-Tenant Applications" - ACM SIGMOD 2019
2. "Cell-Based Distributed Systems" - SOSP 2021
3. "Resource Isolation in Cloud Computing" - IEEE Cloud 2020
4. "Tenant Placement in Multi-Tenant Databases" - VLDB 2018
5. "Security Isolation in Shared Cloud Infrastructure" - USENIX Security 2022

### 11.4 Standards and Compliance

1. NIST SP 800-204B: "Attribute-Based Access Control"
2. ISO/IEC 27001:2013 - Information Security Management
3. SOC 2 Trust Services Criteria
4. GDPR Article 32 - Security of Processing
5. HIPAA Security Rule (for healthcare scenarios)

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-04 | Research Agent | Initial SOTA analysis |

---

*This document follows the nanovms specification gold standard for technical documentation.*
