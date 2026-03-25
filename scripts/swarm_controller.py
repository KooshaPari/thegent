#!/usr/bin/env python3
"""Self-Healing Swarm Controller for agent execution system.

Monitors agent health, detects issues, and auto-heals via pausing, restarting,
and dynamic scaling. Maintains state in .claude/swarm_state.json and logs all
decisions to .claude/swarm_controller.log.

Integration: Phase 1 - Agent Identity System & Global Registry
Provides cross-project agent discovery and hierarchical coordination.
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
except ImportError:
    print("psutil not installed. Install with: pip3 install psutil")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("pyyaml not installed. Install with: pip3 install pyyaml")
    sys.exit(1)

# Phase 1 Integration: Agent Identity System
# Check if agent_identity_system is available (imported dynamically)
AGENT_IDENTITY_AVAILABLE = True
try:
    from agent_identity_system import GlobalAgentRegistry, AgentIdentityFactory, AgentRole
except ImportError:
    AGENT_IDENTITY_AVAILABLE = False
    GlobalAgentRegistry = None  # type: ignore
    AgentIdentityFactory = None  # type: ignore
    AgentRole = None  # type: ignore


class AgentStatus(Enum):
    """Agent lifecycle states."""

    HEALTHY = "healthy"
    PAUSED = "paused"
    UNHEALTHY = "unhealthy"
    RESTARTING = "restarting"
    DEAD = "dead"


class ScalingDirection(Enum):
    """Scaling direction."""

    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass
class AgentMetrics:
    """Agent performance and health metrics."""

    agent_id: str
    pid: Optional[int] = None
    status: AgentStatus = AgentStatus.HEALTHY
    last_heartbeat: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    task_progress: int = 0
    restart_count: int = 0
    restart_timestamps: list[float] = field(default_factory=list)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    open_files: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    slo_breaches: int = 0
    session_start_time: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "pid": self.pid,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat,
            "last_activity": self.last_activity,
            "task_progress": self.task_progress,
            "restart_count": self.restart_count,
            "restart_timestamps": self.restart_timestamps,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "open_files": self.open_files,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "slo_breaches": self.slo_breaches,
            "session_start_time": self.session_start_time,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentMetrics":
        """Create from dictionary."""
        data = data.copy()
        if "status" in data and isinstance(data["status"], str):
            data["status"] = AgentStatus(data["status"])
        return cls(**data)


@dataclass
class Config:
    """Configuration for swarm controller."""

    # Health monitoring
    health_check_interval: int = 10  # seconds
    stale_threshold: int = 30  # seconds without update
    slo_time_multiplier: float = 1.5  # 150% of expected time

    # Pause vs Kill
    graceful_pause_enabled: bool = True
    max_restart_attempts: int = 3

    # Scaling
    scale_up_queue_threshold: int = 5
    scale_down_queue_threshold: int = 2
    max_concurrent_agents: int = 10
    min_concurrent_agents: int = 1

    # Resource management
    cpu_threshold: float = 80.0  # percent
    memory_threshold: float = 70.0  # percent
    max_open_files_threshold: int = 1000

    # Queue management
    max_claimed_per_agent: int = 5
    backpressure_claimed_threshold: int = 10

    # Restart backoff (seconds)
    restart_backoff: list[int] = field(default_factory=lambda: [2, 4, 8, 16])

    # Logging
    log_file: str = ".claude/swarm_controller.log"
    state_file: str = ".claude/swarm_state.json"
    agents_active_file: str = "docs/reference/AGENTS_ACTIVE.md"
    work_stream_file: str = "docs/reference/WORK_STREAM.md"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file."""
        if not Path(yaml_path).exists():
            logging.warning(f"Config file not found: {yaml_path}, using defaults")
            return cls()

        with open(yaml_path) as f:
            data = yaml.safe_load(f) or {}

        # Extract top-level config
        config_data = data.get("config", {})
        return cls(**{k: v for k, v in config_data.items() if hasattr(cls, k)})


