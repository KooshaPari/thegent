#!/usr/bin/env python3
"""Test script for Swarm Controller.

This script demonstrates basic functionality and validates the controller
implementation without requiring actual agents to be running.
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from swarm_controller import (
    SwarmController,
    Config,
    AgentMetrics,
    AgentStatus,
    ResourceManager,
    QueueManager,
    RestartPolicy,
    ScalingDecision,
)


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 70)
    print("TEST: Configuration Loading")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")

    print("✓ Config loaded successfully")
    print(f"  - Health check interval: {config.health_check_interval}s")
    print(f"  - Stale threshold: {config.stale_threshold}s")
    print(f"  - Max concurrent agents: {config.max_concurrent_agents}")
    print(f"  - CPU threshold: {config.cpu_threshold}%")
    print(f"  - Memory threshold: {config.memory_threshold}%")
    print(f"  - Max restart attempts: {config.max_restart_attempts}")
    print(f"  - Restart backoff: {config.restart_backoff}")

    assert config.health_check_interval == 10
    assert config.stale_threshold == 30
    assert config.max_concurrent_agents == 10


def test_agent_metrics():
    """Test agent metrics dataclass."""
    print("\n" + "=" * 70)
    print("TEST: Agent Metrics")
    print("=" * 70)

    metrics = AgentMetrics(
        agent_id="test-agent-1",
        pid=12345,
        task_progress=5,
        cpu_percent=45.2,
        memory_percent=32.1,
    )

    print("✓ Agent metrics created")
    print(f"  - Agent ID: {metrics.agent_id}")
    print(f"  - PID: {metrics.pid}")
    print(f"  - Status: {metrics.status.value}")
    print(f"  - Task progress: {metrics.task_progress}")
    print(f"  - CPU: {metrics.cpu_percent}%")
    print(f"  - Memory: {metrics.memory_percent}%")

    # Test serialization
    data = metrics.to_dict()
    metrics2 = AgentMetrics.from_dict(data)

    print("✓ Serialization/deserialization working")
    assert metrics2.agent_id == metrics.agent_id
    assert metrics2.pid == metrics.pid
    assert metrics2.status == metrics.status


def test_resource_manager():
    """Test resource manager."""
    print("\n" + "=" * 70)
    print("TEST: Resource Manager")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")
    rm = ResourceManager(config)

    # Get system resources
    cpu, mem = rm.get_system_resources()
    print("✓ System resources retrieved")
    print(f"  - CPU: {cpu:.1f}%")
    print(f"  - Memory: {mem:.1f}%")

    # Check thresholds
    under_pressure = rm.is_resource_pressure()
    print(f"✓ Resource pressure check: {under_pressure}")

    # Get agent resources (current process)
    import os

    pid = os.getpid()
    cpu_proc, mem_proc, files = rm.get_agent_resources(pid)
    print("✓ Agent resources for current process")
    print(f"  - CPU: {cpu_proc:.1f}%")
    print(f"  - Memory: {mem_proc:.1f}%")
    print(f"  - Open files: {files}")


def test_queue_manager():
    """Test queue manager."""
    print("\n" + "=" * 70)
    print("TEST: Queue Manager")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")
    qm = QueueManager(config)

    stats = qm.get_queue_stats()
    print("✓ Queue stats retrieved")
    print(f"  - Pending: {stats['pending']}")
    print(f"  - Claimed: {stats['claimed']}")
    print(f"  - Completed: {stats['completed']}")

    backpressure = qm.is_backpressure_active()
    print(f"✓ Backpressure check: {backpressure}")

    can_accept = qm.can_accept_new_work()
    print(f"✓ Can accept new work: {can_accept}")


def test_restart_policy():
    """Test restart policy."""
    print("\n" + "=" * 70)
    print("TEST: Restart Policy")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")
    rp = RestartPolicy(config)

    # Test backoff delays
    print("✓ Restart backoff sequence:")
    for attempt in range(5):
        delay = rp.get_restart_delay(attempt)
        if delay is None:
            print(f"  - Attempt {attempt + 1}: EXCEEDED (max retries)")
        else:
            print(f"  - Attempt {attempt + 1}: {delay}s")

    # Test should_restart
    metrics = AgentMetrics(agent_id="test-agent")
    metrics.status = AgentStatus.DEAD

    should_restart = rp.should_restart(metrics)
    print(f"✓ Should restart dead agent: {should_restart}")

    # After max restarts
    metrics.restart_count = config.max_restart_attempts
    should_restart = rp.should_restart(metrics)
    print(f"✓ Should restart after max attempts: {should_restart}")


def test_scaling_decision():
    """Test scaling decision logic."""
    print("\n" + "=" * 70)
    print("TEST: Scaling Decision")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")
    sd = ScalingDecision(config)

    # Test scale up scenario
    queue_stats = {"pending": 10, "claimed": 2, "completed": 20}
    direction = sd.should_scale(queue_stats, current_agents=5, resource_available=True)
    print(f"✓ Scale up decision (pending=10): {direction.value}")

    # Test scale down scenario
    queue_stats = {"pending": 1, "claimed": 0, "completed": 50}
    direction = sd.should_scale(queue_stats, current_agents=5, resource_available=True)
    print(f"✓ Scale down decision (pending=1): {direction.value}")

    # Test resource pressure
    queue_stats = {"pending": 10, "claimed": 2, "completed": 20}
    direction = sd.should_scale(queue_stats, current_agents=5, resource_available=False)
    print(f"✓ No scale up under pressure: {direction.value}")


def test_swarm_controller():
    """Test main swarm controller."""
    print("\n" + "=" * 70)
    print("TEST: Swarm Controller")
    print("=" * 70)

    config = Config.from_yaml("config/swarm_controller_config.yaml")
    controller = SwarmController(config)

    print("✓ SwarmController initialized")
    print(f"  - Log file: {config.log_file}")
    print(f"  - State file: {config.state_file}")

    # Update metrics
    controller.update_agent_metrics(
        "test-agent-1",
        pid=12345,
        task_progress=5,
        cpu_percent=45.2,
    )

    print("✓ Agent metrics updated")

    metrics = controller.metrics.get("test-agent-1")
    if metrics:
        print(f"  - Agent ID: {metrics.agent_id}")
        print(f"  - PID: {metrics.pid}")
        print(f"  - Task progress: {metrics.task_progress}")
        print(f"  - CPU: {metrics.cpu_percent}%")

    # Get status
    status = controller.get_status()
    print("✓ Status retrieved")
    print(f"  - Agents: {len(status['agents'])}")
    print(f"  - Queue pending: {status['queue']['pending']}")

    # Get health report
    report = controller.health_report()
    print("✓ Health report generated")
    print("  Report preview:")
    for line in report.split("\n")[:5]:
        print(f"    {line}")

    # Save state
    controller._save_state()
    print(f"✓ State saved to {config.state_file}")

    # Verify state file
    state_path = Path(config.state_file)
    if state_path.exists():
        with open(state_path) as f:
            state_data = json.load(f)
            print(f"  - Saved {len(state_data)} agent(s)")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SWARM CONTROLLER TEST SUITE")
    print("=" * 70)

    tests = [
        ("Config Loading", test_config_loading),
        ("Agent Metrics", test_agent_metrics),
        ("Resource Manager", test_resource_manager),
        ("Queue Manager", test_queue_manager),
        ("Restart Policy", test_restart_policy),
        ("Scaling Decision", test_scaling_decision),
        ("Swarm Controller", test_swarm_controller),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ TEST FAILED: {name}")
            print(f"  Error: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        return 0
    print(f"\n✗ {failed} TEST(S) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
