# Temporal (temporalio Python SDK) Context

> Definitive reference for building durable workflows with the Temporal Python SDK (temporalio).
> Sources: pypi.org/project/temporalio, github.com/temporalio/sdk-python/releases, docs.temporal.io (fetched 2026-02-20).
> **Version covered: temporalio 1.23.0 (2026-02-18, latest stable)**

---

## What is Temporal

**Temporal** is a durable workflow orchestration platform. It provides a fault-tolerant execution environment where:

- **Workflows** are long-running, resumable functions that survive process restarts, network failures, and server crashes
- **Activities** are individual steps of a workflow (external API calls, DB writes, etc.) that are executed with automatic retry
- **Workers** are processes that poll Temporal Server for work and execute workflows/activities
- **Temporal Server** stores workflow state, manages scheduling, and handles failure recovery

**Why Temporal over job queues?** Standard queues lose state on failure. Temporal durably persists every event and can replay workflow execution from any point. Workflows can sleep for days, wait for external signals, and span multiple services — without managing that state yourself.

**trace Use Case:** `temporalio>=1.7.0` in `pyproject.toml`. Used for long-running orchestration tasks (AI agent job coordination, multi-step pipelines, async background processing) where durable execution across restarts is required.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Workflow** | Deterministic, durable function decorated with `@workflow.defn`; must not have side effects |
| **Activity** | Regular function with side effects (I/O, API calls) decorated with `@activity.defn` |
| **Worker** | Process hosting workflow/activity executors; polls Temporal Server for tasks |
| **Task Queue** | Named queue pairing workflows/activities to workers |
| **Workflow ID** | Business-level unique ID for a workflow instance |
| **Run ID** | Temporal-assigned unique ID for a specific workflow run |
| **Signal** | Async message sent to a running workflow to change its state |
| **Query** | Synchronous read of a running workflow's state |
| **Update** | Sync call into a running workflow that can return a value |
| **Schedule** | Cron-like trigger for workflows |
| **Namespace** | Isolation boundary (like a tenant); `default` namespace for dev |
| **Nexus** | Temporal's cross-namespace, cross-cluster workflow RPC layer |

---

## Installation

```bash
pip install temporalio
# Current stable: temporalio >= 1.7.0 (trace), 1.23.0 latest

# With OpenTelemetry
pip install "temporalio[opentelemetry]"
```

**Temporal Server for local dev:**

```bash
# Via Temporal CLI (recommended)
brew install temporal
temporal server start-dev   # Starts on localhost:7233; UI at localhost:8233

# Or Docker
docker run --network=host temporalio/auto-setup:latest
```

---

## Client

Connect to Temporal Server to start workflows, send signals, query state.

```python
import asyncio
from temporalio.client import Client

async def main():
    # Connect to local dev server
    client = await Client.connect("localhost:7233")

    # Connect to Temporal Cloud (API key auth since temporalio 1.21+)
    client = await Client.connect(
        "mynamespace.acct.tmprl.cloud:7233",
        api_key=os.getenv("TEMPORAL_API_KEY"),
        # TLS enabled automatically when API key is provided
        namespace="mynamespace.acct",
    )

    return client
```

### Starting a Workflow

```python
# Start workflow and get handle
handle = await client.start_workflow(
    MyWorkflow.run,                     # Workflow method
    args=["input_data"],               # Positional args
    id="my-workflow-id-001",           # Unique business ID
    task_queue="my-task-queue",        # Must match worker's task_queue
    execution_timeout=timedelta(hours=1),  # Max total runtime
    run_timeout=timedelta(minutes=30),     # Max single run
    retry_policy=RetryPolicy(
        maximum_attempts=3,
        backoff_coefficient=2.0,
    ),
)

# Wait for result
result = await handle.result()

# Or start and wait in one call
result = await client.execute_workflow(
    MyWorkflow.run,
    "input_data",
    id="my-workflow-id-001",
    task_queue="my-task-queue",
)
```

