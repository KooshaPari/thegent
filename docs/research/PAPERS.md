# Academic References — thegent

**Purpose:** Research backing for dotfiles/config management architecture  
**Last Updated:** 2026-04-02

---

## Core Academic Foundations

### Nix Research (Primary Influence)

1. **"Nix: A Safe and Policy-Free System for Software Deployment"**
   - *Author:* Eelco Dolstra
   - *Institution:* Utrecht University
   - *Year:* 2006
   - *Type:* PhD Thesis
   - *URL:* https://nixos.org/~eelco/pubs/phd-thesis.pdf
   - *Key Contributions:*
     - Pure functional package management
     - Immutable software stores (/nix/store)
     - Transactional upgrades and rollbacks
     - Reproducible builds
   - *Application:* thegent Nix integration, reproducible environment guarantee
   - *Citations:* 1000+ (foundational for Nix ecosystem)

2. **"The Purely Functional Software Deployment Model"**
   - *Authors:* Eelco Dolstra, Merijn de Jonge, Eelco Visser
   - *Venue:* 26th International Conference on Software Engineering (ICSE 2004)
   - *Pages:* 205-214
   - *URL:* https://nixos.org/~eelco/pubs/icse2004-nix.pdf
   - *Key Contributions:*
     - Functional deployment model
     - Dependency isolation
     - Build reproducibility
   - *Application:* thegent factory seed reproducibility

3. **"NixOS: A Purely Functional Linux Distribution"**
   - *Authors:* Eelco Dolstra, Andres Löh
   - *Venue:* 13th ACM SIGPLAN International Conference on Functional Programming (ICFP 2008)
   - *Pages:* 367-378
   - *URL:* https://nixos.org/~eelco/pubs/icfp2008-nixos.pdf
   - *Key Contributions:*
     - System-level functional configuration
     - NixOS module system
     - Declarative system configuration
   - *Application:* thegent system configuration patterns

4. **"Integrating Software Construction and Software Deployment"**
   - *Authors:* Eelco Dolstra
   - *Venue:* 11th International Conference on Software Configuration Management (SCM 2011)
   - *URL:* https://nixos.org/~eelco/pubs/scm2011-integration.pdf
   - *Key Contributions:*
     - Unified build and deployment
     - Build system integration
   - *Application:* thegent build + deploy integration

---

## Software Architecture

5. **"Design Patterns: Elements of Reusable Object-Oriented Software"**
   - *Authors:* Gamma, Helm, Johnson, Vlissides (GoF)
   - *Publisher:* Addison-Wesley, 1994
   - *Patterns Applied:*
     - **Factory Pattern:** Factory seed system
     - **Adapter Pattern:** Multi-manager abstraction
     - **Plugin Pattern:** Skill system architecture
     - **Singleton:** Policy gate coordination

6. **"Domain-Driven Design: Tackling Complexity in the Heart of Software"**
   - *Author:* Eric Evans
   - *Publisher:* Addison-Wesley, 2003
   - *Concepts Applied:*
     - **Bounded Contexts:** Platform-specific modules
     - **Factories:** Factory seed pattern
     - **Aggregates:** Configuration bundles
     - **Domain Events:** Policy gate triggers

7. **"Clean Architecture: A Craftsman's Guide to Software Structure and Design"**
   - *Author:* Robert C. Martin
   - *Publisher:* Prentice Hall, 2017
   - *Concepts Applied:*
     - Dependency inversion
     - Boundary abstractions
     - Framework independence

---

## DevOps & Configuration Management

8. **"Infrastructure as Code: Managing Servers in the Cloud"**
   - *Author:* Kief Morris
   - *Publisher:* O'Reilly Media, 2020 (2nd Edition)
   - *Key Concepts:*
     - Declarative infrastructure
     - Immutable infrastructure
     - Idempotency
     - Configuration drift detection
   - *Application:* thegent declarative config, drift prevention via policy gates

9. **"Site Reliability Engineering: How Google Runs Production Systems"**
   - *Editors:* Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Murphy
   - *Publisher:* O'Reilly Media, 2017
   - *Key Concepts:*
     - Error budgets
     - Automation
     - Monitoring and observability
     - Change management
   - *Application:* thegent governance model, SLOs, policy gates