class ResourceManager:
    """Manages system resource monitoring and thresholds."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_agent_resources(self, pid: Optional[int]) -> tuple[float, float, int]:
        """Get CPU%, memory%, and open file count for agent process.

        Returns:
            Tuple of (cpu_percent, memory_percent, open_files)
        """
        if pid is None:
            return 0.0, 0.0, 0

        try:
            proc = psutil.Process(pid)
            cpu = proc.cpu_percent(interval=0.1)
            memory = proc.memory_percent()
            open_files = len(proc.open_files())
            return cpu, memory, open_files
        except psutil.NoSuchProcess, psutil.AccessDenied:
            return 0.0, 0.0, 0

    def get_system_resources(self) -> tuple[float, float]:
        """Get overall system CPU% and memory%.

        Returns:
            Tuple of (cpu_percent, memory_percent)
        """
        return psutil.cpu_percent(interval=0.1), psutil.virtual_memory().percent

    def is_resource_pressure(self) -> bool:
        """Check if system is under resource pressure."""
        cpu, memory = self.get_system_resources()
        return cpu > self.config.cpu_threshold or memory > self.config.memory_threshold

    def should_throttle_agents(self) -> bool:
        """Check if agents should be throttled due to resource pressure."""
        return self.is_resource_pressure()


class QueueManager:
    """Manages work queue state and backpressure."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_queue_stats(self) -> dict[str, int]:
        """Get current queue statistics from WORK_STREAM.md."""
        work_stream = Path(self.config.work_stream_file)
        if not work_stream.exists():
            return {"pending": 0, "claimed": 0, "completed": 0}

        try:
            content = work_stream.read_text()
            pending = content.count("| PENDING |")
            claimed = content.count("| CLAIMED |")
            completed = content.count("| COMPLETED |")
            return {"pending": pending, "claimed": claimed, "completed": completed}
        except Exception as e:
            self.logger.error(f"Failed to read work stream: {e}")
            return {"pending": 0, "claimed": 0, "completed": 0}

    def is_backpressure_active(self) -> bool:
        """Check if backpressure should be applied."""
        stats = self.get_queue_stats()
        return stats.get("claimed", 0) > self.config.backpressure_claimed_threshold

    def can_accept_new_work(self) -> bool:
        """Check if system can accept new work."""
        return not self.is_backpressure_active()


class RestartPolicy:
    """Manages restart logic with exponential backoff."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_restart_delay(self, restart_count: int) -> Optional[int]:
        """Get delay before next restart attempt.

        Returns:
            Delay in seconds, or None if max retries exceeded.
        """
        if restart_count >= self.config.max_restart_attempts:
            return None

        if restart_count < len(self.config.restart_backoff):
            return self.config.restart_backoff[restart_count]

        return self.config.restart_backoff[-1]

    def should_restart(self, metrics: AgentMetrics) -> bool:
        """Check if agent should be automatically restarted."""
        if metrics.restart_count >= self.config.max_restart_attempts:
            return False

        if metrics.status == AgentStatus.DEAD:
            return True

        return False


class ScalingDecision:
    """Determines agent scaling decisions."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def should_scale(
        self,
        queue_stats: dict[str, int],
        current_agents: int,
        resource_available: bool,
    ) -> ScalingDirection:
        """Determine if scaling is needed."""
        queue_depth = queue_stats.get("pending", 0)

        # Scale down if queue is empty or system under pressure
        if queue_depth < self.config.scale_down_queue_threshold or not resource_available:
            if current_agents > self.config.min_concurrent_agents:
                return ScalingDirection.DOWN

        # Scale up if queue growing
        if (
            queue_depth > self.config.scale_up_queue_threshold
            and current_agents < self.config.max_concurrent_agents
            and resource_available
        ):
            return ScalingDirection.UP

        return ScalingDirection.NONE

    def get_target_agent_count(
        self,
        queue_stats: dict[str, int],
        current_agents: int,
        resource_available: bool,
    ) -> int:
        """Get target number of agents."""
        direction = self.should_scale(queue_stats, current_agents, resource_available)

        if direction == ScalingDirection.UP:
            return min(current_agents + 1, self.config.max_concurrent_agents)
        if direction == ScalingDirection.DOWN:
            return max(current_agents - 1, self.config.min_concurrent_agents)

        return current_agents