### Workflow Handles

```python
# Get handle for existing workflow
handle = client.get_workflow_handle("my-workflow-id-001")

# Operations on handle
result = await handle.result()          # Wait for completion
await handle.signal(MyWorkflow.my_signal, "signal_data")
value = await handle.query(MyWorkflow.my_query)
await handle.cancel()
await handle.terminate(reason="cleanup")
description = await handle.describe()   # WorkflowExecutionDescription
```

---

## Workflows

Workflows are **deterministic** functions. No I/O, no random, no time.time() — use `workflow.now()` and `asyncio.sleep()` (which maps to Temporal timers).

```python
import asyncio
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

@dataclass
class ProcessJobInput:
    job_id: str
    config: dict

@workflow.defn
class ProcessJobWorkflow:
    def __init__(self):
        self._status = "pending"
        self._result = None

    @workflow.run
    async def run(self, input: ProcessJobInput) -> dict:
        """Main workflow entry point."""
        self._status = "running"

        # Execute activity (with automatic retry)
        result = await workflow.execute_activity(
            validate_job,                           # Activity function
            input.job_id,
            schedule_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Sleep for a duration (durable — survives restarts)
        await asyncio.sleep(1)  # Temporal timer, not OS sleep

        # Execute another activity
        final_result = await workflow.execute_activity(
            process_job,
            args=[input.job_id, result],
            start_to_close_timeout=timedelta(minutes=10),
        )

        self._status = "completed"
        self._result = final_result
        return final_result

    @workflow.signal
    async def cancel_job(self) -> None:
        """Signal handler — cancel running job."""
        self._status = "cancelled"
        # Raise CancelledError to stop workflow
        raise asyncio.CancelledError("Job cancelled by signal")

    @workflow.query
    def get_status(self) -> str:
        """Query handler — return current status."""
        return self._status

    @workflow.update
    async def pause_and_resume(self, seconds: int) -> str:
        """Update handler — pause and return when done."""
        await asyncio.sleep(seconds)
        return "Resumed"
```

### Child Workflows

```python
@workflow.run
async def run(self, parent_id: str) -> str:
    # Start child workflow
    child_handle = await workflow.start_child_workflow(
        ChildWorkflow.run,
        args=["child_input"],
        id=f"{parent_id}-child",
        task_queue="child-queue",
    )
    result = await child_handle
    return result

    # Or execute synchronously
    result = await workflow.execute_child_workflow(
        ChildWorkflow.run,
        "child_input",
        id=f"{parent_id}-child",
    )
```

### Workflow Versioning

```python
@workflow.run
async def run(self, input: str) -> str:
    # Version check for safe code evolution
    version = workflow.patched("add-validation-step")
    # version is True for new executions, False for old replaying ones
    if version:
        await workflow.execute_activity(validate, input, ...)
    return await workflow.execute_activity(process, input, ...)
```

---

## Activities

Activities are **regular Python functions** (or class methods) that perform I/O and side effects.

```python
import asyncio
from temporalio import activity

@activity.defn
async def validate_job(job_id: str) -> dict:
    """Validate job exists and is runnable."""
    # I/O is fine here
    result = await database.get_job(job_id)
    if not result:
        raise ValueError(f"Job {job_id} not found")
    return {"job_id": job_id, "status": result.status}

@activity.defn
async def process_job(job_id: str, validation: dict) -> dict:
    """Process the job."""
    # Access activity context
    info = activity.info()
    activity.logger.info(f"Processing {job_id}, attempt {info.attempt}")

    # Send heartbeat for long-running activities
    activity.heartbeat(f"Processing step 1...")

    result = await do_heavy_work(job_id)

    activity.heartbeat("Processing step 2...")
    final = await finalize(result)

    return {"status": "done", "output": final}
```

**Activity timeouts:**

