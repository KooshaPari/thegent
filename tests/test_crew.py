"""Unit tests for crew system."""


import pytest

from thegent.crew import (
    Crew,
    CrewAgent,
    CrewExecutor,
    CrewStage,
    ExecutionMode,
    MonitoringEngine,
    RouterManager,
    RoutingStrategy,
    Task,
    TaskStatus,
    WorkflowEngine,
)
from thegent.crew.executor import (
    ExecutionResult,
    HierarchicalAssigner,
    RoundRobinAssigner,
    SkillBasedAssigner,
    TaskExecutor,
)


class TestCrew:
    """Test Crew model."""

    def test_create_crew(self):
        """Test crew creation."""
        crew = Crew(
            name="Test Crew",
            description="Test description",
            execution_mode=ExecutionMode.SEQUENTIAL,
        )

        assert crew.name == "Test Crew"
        assert crew.description == "Test description"
        assert crew.execution_mode == ExecutionMode.SEQUENTIAL
        assert crew.status == "idle"

    def test_add_agent(self):
        """Test adding agent to crew."""
        crew = Crew(name="Test Crew")
        agent = CrewAgent(role="coder", name="Coder")

        crew.add_agent(agent)
        assert len(crew.agents) == 1
        assert crew.agents[0] == agent

    def test_add_task(self):
        """Test adding task to crew."""
        crew = Crew(name="Test Crew")
        task = Task(description="Test task")

        crew.add_task(task)
        assert len(crew.tasks) == 1
        assert crew.tasks[0] == task

    def test_get_agent_by_id(self):
        """Test getting agent by ID."""
        crew = Crew(name="Test Crew")
        agent = CrewAgent(role="coder", name="Coder")
        crew.add_agent(agent)

        found = crew.get_agent_by_id(agent.id)
        assert found == agent

    def test_get_task_by_id(self):
        """Test getting task by ID."""
        crew = Crew(name="Test Crew")
        task = Task(description="Test task")
        crew.add_task(task)

        found = crew.get_task_by_id(task.id)
        assert found == task


class TestTask:
    """Test Task model."""

    def test_create_task(self):
        """Test task creation."""
        task = Task(description="Test task")

        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert len(task.dependencies) == 0

    def test_add_dependency(self):
        """Test adding dependency."""
        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")

        task2.add_dependency(task1.id)
        assert task1.id in task2.dependencies

    def test_is_ready(self):
        """Test dependency readiness check."""
        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        task2.add_dependency(task1.id)

        assert not task2.is_ready(set())
        assert task2.is_ready({task1.id})

    def test_mark_completed(self):
        """Test marking task as completed."""
        task = Task(description="Test task")
        task.mark_completed("result")

        assert task.status == TaskStatus.COMPLETED
        assert task.result == "result"
        assert task.completed_at is not None

    def test_mark_failed(self):
        """Test marking task as failed."""
        task = Task(description="Test task")
        task.mark_failed("error")

        assert task.status == TaskStatus.FAILED
        assert task.error == "error"
        assert task.completed_at is not None


class TestCrewAgent:
    """Test CrewAgent model."""

    def test_create_agent(self):
        """Test agent creation."""
        agent = CrewAgent(role="coder", name="Coder")

        assert agent.role == "coder"
        assert agent.name == "Coder"

    def test_can_handle_task(self):
        """Test task handling check."""
        agent = CrewAgent(role="coder", capabilities=["python", "javascript"])

        assert agent.can_handle_task("Write Python code")
        assert agent.can_handle_task("Implement JavaScript feature")
        assert not agent.can_handle_task("Design UI mockup")


class TestTaskExecutor:
    """Test TaskExecutor."""

    def test_resolve_dependencies(self):
        """Test dependency resolution."""
        executor = TaskExecutor()

        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        task3 = Task(description="Task 3")

        task2.add_dependency(task1.id)
        task3.add_dependency(task2.id)

        ordered = executor.resolve_dependencies([task3, task1, task2])
        assert ordered[0].id == task1.id
        assert ordered[1].id == task2.id
        assert ordered[2].id == task3.id

    def test_resolve_dependencies_circular(self):
        """Test circular dependency detection."""
        executor = TaskExecutor()

        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")

        task1.add_dependency(task2.id)
        task2.add_dependency(task1.id)

        with pytest.raises(ValueError, match="Circular dependency"):
            executor.resolve_dependencies([task1, task2])

    def test_get_task_input(self):
        """Test getting task input from dependencies."""
        executor = TaskExecutor()

        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        task2.add_dependency(task1.id)

        completed = {
            task1.id: ExecutionResult(task_id=task1.id, success=True, result="result1"),
        }

        context = executor.get_task_input(task2, completed)
        assert "dependencies" in context
        assert task1.id in context["dependencies"]
        assert context["dependencies"][task1.id]["result"] == "result1"