class AgentHealthMonitor:
    """Monitors agent health and detects issues."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.resource_manager = ResourceManager(config)

    def check_agent_health(self, metrics: AgentMetrics) -> AgentStatus:
        """Determine agent health status."""
        now = time.time()

        # Check if stale
        if now - metrics.last_heartbeat > self.config.stale_threshold:
            self.logger.warning(
                f"Agent {metrics.agent_id} is stale (no update for {now - metrics.last_heartbeat:.1f}s)"
            )
            return AgentStatus.UNHEALTHY

        # Check SLO
        expected_time = metrics.task_progress * 10  # Rough estimate
        if now - metrics.last_activity > expected_time * self.config.slo_time_multiplier:
            metrics.slo_breaches += 1
            self.logger.warning(f"Agent {metrics.agent_id} SLO breach (activity timeout)")
            return AgentStatus.UNHEALTHY

        # Check errors
        if metrics.error_count > 5:
            self.logger.warning(f"Agent {metrics.agent_id} has {metrics.error_count} errors")
            return AgentStatus.UNHEALTHY

        return AgentStatus.HEALTHY

    def monitor_all_agents(
        self,
        metrics_dict: dict[str, AgentMetrics],
    ) -> None:
        """Monitor all agents and update status."""
        for agent_id, metrics in metrics_dict.items():
            health = self.check_agent_health(metrics)
            old_status = metrics.status

            if health != metrics.status:
                metrics.status = health
                self.logger.info(f"Agent {agent_id} status change: {old_status.value} -> {health.value}")

            # Update resources
            cpu, mem, files = self.resource_manager.get_agent_resources(metrics.pid)
            metrics.cpu_percent = cpu
            metrics.memory_percent = mem
            metrics.open_files = files


class SwarmController:
    """Main swarm controller orchestrator."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = self._setup_logging()
        self.health_monitor = AgentHealthMonitor(config)
        self.resource_manager = ResourceManager(config)
        self.queue_manager = QueueManager(config)
        self.restart_policy = RestartPolicy(config)
        self.scaling_decision = ScalingDecision(config)
        self.metrics: dict[str, AgentMetrics] = {}
        self._load_state()

        # Phase 1 Integration: Agent Identity System
        self.agent_registry = None
        self.agent_factory = None
        self.l1_agent_id = None
        self.project_name = self._detect_project_name()
        self.agent_id_map: dict[str, str] = {}  # Maps local ID to registry ID

        # Phase 3a: Stale agent cleanup
        self.cycle_count = 0
        self.cleanup_interval = 10  # Every ~50 seconds (10 cycles @ 5s each)

        if AGENT_IDENTITY_AVAILABLE and GlobalAgentRegistry is not None and AgentIdentityFactory is not None:
            try:
                self.agent_registry = GlobalAgentRegistry()
                self.agent_factory = AgentIdentityFactory(self.agent_registry)
                self.logger.info("Phase 1: Agent Identity System initialized")
            except Exception as e:
                self.logger.warning(f"Phase 1 initialization failed: {e}")
                self.agent_registry = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("swarm_controller")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def _detect_project_name(self) -> str:
        """Detect project name from current directory."""
        # Extract project name from current working directory
        return Path.cwd().name

    def _load_state(self) -> None:
        """Load controller state from disk."""
        state_path = Path(self.config.state_file)
        if state_path.exists():
            try:
                with open(state_path) as f:
                    data = json.load(f)
                    for agent_id, metrics_data in data.items():
                        self.metrics[agent_id] = AgentMetrics.from_dict(metrics_data)
                self.logger.info(f"Loaded state for {len(self.metrics)} agents")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")

    def _save_state(self) -> None:
        """Save controller state to disk."""
        state_path = Path(self.config.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(state_path, "w") as f:
                data = {aid: metrics.to_dict() for aid, metrics in self.metrics.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent gracefully."""
        metrics = self.metrics.get(agent_id)
        if metrics is None or metrics.pid is None:
            return False

        try:
            os.kill(metrics.pid, signal.SIGSTOP)
            metrics.status = AgentStatus.PAUSED
            self.logger.info(f"Paused agent {agent_id} (PID {metrics.pid})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pause agent {agent_id}: {e}")
            return False

    def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent."""
        metrics = self.metrics.get(agent_id)
        if metrics is None or metrics.pid is None:
            return False

        try:
            os.kill(metrics.pid, signal.SIGCONT)
            metrics.status = AgentStatus.HEALTHY
            self.logger.info(f"Resumed agent {agent_id} (PID {metrics.pid})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to resume agent {agent_id}: {e}")
            return False

    def restart_agent(self, agent_id: str) -> bool:
        """Restart an agent with backoff."""
        metrics = self.metrics.get(agent_id)
        if metrics is None:
            return False

        delay = self.restart_policy.get_restart_delay(metrics.restart_count)
        if delay is None:
            self.logger.error(f"Agent {agent_id} exceeded max restart attempts ({self.config.max_restart_attempts})")
            metrics.status = AgentStatus.DEAD
            return False

        self.logger.info(f"Restarting agent {agent_id} (attempt {metrics.restart_count + 1}, delay {delay}s)")
        metrics.status = AgentStatus.RESTARTING
        metrics.restart_count += 1
        metrics.restart_timestamps.append(time.time())

        # TODO: Implement actual restart logic (integration with agent spawner)
        return True

    def handle_resource_pressure(self) -> None:
        """Handle system resource pressure by pausing low-priority agents."""
        if not self.resource_manager.should_throttle_agents():
            return

        cpu, memory = self.resource_manager.get_system_resources()
        self.logger.warning(f"Resource pressure detected: CPU {cpu:.1f}%, Memory {memory:.1f}%")

        # Pause lowest priority agents
        for agent_id, metrics in self.metrics.items():
            if metrics.status == AgentStatus.HEALTHY:
                if self.pause_agent(agent_id):
                    break  # Pause one at a time

    def handle_unhealthy_agents(self) -> None:
        """Handle unhealthy agents via restart or escalation."""
        for agent_id, metrics in self.metrics.items():
            if metrics.status == AgentStatus.UNHEALTHY:
                if self.restart_policy.should_restart(metrics):
                    self.restart_agent(agent_id)
                else:
                    self.logger.error(f"Agent {agent_id} unhealthy and cannot restart. Escalating to L1.")

    def handle_scaling(self) -> None:
        """Handle dynamic scaling based on queue depth."""
        queue_stats = self.queue_manager.get_queue_stats()
        current_agents = len([m for m in self.metrics.values() if m.status != AgentStatus.DEAD])
        resource_available = not self.resource_manager.should_throttle_agents()

        direction = self.scaling_decision.should_scale(queue_stats, current_agents, resource_available)

        if direction == ScalingDirection.UP:
            self.logger.info(f"Scaling UP: queue_depth={queue_stats.get('pending', 0)}, agents={current_agents}")
            # TODO: Spawn new agent

        elif direction == ScalingDirection.DOWN:
            self.logger.info(f"Scaling DOWN: queue_depth={queue_stats.get('pending', 0)}, agents={current_agents}")
            # Pause an agent or wind down
            for agent_id, metrics in self.metrics.items():
                if metrics.status == AgentStatus.HEALTHY:
                    self.pause_agent(agent_id)
                    break

    def _register_agent_to_registry(self, agent_id: str, metrics: AgentMetrics) -> None:
        """Phase 2/3B: Register discovered agent to global registry as L2 or L3.

        Called when an agent is first seen in monitoring.
        Heuristic: Agents become L2 (named workers), executors become L3 (under L2).
        """
        if not (self.agent_factory and AGENT_IDENTITY_AVAILABLE and self.l1_agent_id):
            return

        # Skip if already registered
        if agent_id in self.agent_id_map:
            return

        try:
            from agent_identity_system import AgentRole as _AgentRole

            # Determine role and level from agent name heuristic
            role = _AgentRole.GENERIC
            is_executor = False

            if "executor" in agent_id.lower():
                # Phase 3B: Register as L3 executor under L2
                is_executor = True
                role = _AgentRole.EXECUTOR
            elif "researcher" in agent_id.lower():
                role = _AgentRole.RESEARCHER
            elif "builder" in agent_id.lower():
                role = _AgentRole.BUILDER
            elif "integrator" in agent_id.lower():
                role = _AgentRole.INTEGRATOR

            if is_executor:
                # Phase 3B: Register as L3 under L2
                # Try to find parent L2 agent (use L1 as fallback)
                parent_l2_id = self.l1_agent_id
                # Could improve this by tracking L2 agents, but L1 works as parent too

                l3_identity = self.agent_factory.create_l3_agent(
                    self.project_name,
                    parent_l2_id=parent_l2_id,
                    capabilities=["micro_task_execution"],
                    scope_tags={"type": "executor", "local_id": agent_id},
                )
                self.agent_id_map[agent_id] = l3_identity.agent_id
                self.logger.info(f"Phase 3B: Registered L3 executor {agent_id} -> {l3_identity.agent_id}")
            else:
                # Register as L2 worker under L1
                l2_identity = self.agent_factory.create_l2_agent(
                    self.project_name,
                    role=role,
                    parent_l1_id=self.l1_agent_id,
                    capabilities=["task_execution", "sub_delegation"],
                    scope_tags={"swarm_controller_pid": str(metrics.pid), "local_id": agent_id},
                )

                # Track mapping
                self.agent_id_map[agent_id] = l2_identity.agent_id
                self.logger.info(f"Phase 2: Registered L2 agent {agent_id} -> {l2_identity.agent_id}")
        except Exception as e:
            self.logger.debug(f"Phase 2/3B: Failed to register agent {agent_id}: {e}")

    def cleanup_stale_agents(self) -> None:
        """Phase 3a: Clean up stale agents from registry."""
        if not (self.agent_registry and AGENT_IDENTITY_AVAILABLE):
            return

        try:
            stale_agents = self.agent_registry.get_stale_agents()
            if not stale_agents:
                return

            self.logger.debug(f"Phase 3a: Found {len(stale_agents)} stale agent(s)")

            for stale_id in stale_agents:
                # Try to recover first
                if self.recover_stale_agent(stale_id):
                    self.logger.info(f"Phase 3a: Recovered stale agent {stale_id}")
                else:
                    # Recovery failed, unregister
                    try:
                        self.agent_registry.unregister_agent(stale_id)
                        # Clean up local mapping
                        for local_id, registry_id in list(self.agent_id_map.items()):
                            if registry_id == stale_id:
                                del self.agent_id_map[local_id]
                                break
                        self.logger.warning(f"Phase 3a: Unregistered dead agent {stale_id}")
                    except Exception as e:
                        self.logger.debug(f"Phase 3a: Failed to unregister {stale_id}: {e}")
        except Exception as e:
            self.logger.debug(f"Phase 3a: Cleanup cycle failed: {e}")

    def recover_stale_agent(self, agent_id: str) -> bool:
        """Phase 3a: Attempt to recover a stale agent."""
        if not self.agent_registry:
            return False

        # Find the local agent ID that maps to this registry ID
        local_agent_id = None
        for local_id, registry_id in self.agent_id_map.items():
            if registry_id == agent_id:
                local_agent_id = local_id
                break

        if local_agent_id is None:
            return False

        metrics = self.metrics.get(local_agent_id)
        if metrics is None or metrics.pid is None:
            return False

        try:
            # Attempt graceful recovery: pause then resume
            self.pause_agent(local_agent_id)
            time.sleep(1)  # Brief pause for recovery
            self.resume_agent(local_agent_id)
            # Update heartbeat to mark as recovered
            self.agent_registry.update_heartbeat(agent_id)
            return True
        except Exception as e:
            self.logger.debug(f"Phase 3a: Recovery failed for {local_agent_id}: {e}")
            return False

    def update_agent_metrics(self, agent_id: str, **kwargs: Any) -> None:
        """Update metrics for an agent."""
        if agent_id not in self.metrics:
            self.metrics[agent_id] = AgentMetrics(agent_id=agent_id)

        metrics = self.metrics[agent_id]
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)

        metrics.last_activity = time.time()

    def monitor_cycle(self) -> None:
        """Run one monitoring cycle."""
        self.logger.debug("Starting monitoring cycle")

        # Monitor all agents
        self.health_monitor.monitor_all_agents(self.metrics)

        # Phase 2 Integration: Register discovered agents
        if self.agent_registry and self.agent_factory and AGENT_IDENTITY_AVAILABLE and self.l1_agent_id:
            try:
                for agent_id, metrics in self.metrics.items():
                    # Register new agents not yet in registry
                    if agent_id not in self.agent_id_map:
                        self._register_agent_to_registry(agent_id, metrics)
                    # Update heartbeat for registered L2 agents
                    elif agent_id in self.agent_id_map:
                        registry_id = self.agent_id_map[agent_id]
                        self.agent_registry.update_heartbeat(registry_id)
            except Exception as e:
                self.logger.debug(f"Phase 2: Failed to register/update agents: {e}")

        # Handle issues
        self.handle_resource_pressure()
        self.handle_unhealthy_agents()
        self.handle_scaling()

        # Phase 3a: Cleanup stale agents (every N cycles)
        if self.cycle_count % self.cleanup_interval == 0:
            self.cleanup_stale_agents()

        # Phase 1 Integration: Update heartbeats in registry
        if self.agent_registry and AGENT_IDENTITY_AVAILABLE:
            try:
                if self.l1_agent_id:
                    self.agent_registry.update_heartbeat(self.l1_agent_id)
            except Exception as e:
                self.logger.debug(f"Phase 1: Failed to update L1 heartbeat: {e}")

        # Save state
        self._save_state()

        # Increment cycle counter
        self.cycle_count += 1

        self.logger.debug("Monitoring cycle complete")

    def run_monitor(self) -> None:
        """Run continuous monitoring loop."""
        self.logger.info("Starting swarm controller monitor")

        # Phase 1 Integration: Register as L1 strategic agent
        if self.agent_factory and AGENT_IDENTITY_AVAILABLE:
            try:
                # Import AgentRole locally to avoid type issues
                from agent_identity_system import AgentRole as _AgentRole

                l1_identity = self.agent_factory.create_l1_agent(
                    self.project_name,
                    role=_AgentRole.COORDINATOR,
                    capabilities=["health_monitoring", "agent_scaling", "dynamic_restart"],
                    scope_tags={"swarm_controller": "true"},
                )
                self.l1_agent_id = l1_identity.agent_id
                self.logger.info(f"Phase 1: Registered L1 agent: {self.l1_agent_id}")
            except Exception as e:
                self.logger.warning(f"Phase 1: Failed to register L1 agent: {e}")

        try:
            while True:
                self.monitor_cycle()
                time.sleep(self.config.health_check_interval)
        except KeyboardInterrupt:
            self.logger.info("Monitor interrupted by user")
            self._save_state()

    def get_status(self) -> dict[str, Any]:
        """Get current swarm status."""
        queue_stats = self.queue_manager.get_queue_stats()
        cpu, memory = self.resource_manager.get_system_resources()

        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                aid: {
                    "status": m.status.value,
                    "restart_count": m.restart_count,
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "error_count": m.error_count,
                }
                for aid, m in self.metrics.items()
            },
            "queue": queue_stats,
            "system": {
                "cpu_percent": cpu,
                "memory_percent": memory,
            },
        }

    def health_report(self) -> str:
        """Generate a health report."""
        status = self.get_status()
        healthy_count = sum(1 for a in status["agents"].values() if a["status"] == "healthy")
        total_count = len(status["agents"])

        lines = [
            f"Swarm Controller Health Report - {status['timestamp']}",
            "=" * 70,
            f"Agents: {healthy_count}/{total_count} healthy",
            f"Queue: {status['queue']['pending']} pending, "
            f"{status['queue']['claimed']} claimed, "
            f"{status['queue']['completed']} completed",
            f"System: CPU {status['system']['cpu_percent']:.1f}%, Memory {status['system']['memory_percent']:.1f}%",
            "",
            "Agent Details:",
        ]

        for aid, agent in status["agents"].items():
            lines.append(
                f"  {aid}: {agent['status']} "
                f"(restarts: {agent['restart_count']}, "
                f"errors: {agent['error_count']}, "
                f"cpu: {agent['cpu_percent']:.1f}%, "
                f"mem: {agent['memory_percent']:.1f}%)"
            )

        return "\n".join(lines)

    def get_civilization_status(self) -> dict[str, Any]:
        """Phase 3C: Get civilization-wide status for dashboard."""
        if not self.agent_registry or not AGENT_IDENTITY_AVAILABLE:
            return {"error": "Registry not available"}

        try:
            stats = self.agent_registry.get_stats()
            stale = self.agent_registry.get_stale_agents()

            # Build project summary
            projects = {}
            for agent_id in stats.get("agents_by_project", {}):
                project = agent_id if isinstance(agent_id, str) else agent_id.project
                if project not in projects:
                    projects[project] = {
                        "l1_count": 0,
                        "l2_count": 0,
                        "l3_count": 0,
                        "stale_count": 0,
                    }

            # Count agents by level and check staleness
            for agent_dict in stats.get("agents", {}).values():
                if isinstance(agent_dict, dict):
                    project = agent_dict.get("project")
                    level = agent_dict.get("level")
                    agent_id = agent_dict.get("agent_id")

                    if project and project in projects:
                        if level == "L1":
                            projects[project]["l1_count"] += 1
                        elif level == "L2":
                            projects[project]["l2_count"] += 1
                        elif level == "L3":
                            projects[project]["l3_count"] += 1

                        if agent_id in stale:
                            projects[project]["stale_count"] += 1

            return {
                "total_agents": stats.get("total_agents", 0),
                "active_agents": stats.get("total_agents", 0) - len(stale),
                "stale_agents": len(stale),
                "projects": projects,
                "timestamp": time.time(),
            }
        except Exception as e:
            self.logger.debug(f"Phase 3C: Failed to get civilization status: {e}")
            return {"error": str(e)}

    def get_agents_by_level(self, level: str) -> dict[str, Any]:
        """Phase 3C: Query agents by level (L1, L2, or L3)."""
        if not self.agent_registry or not AGENT_IDENTITY_AVAILABLE:
            return {"error": "Registry not available"}

        try:
            from agent_identity_system import AgentLevel

            level_map = {"L1": AgentLevel.L1, "L2": AgentLevel.L2, "L3": AgentLevel.L3}

            if level not in level_map:
                return {"error": f"Invalid level: {level}"}

            agents = self.agent_registry.get_agents_by_level(level_map[level])
            return {
                "level": level,
                "count": len(agents),
                "agents": [a.agent_id for a in agents] if agents else [],
            }
        except Exception as e:
            self.logger.debug(f"Phase 3C: Failed to query level {level}: {e}")
            return {"error": str(e)}

    def get_agents_by_project(self, project: str) -> dict[str, Any]:
        """Phase 3C: Query agents by project."""
        if not self.agent_registry or not AGENT_IDENTITY_AVAILABLE:
            return {"error": "Registry not available"}

        try:
            agents = self.agent_registry.get_agents_by_project(project)
            l1_count = sum(1 for a in agents if a.level == "L1")
            l2_count = sum(1 for a in agents if a.level == "L2")
            l3_count = sum(1 for a in agents if a.level == "L3")

            return {
                "project": project,
                "total": len(agents),
                "l1": l1_count,
                "l2": l2_count,
                "l3": l3_count,
                "agents": [a.agent_id for a in agents] if agents else [],
            }
        except Exception as e:
            self.logger.debug(f"Phase 3C: Failed to query project {project}: {e}")
            return {"error": str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Self-Healing Swarm Controller for agent execution system")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run continuous monitoring loop",
    )
    parser.add_argument(
        "--auto-heal",
        action="store_true",
        help="Enable automatic healing (pause, restart, scale)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/swarm_controller_config.yaml",
        help="Path to configuration YAML file",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print current swarm status and exit",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print health report and exit",
    )
    parser.add_argument(
        "--pause-agent",
        type=str,
        help="Pause a specific agent",
    )
    parser.add_argument(
        "--resume-agent",
        type=str,
        help="Resume a specific agent",
    )
    parser.add_argument(
        "--update-metrics",
        type=str,
        nargs="+",
        help="Update agent metrics (format: agent_id key=value ...)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Load configuration
    config = Config.from_yaml(args.config)

    # Create controller
    controller = SwarmController(config)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute requested command
    if args.monitor:
        if args.auto_heal:
            controller.logger.info("Running with auto-heal enabled")
        controller.run_monitor()

    elif args.status:
        print(json.dumps(controller.get_status(), indent=2))

    elif args.report:
        print(controller.health_report())

    elif args.pause_agent:
        if controller.pause_agent(args.pause_agent):
            controller._save_state()
            print(f"Paused agent {args.pause_agent}")
        else:
            print(f"Failed to pause agent {args.pause_agent}")
            sys.exit(1)

    elif args.resume_agent:
        if controller.resume_agent(args.resume_agent):
            controller._save_state()
            print(f"Resumed agent {args.resume_agent}")
        else:
            print(f"Failed to resume agent {args.resume_agent}")
            sys.exit(1)

    elif args.update_metrics:
        agent_id = args.update_metrics[0]
        metrics_data = {}
        for item in args.update_metrics[1:]:
            key, value = item.split("=", 1)
            try:
                metrics_data[key] = int(value)
            except ValueError:
                try:
                    metrics_data[key] = float(value)
                except ValueError:
                    metrics_data[key] = value

        controller.update_agent_metrics(agent_id, **metrics_data)
        controller._save_state()
        print(f"Updated metrics for agent {agent_id}")

    else:
        # Default: run monitor with auto-heal
        controller.run_monitor()


if __name__ == "__main__":
    main()
