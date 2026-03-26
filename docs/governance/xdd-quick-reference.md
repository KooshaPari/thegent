# xDD Methodologies Quick Reference Card

**Version:** 1.0.0 | **Print:** A4 landscape, 2 pages

---

## Page 1: Development Methodologies & Design Principles

### Development Methodologies (xDD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT METHODOLOGIES                                                     │
├─────────┬──────────────────────────────────────┬────────────────────────────┤
│ TDD     │ Test-Driven Development             │ Red → Green → Refactor      │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ BDD     │ Behavior-Driven Development         │ Gherkin, human-readable      │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ ATDD    │ Acceptance-Test Driven Development  │ Tests = acceptance criteria  │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ SDD     │ Specification-Driven Development    │ Formal specs → code         │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ FDD     │ Feature-Driven Development         │ Features as unit of work    │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ CDD     │ Consumer-Driven Development        │ Consumers write contracts    │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ MDD     │ Model-Driven Development           │ Models → code (MDA, EMF)    │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ RDD     │ Responsibility-Driven Development  │ Focus on object roles       │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ DDD     │ Domain-Driven Design               │ Bounded contexts, ubiquitous│
│         │                                      │ language                   │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ ADD     │ Attribute-Driven Design             │ Non-functional → design    │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ IDD     │ Interaction-Driven Development      │ UI/UX interactions first   │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ SpecDD  │ Specification-Driven Development  │ Specs as source of truth   │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ AI-DD   │ AI-Driven Development             │ LLMs assist development    │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ PDD     │ Prompt-Driven Development          │ Prompts as specifications   │
├─────────┼──────────────────────────────────────┼────────────────────────────┤
│ StoryDD │ Story-Driven Development           │ AI generates user stories   │
└─────────┴──────────────────────────────────────┴────────────────────────────┘
```

### Design Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SOLID PRINCIPLES                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ S │ Single Responsibility    │ One reason to change                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ O │ Open/Closed             │ Open for ext, closed for mod                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ L │ Liskov Substitution     │ Subtypes substitutable                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ I │ Interface Segregation    │ Small, focused interfaces                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ D │ Dependency Inversion    │ Depend on abstractions                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ OTHER KEY PRINCIPLES                                                         │
├─────────────┬───────────────────────────────────────────────────────────────┤
│ DRY         │ Don't Repeat Yourself - one source of truth                 │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ KISS        │ Keep It Simple, Stupid                                        │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ YAGNI       │ You Aren't Gonna Need It                                     │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ GRASP       │ General Responsibility Assignment Software Patterns (9)       │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ PoLA        │ Principle of Least Astonishment                               │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ LoD         │ Law of Demeter - talk only to friends                       │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ SoC         │ Separation of Concerns                                       │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ CoC         │ Convention over Configuration                                │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ DRY         │ Don't Repeat Yourself                                        │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ WET         │ Write Everything Twice (anti-pattern to avoid)               │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ SLAP        │ Single Level of Abstraction Principle                        │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ OCP         │ Open/Closed Principle                                        │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ LSP         │ Liskov Substitution Principle                                 │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ ISP         │ Interface Segregation Principle                               │
├─────────────┼───────────────────────────────────────────────────────────────┤
│ DIP         │ Dependency Inversion Principle                                │
└─────────────┴───────────────────────────────────────────────────────────────┘
```

---

## Page 2: Architecture & Process