10. **"The DevOps Handbook"**
    - *Authors:* Gene Kim, Jez Humble, Patrick Debois, John Willis
    - *Publisher:* IT Revolution, 2021 (2nd Edition)
    - *Key Concepts:*
      - Three Ways (Flow, Feedback, Continual Learning)
      - Continuous delivery
      - Automated testing
    - *Application:* thegent continuous configuration, automated policy validation

11. **"Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation"**
    - *Authors:* Jez Humble, David Farley
    - *Publisher:* Addison-Wesley, 2010
    - *Key Concepts:*
      - Deployment pipeline
      - Build quality in
      - Everyone responsible for delivery
    - *Application:* thegent quality gates, continuous configuration

---

## Rust Systems Programming

12. **"Programming Rust: Fast, Safe Systems Development"**
    - *Authors:* Jim Blandy, Jason Orendorff, Leonora Tindall
    - *Publisher:* O'Reilly Media, 2021 (2nd Edition)
    - *Application:* Systems-level configuration management, async runtime

13. **"Rust for Rustaceans: Idiomatic Programming for Experienced Developers"**
    - *Author:* Jon Gjengset
    - *Publisher:* No Starch Press, 2021
    - *Application:* Advanced trait design, plugin architecture

14. **"Zero to Production in Rust"**
    - *Author:* Luca Palmieri
    - *Publisher:* Luca Palmieri, 2022
    - *Application:* Production patterns, telemetry, configuration

---

## Security & Policy

15. **"Security Engineering: A Guide to Building Dependable Distributed Systems"**
    - *Author:* Ross J. Anderson
    - *Publisher:* Wiley, 2020 (3rd Edition)
    - *Application:* Secure configuration defaults, policy enforcement

16. **"The Tangled Web: A Guide to Securing Modern Web Applications"**
    - *Author:* Michal Zalewski
    - *Publisher:* No Starch Press, 2011
    - *Application:* Sandboxing, security boundaries

17. **"Secure by Design"**
    - *Authors:* Dan Bergh Johnsson, Daniel Deogun, Daniel Sawano
    - *Publisher:* Manning, 2019
    - *Application:* Secure defaults, domain primitives

---

## Cross-Platform Development

18. **"POSIX Programmer's Guide"**
    - *Author:* Donald Lewine
    - *Publisher:* O'Reilly Media, 1991
    - *Application:* Unix-like compatibility layer

19. **"Advanced Programming in the UNIX Environment"**
    - *Authors:* W. Richard Stevens, Stephen A. Rago
    - *Publisher:* Addison-Wesley, 2013 (3rd Edition)
    - *Application:* File system operations, process management

---

## User Interface Patterns

20. **"The Humane Interface: New Directions for Designing Interactive Systems"**
    - *Author:* Jef Raskin
    - *Publisher:* Addison-Wesley, 2000
    - *Application:* TUI design principles, modelessness

21. **"Designing Interfaces"**
    - *Author:* Jenifer Tidwell
    - *Publisher:* O'Reilly Media, 2020 (3rd Edition)
    - *Application:* CLI/TUI patterns, progressive disclosure

---

## Research Gaps (Future Investigation)

| Topic | Current Gap | Priority | Notes |
|-------|-------------|----------|-------|
| Mobile config management | No academic research found | P3 | iOS/Android restrictive |
| Secrets management integration | Limited papers on dev secrets | P2 | 1Password/pass research |
| Configuration migration patterns | Academic gap | P2 | Dotfile tool migration |
| Team vs. personal configs | Limited research | P2 | Organizational patterns |

---

## Citation Format

When citing in thegent documentation:

```markdown
> Research: Dolstra (2006), "Nix: A Safe and Policy-Free System for Software Deployment"
> URL: https://nixos.org/~eelco/pubs/phd-thesis.pdf
> Application: Factory seed reproducibility guarantee
```

---

**Last Updated:** 2026-04-02  
**Next Review:** 2026-04-16
