"""LiveCodeBench benchmark"""

from dataclasses import dataclass
from helios.models.task import TaskMetadata, TaskInput, TaskResources
from heliosbench.base import Benchmark, BenchmarkMetadata, register_benchmark


@register_benchmark("live-code-bench")
class LiveCodeBench(Benchmark):
    """LiveCodeBench - Coding challenges with tests
    
    Comprehensive coding benchmark covering:
    - LeetCode-style problems
    - Competition problems
    - Real-world coding tasks
    """
    
    VERSION = "1.0"
    
    TASKS = [
        "two-sum",
        "reverse-linked-list",
        "binary-tree-inorder",
        "merge-sorted-arrays",
    ]
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            name="live-code-bench",
            description="Comprehensive coding benchmark with tests",
            version=self.VERSION,
            task_count=len(self.TASKS),
            categories=["coding", "algorithms", "data-structures"],
            url="https://livecodebench.github.io",
        )
    
    def get_task(self, instance_id: str) -> tuple[TaskMetadata, TaskInput]:
        if instance_id not in self.TASKS:
            raise KeyError(f"Task '{instance_id}' not found")
        
        return (
            TaskMetadata(
                id=instance_id,
                dataset="live-code-bench",
                instance_id=instance_id,
                difficulty="medium",
                tags=["coding", "algorithms"],
            ),
            TaskInput(
                instruction=f"Solve the {instance_id} problem. Write a function that passes the provided tests.",
                resources=TaskResources(cpus=1, memory_mb=2048, timeout_sec=300),
            )
        )
    
    def list_instances(self) -> list[str]:
        return self.TASKS
