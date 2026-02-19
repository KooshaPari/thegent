# Mermaid Diagram Examples

This page demonstrates various Mermaid diagram types available in VitePress.

---

## Flowchart

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```
````

---

## Sequence Diagram

````markdown
```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Router
    
    User->>Agent: Request
    Agent->>Router: Route
    Router-->>Agent: Response
    Agent-->>User: Result
```
````

---

## Class Diagram

````markdown
```mermaid
classDiagram
    class Agent {
        +run()
        +stop()
    }
    class Router {
        +route()
    }
    Agent --> Router
```
````

---

## State Diagram

````markdown
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: start()
    Running --> Idle: stop()
    Running --> Error: error()
    Error --> Idle: reset()
```
````

---

## Gantt Chart

````markdown
```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Task 1 :a1, 2026-02-01, 7d
    Task 2 :a2, after a1, 5d
    section Phase 2
    Task 3 :a3, 2026-02-15, 10d
```
````

---

## ER Diagram

````markdown
```mermaid
erDiagram
    USER ||--o{ SESSION : has
    SESSION ||--o{ TASK : contains
    TASK }o--|| AGENT : uses
```
````

---

## Pie Chart

````markdown
```mermaid
pie title Resource Usage
    "CPU" : 40
    "Memory" : 30
    "Network" : 20
    "Storage" : 10
```
````

---

**See Also**: [VITEPRESS_USAGE_GUIDE.md](../guides/VITEPRESS_USAGE_GUIDE.md)