### Architectural Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ARCHITECTURAL PATTERNS                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ CLEAN ARCHITECTURE │ Layers: Domain → App → Interface → Infrastructure      │
├─────────────────────────────────────────────────────────────────────────────┤
│ HEXAGONAL          │ Ports & Adapters - Inside-Out, framework-agnostic      │
├─────────────────────────────────────────────────────────────────────────────┤
│ ONION              │ Core → Services → Interfaces concentric layers          │
├─────────────────────────────────────────────────────────────────────────────┤
│ CQRS               │ Command Query Responsibility Segregation               │
├─────────────────────────────────────────────────────────────────────────────┤
│ EVENT SOURCING     │ Store events, not state - full audit trail             │
├─────────────────────────────────────────────────────────────────────────────┤
│ EDA                │ Event-Driven Architecture - async, reactive             │
├─────────────────────────────────────────────────────────────────────────────┤
│ MICROSERVICES      │ Small, independent, deployable services                │
├─────────────────────────────────────────────────────────────────────────────┤
│ MODULAR MONOLITH   │ Single deploy with clear module boundaries             │
├─────────────────────────────────────────────────────────────────────────────┤
│ SERVERLESS         │ Functions as a Service - scale to zero                │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYERED            │ Traditional: Presentation → Business → Data           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SERVICE PATTERNS                                                              │
├─────────────────────────────────┬───────────────────────────────────────────┤
│ STRANGLER FIG                  │ Incrementally replace monolith              │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ ANTI-CORRUPTION LAYER          │ Translate between legacy and new systems   │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ BACKENDS FOR FRONTENDS (BFF)   │ Tailored API per frontend                 │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ CIRCUIT BREAKER                │ Prevent cascade failures                   │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ SAGA                           │ Distributed transactions pattern           │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ OUTBOX                         │ Reliable event publishing                  │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ SIDEKAR / AMBASSADOR           │ Helper container for service               │
└─────────────────────────────────┴───────────────────────────────────────────┘
```

### Process & Delivery

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT PROCESSES                                                        │
├─────────────────────────────────┬───────────────────────────────────────────┤
│ Agile │ Iterative, adaptive     │ Scrum │ Sprints, ceremonies, roles       │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ Kanban │ Visual flow, WIP       │ XP    │ Extreme Programming             │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ Lean  │ Eliminate waste         │ DevOps │ Dev + Ops collaboration        │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ GitOps │ Git as single source   │ SAFe  │ Scaled Agile Framework          │
├─────────────────────────────────┴───────────────────────────────────────────┤
│ CONTINUOUS DELIVERY                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ CI │ Continuous Integration   │ CD  │ Continuous Delivery                 │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ Trunk-Based Development        │ GitHub Flow                               │
├─────────────────────────────────┴───────────────────────────────────────────┤
│ BRANCHING STRATEGIES                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ GitFlow │ feature, develop, release, hotfix branches                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Trunk │ Short-lived feature branches, main is always deployable            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TESTING PYRAMID                                                              │
│                                                                             │
│                              ▲                                              │
│                             ╱ ╲                                             │
│                            ╱   ╲                                            │
│                           ╱ E2E ╲                                           │
│                          ╱───────╲                                          │
│                         ╱         ╲                                         │
│                        ╱ Integration╲                                       │
│                       ╱─────────────╲                                       │
│                      ╱               ╲                                       │
│                     ╱     Unit       ╲                                      │
│                    ╱───────────────────╲                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Selection Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     WHEN TO USE WHAT                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ COMPLEX DOMAIN     → DDD + Hexagonal + Clean + Event Sourcing              │
├─────────────────────────────────────────────────────────────────────────────┤
│ SIMPLE CRUD        → Layered Architecture + TDD                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ MICROSERVICES      → API Gateway + BFF + Saga + Circuit Breaker            │
├─────────────────────────────────────────────────────────────────────────────┤
│ FRONTEND-HEAVY     → Feature-Sliced + Component-driven + Storybook         │
├─────────────────────────────────────────────────────────────────────────────┤
│ LIBRARY/SDK        → Semantic Versioning + API-first + CDD                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ REAL-TIME          → EDA + WebSockets + Event Sourcing                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ DATA-INTENSIVE     → CQRS + Read Replicas + Batch Processing               │
├─────────────────────────────────────────────────────────────────────────────┤
│ STARTUP/MVP        → KISS + YAGNI + Monolith first                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ ENTERPRISE         │ DDD + Hexagonal + CQRS + Saga + Event Sourcing       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Legend:** ↑ = up | ↓ = down | → = leads to/use | ⊕ = combine with