| Timeout | Description |
|---------|-------------|
| `schedule_to_close_timeout` | Max time from scheduling to completion (including retries) |
| `start_to_close_timeout` | Max time for a single attempt |
| `schedule_to_start_timeout` | Max wait time in queue before worker picks up |
| `heartbeat_timeout` | Max time between heartbeats; worker considered dead if exceeded |

**Heartbeats** (required for long-running activities):

```python
@activity.defn
async def long_running_activity(items: list[str]) -> list[str]:
    results = []
    for i, item in enumerate(items):
        # Heartbeat allows cancellation and reports liveness
        activity.heartbeat({"progress": i, "total": len(items)})
        result = await process_item(item)
        results.append(result)
        await asyncio.sleep(0.1)
    return results
```

### Activity Dependency Injection

Inject shared resources (DB pools, HTTP clients) via class-based activities:

```python
from dataclasses import dataclass

@dataclass
class DatabaseActivities:
    db_pool: asyncpg.Pool
    http_client: httpx.AsyncClient

    @activity.defn
    async def get_user(self, user_id: str) -> dict:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
            return dict(row)

    @activity.defn
    async def call_external_api(self, endpoint: str) -> dict:
        response = await self.http_client.get(endpoint)
        return response.json()
```

---

## Workers

Workers poll Temporal Server and execute workflows and activities.

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

async def run_worker():
    client = await Client.connect("localhost:7233")

    # Inject shared dependencies
    db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    http_client = httpx.AsyncClient()
    db_activities = DatabaseActivities(db_pool=db_pool, http_client=http_client)

    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[ProcessJobWorkflow],          # Register workflow classes
        activities=[
            validate_job,                        # Function-based activities
            process_job,
            db_activities.get_user,              # Instance method activities
            db_activities.call_external_api,
        ],
        # Worker options
        max_concurrent_workflow_tasks=100,
        max_concurrent_activities=50,
        max_concurrent_local_activities=50,
    )

    # Run until cancelled
    await worker.run()

if __name__ == "__main__":
    asyncio.run(run_worker())
```

### Worker + FastAPI (trace pattern)

Run Temporal worker alongside FastAPI in same process:

```python
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from temporalio.client import Client
from temporalio.worker import Worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="trace-task-queue",
        workflows=[ProcessJobWorkflow],
        activities=[process_job, validate_job],
    )
    worker_task = asyncio.create_task(worker.run())

    yield {"temporal_client": client}  # Available via request.state

    # Shutdown
    worker_task.cancel()
    await asyncio.gather(worker_task, return_exceptions=True)
    await client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/jobs/{job_id}/start")
async def start_job(job_id: str, request: Request):
    client: Client = request.state.temporal_client
    handle = await client.start_workflow(
        ProcessJobWorkflow.run,
        ProcessJobInput(job_id=job_id, config={}),
        id=f"job-{job_id}",
        task_queue="trace-task-queue",
    )
    return {"run_id": handle.first_execution_run_id}
```

---

## Schedules (Cron)

```python
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from datetime import timedelta

client = await Client.connect("localhost:7233")

# Create a schedule (every hour)
await client.create_schedule(
    "hourly-cleanup",
    Schedule(
        action=ScheduleActionStartWorkflow(
            CleanupWorkflow.run,
            id="cleanup-scheduled",
            task_queue="cleanup-queue",
        ),
        spec=ScheduleSpec(
            intervals=[ScheduleIntervalSpec(every=timedelta(hours=1))],
        ),
    ),
)

# Manage schedules
handle = client.get_schedule_handle("hourly-cleanup")
await handle.trigger()    # Manual trigger
await handle.pause()      # Pause
await handle.unpause()    # Resume
await handle.delete()     # Remove
```

---

## Error Handling & Retry

```python
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError, ActivityError

# Custom retry policy
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=1),
    maximum_attempts=10,
    non_retryable_error_types=["ValueError", "AuthorizationError"],
)

# In workflow
result = await workflow.execute_activity(
    my_activity,
    retry_policy=retry_policy,
    schedule_to_close_timeout=timedelta(hours=1),
)

