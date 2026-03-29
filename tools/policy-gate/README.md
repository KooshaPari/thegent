# Policy Gate CLI

Agent-driven policy change approval system for Phenotype.

Agents cannot make arbitrary policy changes without approval. This CLI layers policy changes behind a human-driven approval queue.

## Installation

```bash
cd tools/policy-gate
pip install -e .
```

## Quick Start

### Agent: Submit a Policy Change Request

```bash
policy-gate request \
  --policy "agent-escalation" \
  --change "Allow elevated access for debugging" \
  --requester "impl-agent-003"
```

Returns a request ID: `POL-AGENT-a1b2c3d4`

Agent can optionally add JSON metadata:

```bash
policy-gate request \
  --policy "data-retention" \
  --change "Extend retention period" \
  --requester "planner-agent-001" \
  --metadata '{"priority":"high","tags":["audit","compliance"]}'
```

### Human: Review and Approve/Deny Requests

List pending requests:

```bash
policy-gate list
policy-gate list --status pending
policy-gate list --policy "agent-escalation"
```

Approve a request:

```bash
policy-gate approve POL-AGENT-a1b2c3d4
policy-gate approve POL-AGENT-a1b2c3d4 --reviewer "security-lead"
```

Deny a request:

```bash
policy-gate deny POL-AGENT-a1b2c3d4 --reason "Insufficient justification"
policy-gate deny POL-AGENT-a1b2c3d4 --reason "Does not meet security requirements" --reviewer "compliance-officer"
```

### Agent: Check Request Status

```bash
policy-gate check POL-AGENT-a1b2c3d4
```

Exit codes:
- `0` = approved (change may proceed)
- `1` = pending or error (change must not proceed)
- `2` = denied (change is explicitly blocked)

For scripting, use `--quiet`:

```bash
policy-gate check POL-AGENT-a1b2c3d4 --quiet
if [ $? -eq 0 ]; then
  echo "Approved! Proceeding with change..."
fi
```

### View Request History

See all requests (approved, pending, denied) for a policy:

```bash
policy-gate history "agent-escalation"
policy-gate history "data-retention" --limit 10
```

## Database Location

Requests are stored in SQLite at:

```
~/.phenotype/policy-requests.db
```

This directory is created automatically on first use.

## Use Cases

### Agent Wants Elevated Access

```bash
policy-gate request \
  --policy "elevated-access" \
  --change "Temporary elevated permissions for debugging session ABC" \
  --requester "debug-agent"

# ... wait for human review ...

policy-gate check POL-ELEV-xyz123 --quiet
echo $?  # 0 if approved, 1 if pending, 2 if denied
```

### Agent Proposes Policy Change

```bash
policy-gate request \
  --policy "rate-limit" \
  --change "Change default rate limit from 100 to 500 req/sec for batch operations" \
  --requester "perf-agent" \
  --metadata '{"impact":"high","rollback":"possible"}'

policy-gate list --policy "rate-limit"
# Human reviews and approves/denies
policy-gate history "rate-limit"
```

### Multi-Stage Approval

Requests can be reviewed by multiple humans. The workflow is:

1. Agent submits request
2. First human reviews → approves or denies
3. Once approved, agent proceeds
4. If denied, agent can submit revised request

## Integration with Agent Workflows

In agent code (Python):

```python
import subprocess
import sys

def check_policy_approval(request_id):
    """Check if a policy change request is approved."""
    result = subprocess.run(
        ["policy-gate", "check", request_id, "--quiet"],
        capture_output=True
    )
    if result.returncode == 0:
        return True  # Approved
    elif result.returncode == 1:
        return None  # Pending
    else:  # 2 or other
        return False  # Denied

# Usage
req_id = "POL-AGENT-a1b2c3d4"
status = check_policy_approval(req_id)

if status is True:
    print("Policy approved! Proceeding with change...")
elif status is False:
    print("Policy change denied. Cannot proceed.")
else:
    print("Policy approval pending. Please wait...")
```

Or in shell scripts:

```bash
#!/bin/bash

REQUEST_ID="POL-AGENT-a1b2c3d4"

policy-gate check "$REQUEST_ID" --quiet
case $? in
  0)
    echo "Change approved. Proceeding..."
    # Execute change
    ;;
  1)
    echo "Change pending approval. Waiting..."
    exit 1
    ;;
  2)
    echo "Change denied. Stopping."
    exit 2
    ;;
esac
```

## Commands

| Command | Purpose | Exit Codes |
|---------|---------|-----------|
| `request` | Submit a policy change request | 0=success, 1=error |
| `list` | Show pending/approved/denied requests | 0 |
| `approve` | Approve a pending request | 0=success, 1=error |
| `deny` | Deny a pending request | 0=success, 1=error |
| `check` | Check request status | 0=approved, 1=pending, 2=denied |
| `history` | Show all requests for a policy | 0 |

## Testing

```bash
cd tools/policy-gate
pytest tests/ -v
```

All tests are isolated and use temporary databases.

## Design Principles

1. **Simple**: Single SQLite database, no external services
2. **Auditable**: All decisions logged with timestamp and reviewer
3. **Scriptable**: Exit codes and quiet mode for automation
4. **Agent-safe**: Agents can only submit and check, not approve/deny
5. **Human-readable**: Rich CLI output with colors and tables

## Metadata

Requests can carry JSON metadata for context:

```bash
policy-gate request \
  --policy "feature-flag" \
  --change "Enable new UI component" \
  --requester "ui-agent" \
  --metadata '{"component":"dashboard","risk":"low","testing":"automated"}'
```

Metadata is stored but not enforced — it's for human review context only.

## Future Enhancements

- Policy templates (e.g., "always require security review")
- Automatic denials for certain keywords
- Email notifications on new requests
- Webhook integrations (GitHub, Slack)
- Time-limited approvals (e.g., "valid for 24 hours")
- Multi-approver workflows
