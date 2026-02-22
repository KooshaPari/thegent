"""Unified worker daemon (MTSP-05).

Consolidates MCP host, LSP multiplexer, and task worker pool into a
single persistent process to minimize process count and overhead.

WL-085: Subscribes to the SubAgentEventQueue so that orchestration events
emitted by SubAgentDispatcher are consumed and logged by the daemon.
"""

import asyncio
import logging
import signal
from thegent.governance.post_agent_run_hook import dispatch_post_agent_run_hook
from thegent.lsp.persistent_serena import PersistentSerenaDaemon
from thegent.orchestration.event_queue import SubAgentEventQueue, get_global_event_queue
from thegent.orchestration.protocol import SubAgentEventType
from thegent.orchestration.worker_pool import TaskWorkerPool

_log = logging.getLogger(__name__)


class UnifiedWorkerDaemon:
    """Unified worker daemon consolidating multiple services (MTSP-05).

    WL-085: Subscribes to the SubAgentEventQueue and forwards events to the
    structured logger so that all orchestration activity is captured centrally.
    """

    def __init__(self, event_queue: SubAgentEventQueue | None = None) -> None:
        self.serena = PersistentSerenaDaemon(port=3848)
        self.task_pool = TaskWorkerPool(max_workers=4)
        self._running = False
        # WL-085: Use the provided queue or the process-global queue.
        self._event_queue: SubAgentEventQueue = event_queue if event_queue is not None else get_global_event_queue()
        self._event_consumer_task: asyncio.Task | None = None  # type: ignore[type-arg]

    async def start(self) -> None:
        """Start all consolidated services."""
        _log.info("MTSP-05: Starting Unified Worker Daemon")
        self._running = True

        # Start Serena daemon
        await self.serena.start()

        # Start Task worker pool
        # Note: task_pool.start() is a blocking loop, so we run it in a task
        self._task_pool_task = asyncio.create_task(self.task_pool.start())

        # WL-085: Start the SubAgentEvent consumer background task.
        self._event_consumer_task = asyncio.create_task(self._consume_events())

        _log.info("Unified Worker Daemon services started")

        # Keep the daemon running
        while self._running:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """Gracefully stop all services."""
        _log.info("Stopping Unified Worker Daemon")
        self._running = False

        # WL-085: Cancel the event consumer task first.
        if self._event_consumer_task is not None and not self._event_consumer_task.done():
            self._event_consumer_task.cancel()
            try:
                await self._event_consumer_task
            except asyncio.CancelledError:
                pass

        # Stop Serena
        await self.serena.stop()

        # Stop Task pool
        self.task_pool.stop()
        if hasattr(self, "_task_pool_task"):
            await self._task_pool_task

        _log.info("Unified Worker Daemon stopped")

    # ------------------------------------------------------------------
    # WL-085: SubAgentEvent consumer
    # ------------------------------------------------------------------

    async def _consume_events(self) -> None:
        """Background task: drain SubAgentEvents and forward to logger.

        Runs until cancelled (triggered by stop()). Each event is logged at
        INFO level with structured fields matching the event schema.

        # @trace WL-085
        """
        _log.info("WL-085: SubAgentEvent consumer started")
        while True:
            event = await self._event_queue.get()
            _log.info(
                "orchestration_event event_type=%s request_id=%s parent_id=%s payload=%s",
                event.event_type,
                event.request_id,
                event.parent_id,
                event.payload,
            )
            if event.event_type == SubAgentEventType.COMPLETED:
                dispatch_post_agent_run_hook(
                    result=event.payload,
                    run_id=event.request_id,
                    session_id=event.parent_id,
                    cwd=None,
                    extra_context={
                        "event_type": str(event.event_type),
                        "output_context": event.payload,
                    },
                )


async def main():
    """Entry point for the unified worker daemon process."""
    logging.basicConfig(level=logging.INFO)
    daemon = UnifiedWorkerDaemon()

    # Handle signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))

    try:
        await daemon.start()
    except Exception as e:
        _log.error("Daemon crashed: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
