"""SWE-Bench benchmark"""

from dataclasses import dataclass
from typing import Any
from helios.models.task import TaskMetadata, TaskInput, TaskResources
from heliosbench.base import Benchmark, BenchmarkMetadata, register_benchmark


@register_benchmark("swe-bench")
class SWEBench(Benchmark):
    """SWE-Bench - Software Engineering Benchmark
    
    Real-world bug fixes from GitHub issues.
    """
    
    VERSION = "1.0"
    
    # Placeholder - full impl would load from SWE-bench dataset
    TASKS = [
        "django__django-110",
        "pytest__pytest-1234",
        "requests__requests-1234",
    ]
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            name="swe-bench",
            description="Real-world bug fixes from GitHub",
            version=self.VERSION,
            task_count=len(self.TASKS),
            categories=["bug-fix", "software-engineering"],
            url="https://github.com/princeton-nlp/SWE-bench",
        )
    
    def get_task(self, instance_id: str) -> tuple[TaskMetadata, TaskInput]:
        """Get a SWE-bench task"""
        # Parse repo__issue format
        if "__" not in instance_id:
            raise ValueError(f"Invalid SWE-bench instance ID: {instance_id}")
        
        repo, issue = instance_id.split("__", 1)
        
        return (
            TaskMetadata(
                id=instance_id,
                dataset="swe-bench",
                instance_id=instance_id,
                difficulty="hard",
                tags=["bug-fix", "github", repo],
            ),
            TaskInput(
                instruction=f"Fix the issue in {repo} described in the issue #{issue}",
                resources=TaskResources(cpus=2, memory_mb=4096, timeout_sec=1800),
            )
        )
    
    def list_instances(self) -> list[str]:
        return self.TASKS
