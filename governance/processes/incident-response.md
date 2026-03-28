# Incident Response Process

## Overview

This document defines the incident response process for the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| SRE | Incident management principles |
| Chaos Engineering | Proactive failure testing |
| Observability | Monitoring and alerting |

## Incident Severity

| Severity | Definition | Response Time |
|----------|------------|---------------|
| SEV-1 | Complete service outage | 15 minutes |
| SEV-2 | Major feature broken | 1 hour |
| SEV-3 | Minor feature broken | 4 hours |
| SEV-4 | Cosmetic issue | Next sprint |

## Incident Lifecycle

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ DETECT  │───►│ TRIAGE  │───►│ RESPOND │───►│ RESOLVE │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
  Alert/       Severity       Mitigation     Recovery
  Monitoring   Assignment     Actions        Verification
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │   RETROSPECTIVE │
                                              └─────────────┘
```

## Phase 1: Detection

### Monitoring Tools

- Application metrics (Prometheus)
- Logs (Loki/ELK)
- Traces (Jaeger)
- Health checks

### Alert Sources

| Source | Type | Severity |
|--------|------|----------|
| Prometheus alerts | Metrics | Auto-assigned |
| Sentry | Errors | Based on impact |
| Health checks | Availability | SEV-1 |
| User reports | Manual | Varies |

## Phase 2: Triage

### Initial Triage Questions

1. What is broken?
2. When did it start?
3. What is the impact?
4. Who needs to be notified?
5. How do we stop the bleeding?

### Communication Template

```markdown
**INCIDENT: {Short Description}**

Severity: SEV-{N}
Status: Investigating
Started: {YYYY-MM-DD HH:MM UTC}
Impact: {Who/what is affected}

**Current Status:**
{What we know}

**Next Steps:**
{What we're doing}

**Incident Commander:** {Name}
**Comms Channel:** {Slack thread link}
```

## Phase 3: Response

### Mitigation Actions

1. **Stop the bleeding**
   - Rollback deployment
   - Disable feature flag
   - Scale up resources
   - Block malicious traffic

2. **Gather data**
   - Check logs
   - Review metrics
   - Examine recent changes
   - Query database

3. **Implement fix**
   - Apply patch
   - Update configuration
   - Deploy hotfix

### Common Mitigations

| Issue | Mitigation |
|-------|------------|
| Deployment failure | Rollback to previous version |
| Database connection | Restart connection pool |
| Memory leak | Restart affected service |
| DDOS | Enable rate limiting |
| Data corruption | Restore from backup |

## Phase 4: Resolution

### Verification

- [ ] Service is responding
- [ ] Metrics return to normal
- [ ] No new errors in logs
- [ ] Users confirm resolution

### Resolution Communication

```markdown
**RESOLVED: {Short Description}**

Severity: SEV-{N}
Duration: {X hours Y minutes}
Resolved: {YYYY-MM-DD HH:MM UTC}

**Summary:**
{What happened and what we did}

**Root Cause:**
{Why it happened}

**Action Items:**
- [ ] {Action 1}
- [ ] {Action 2}
```

## Phase 5: Retrospective

### When

Within 48 hours of resolution for SEV-1 and SEV-2.
Within 1 week for SEV-3.

### Agenda

1. **Timeline** (15 min)
   - What happened, when

2. **Impact** (10 min)
   - Who/what was affected

3. **Root Cause** (20 min)
   - Why it happened

4. **What went well** (10 min)
   - Detection, response, communication

5. **What could improve** (15 min)
   - Process, tooling, communication

6. **Action items** (10 min)
   - Concrete improvements

### Retrospective Document

```markdown
# Incident Retrospective: {ID}-{SHORT-NAME}

**Date:** {YYYY-MM-DD}
**Severity:** SEV-{N}
**Duration:** {X hours Y minutes}
**Prepared by:** {Name}

## Summary
{One paragraph summary}

## Timeline
| Time (UTC) | Event |
|------------|-------|
| HH:MM | Event description |
| HH:MM | Event description |

## Impact
- Users affected: {N}
- Revenue impact: {Description}
- Other impact: {Description}

## Root Cause
{Detailed explanation of why}

## Contributing Factors
- Factor 1
- Factor 2

## What Went Well
- Positive 1
- Positive 2

## Areas for Improvement
- Improvement 1
- Improvement 2

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Action description | @name | YYYY-MM-DD | Pending |
```

---

*Maintained by: Architecture Guild*