# Non-retryable error from activity
@activity.defn
async def my_activity(data: str) -> str:
    if not is_valid(data):
        # This error won't be retried (matching non_retryable_error_types)
        raise ApplicationError("Invalid data format", non_retryable=True)
    return process(data)
```

---

## 2026 Features (temporalio 1.23.0, 2026-02-20)

| Feature | Version Added | Status |
|---------|--------------|--------|
| Experimental standalone activity support | 1.23.0 | Experimental |
| OpenTelemetry v2 integration | 1.23.0 | Stable |
| Payload limit validation from server | 1.23.0 | Stable |
| Deployment-based Worker Versioning GA | 1.22.0 | GA |
| Worker Heartbeating (Public Preview) | 1.20.0 | Public Preview |
| TLS auto-enabled with API key | 1.21.0 | Stable |
| Python 3.9 support removed | 1.19.0 | Breaking |
| Nexus cross-cluster RPC | 1.x | Experimental |

---

## thegent / trace Integration

- **trace**: `temporalio>=1.7.0` in `pyproject.toml`; used for background job orchestration
- **Task queue**: `"trace-task-queue"` (verify in trace/src)
- **Temporal Server**: Local dev via `temporal server start-dev`; prod via Temporal Cloud or self-hosted
- **Pattern**: FastAPI lifespan starts/stops worker; route handlers dispatch workflows via client

---

## Known Issues / Gotchas

1. **Workflows must be deterministic**: No `random`, `datetime.now()`, `os.environ`, or direct I/O. Use `workflow.now()` for time, `workflow.execute_activity()` for I/O.
2. **Sandbox importing**: Modules imported after workflows load produce warnings (1.19+). Import before loading workflows or configure `ImportPolicy`.
3. **Heartbeat required**: Activities running > `heartbeat_timeout` without heartbeating are considered dead and rescheduled. Always heartbeat in loops.
4. **Worker versioning**: Changing workflow code for running instances requires `workflow.patched()` guards to handle both old and new codepaths during replay.
5. **Dataclass parameters**: Use dataclasses (not plain dicts) for workflow/activity inputs — Temporal serializes them as JSON via `dataclasses.asdict()`.
6. **Python 3.9 removed**: Since 1.19.0, minimum Python is 3.10.

---

## Sources & References

- **GitHub**: https://github.com/temporalio/sdk-python (fetched 2026-02-20)
- **Releases**: https://github.com/temporalio/sdk-python/releases (fetched 2026-02-20)
- **PyPI**: https://pypi.org/project/temporalio/ (fetched 2026-02-20)
- **Samples**: https://github.com/temporalio/samples-python (fetched 2026-02-20)
- **Temporal Docs**: https://docs.temporal.io (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Package | `temporalio>=1.7.0` |
| Latest version | `1.23.0` (2026-02-18) |
| Default server port | `localhost:7233` |
| Temporal UI port | `localhost:8233` (dev server) |
| Dev server | `temporal server start-dev` |
| Min Python | 3.10 (since 1.19.0) |

### Decorator Cheat Sheet

```python
@workflow.defn         # Mark class as workflow
@workflow.run          # Entry point (exactly one per workflow class)
@workflow.signal       # Async signal handler
@workflow.query        # Sync query handler (must be synchronous)
@workflow.update       # Sync or async update handler (can return value)
@activity.defn         # Mark function/method as activity
```

### Client Quick Patterns

```python
# Connect
client = await Client.connect("localhost:7233")

# Start workflow
handle = await client.start_workflow(MyWf.run, arg, id="id", task_queue="queue")

# Start and wait
result = await client.execute_workflow(MyWf.run, arg, id="id", task_queue="queue")

# Get existing handle
handle = client.get_workflow_handle("workflow-id")

# Signal / Query
await handle.signal(MyWf.my_signal, "data")
status = await handle.query(MyWf.get_status)
result = await handle.update(MyWf.pause_and_resume, 5)
```