class TestAgentAssigner:
    """Test agent assignment strategies."""

    def test_round_robin_assigner(self):
        """Test round-robin assignment."""
        assigner = RoundRobinAssigner()

        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        task3 = Task(description="Task 3")

        agent1 = CrewAgent(role="agent1")
        agent2 = CrewAgent(role="agent2")

        assignments = assigner.assign([task1, task2, task3], [agent1, agent2])

        assert assignments[task1.id] == agent1.id
        assert assignments[task2.id] == agent2.id
        assert assignments[task3.id] == agent1.id

    def test_skill_based_assigner(self):
        """Test skill-based assignment."""
        assigner = SkillBasedAssigner()

        task = Task(description="Write Python code")

        python_agent = CrewAgent(role="python-developer", capabilities=["python"])
        js_agent = CrewAgent(role="javascript-developer", capabilities=["javascript"])

        assignments = assigner.assign([task], [python_agent, js_agent])

        assert assignments[task.id] == python_agent.id

    def test_hierarchical_assigner(self):
        """Test hierarchical assignment."""
        assigner = HierarchicalAssigner()

        task1 = Task(description="Task 1")
        task2 = Task(description="Task 2")
        task3 = Task(description="Task 3")

        manager = CrewAgent(role="manager")
        worker = CrewAgent(role="worker")

        assignments = assigner.assign([task1, task2, task3], [manager, worker])

        # First tasks should go to manager
        assert assignments[task1.id] == manager.id
        assert assignments[task2.id] == manager.id
        # Later tasks to worker
        assert assignments[task3.id] == worker.id


class TestCrewExecutor:
    """Test CrewExecutor."""

    def test_create_executor(self):
        """Test executor creation."""
        crew = Crew(name="Test Crew")
        executor = CrewExecutor(crew)

        assert executor.crew == crew
        assert executor.task_executor is not None
        assert executor.agent_assigner is not None

    def test_assign_tasks_to_agents(self):
        """Test task assignment."""
        crew = Crew(name="Test Crew", execution_mode=ExecutionMode.SEQUENTIAL)

        agent = CrewAgent(role="coder")
        task = Task(description="Test task")

        crew.add_agent(agent)
        crew.add_task(task)

        executor = CrewExecutor(crew)
        assignments = executor.assign_tasks_to_agents()

        assert task.id in assignments
        assert assignments[task.id] == agent.id


class TestWorkflowEngine:
    """Test WorkflowEngine."""

    def test_add_stage(self):
        """Test adding stage."""
        engine = WorkflowEngine()
        stage = CrewStage(id="stage1", name="Stage 1")

        engine.add_stage(stage)
        assert len(engine.stages) == 1

    def test_resolve_stage_dependencies(self):
        """Test stage dependency resolution."""
        engine = WorkflowEngine()

        stage1 = CrewStage(id="stage1", name="Stage 1")
        stage2 = CrewStage(id="stage2", name="Stage 2", depends_on=["stage1"])

        engine.add_stage(stage2)
        engine.add_stage(stage1)

        ordered = engine.resolve_stage_dependencies()
        assert ordered[0].id == "stage1"
        assert ordered[1].id == "stage2"


class TestRouterManager:
    """Test RouterManager."""

    def test_create_router(self):
        """Test router creation."""
        router = RouterManager(strategy=RoutingStrategy.COST_OPTIMIZED)

        assert router.strategy == RoutingStrategy.COST_OPTIMIZED

    def test_select_agent_cost_optimized(self):
        """Test cost-optimized routing."""
        router = RouterManager(strategy=RoutingStrategy.COST_OPTIMIZED)

        from thegent.crew.router import RouteMetrics

        agent1 = CrewAgent(role="agent1")
        agent2 = CrewAgent(role="agent2")

        router.update_agent_metrics(agent1.id, RouteMetrics(cost_per_token=0.001))
        router.update_agent_metrics(agent2.id, RouteMetrics(cost_per_token=0.002))

        selected = router.select_agent("Test task", [agent1, agent2])
        assert selected == agent1


class TestMonitoringEngine:
    """Test MonitoringEngine."""

    def test_check_health(self):
        """Test health checking."""
        engine = MonitoringEngine()
        crew = Crew(name="Test Crew")

        agent = CrewAgent(role="coder")
        task = Task(description="Test task")

        crew.add_agent(agent)
        crew.add_task(task)

        health = engine.check_health(crew)
        assert health.healthy is True

    def test_track_performance(self):
        """Test performance tracking."""
        engine = MonitoringEngine()

        results = {
            "task1": ExecutionResult(task_id="task1", success=True, duration_seconds=10.0),
            "task2": ExecutionResult(task_id="task2", success=True, duration_seconds=20.0),
            "task3": ExecutionResult(task_id="task3", success=False, duration_seconds=5.0),
        }

        metrics = engine.track_performance("crew1", results)

        assert metrics.total_tasks == 3
        assert metrics.completed_tasks == 2
        assert metrics.failed_tasks == 1
        assert metrics.avg_duration_seconds == 15.0

    def test_track_costs(self):
        """Test cost tracking."""
        engine = MonitoringEngine()

        results = {
            "task1": ExecutionResult(task_id="task1", success=True, tokens_used=100, cost_usd=0.01),
            "task2": ExecutionResult(task_id="task2", success=True, tokens_used=200, cost_usd=0.02),
        }

        metrics = engine.track_costs("crew1", results)

        assert metrics.total_tokens == 300
        assert metrics.total_cost_usd == 0.03
        assert metrics.cost_per_task == 0.015
