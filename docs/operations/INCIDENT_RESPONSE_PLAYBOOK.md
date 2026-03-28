# Incident Response Playbook

Incident response procedures for Phenotype ecosystem.

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|--------------|
| SEV1 | Complete outage, data loss risk | 15 minutes |
| SEV2 | Major feature degraded, >50% users affected | 30 minutes |
| SEV3 | Minor feature degraded, <50% users affected | 4 hours |
| SEV4 | Cosmetic issues, no user impact | Next business day |

## Response Process

### 1. Detect

- Automated alerts from monitoring
- User reports via support channel
- Internal detection

### 2. Assess

```
1. Identify severity level
2. Create incident channel: #incidents-YYYY-MM-DD-<brief>
3. Assign incident commander
4. Notify stakeholders per severity
```

### 3. Mitigate

```
1. Identify root cause
2. Implement temporary fix if available
3. Communicate status to stakeholders
4. Monitor for resolution
```

### 4. Resolve

```
1. Verify fix is holding
2. Update stakeholders
3. Close incident channel
4. Schedule post-mortem
```

### 5. Post-Mortem

Within 48 hours:
- [ ] Timeline of events
- [ ] Root cause analysis
- [ ] Action items with owners
- [ ] Prevention measures

## Contact Information

| Role | Contact |
|------|---------|
| On-call engineer | PagerDuty |
| Engineering lead | @kooshapari |
| DevOps | @devops |

## Common Incidents

### Service Won't Start

1. Check logs: `kubectl logs <pod>`
2. Verify secrets exist: `kubectl get secrets`
3. Check resource limits: `kubectl describe pod <pod>`
4. Verify configmaps: `kubectl get configmaps`

### High Latency

1. Check metrics dashboard
2. Identify slow queries or endpoints
3. Scale horizontally if capacity issue
4. Enable caching if appropriate

### Database Connection Issues

1. Check database pod status
2. Verify connection string in secrets
3. Test connectivity from application pod
4. Check database logs

## Post-Mortem Template

```markdown
# Incident Post-Mortem - YYYY-MM-DD

## Summary
[Brief description of incident]

## Impact
- Users affected: X
- Duration: Y minutes
- Services affected: [...]

## Timeline
- HH:MM - Event
- HH:MM - Event

## Root Cause
[Technical explanation]

## Action Items
| Item | Owner | Due Date |
|------|-------|----------|
| ... | ... | ... |
```

## Prevention Measures

- [ ] Add monitoring/alerting
- [ ] Improve testing coverage
- [ ] Add circuit breakers
- [ ] Improve documentation
- [ ] Capacity planning
