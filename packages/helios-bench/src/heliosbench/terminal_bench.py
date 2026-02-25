"""Terminal-Bench 2.0 benchmark"""

from dataclasses import dataclass
from heliosbench.base import Benchmark, BenchmarkMetadata, BenchmarkRegistry, register_benchmark


@register_benchmark("terminal-bench")
class TerminalBench(Benchmark):
    """Terminal-Bench 2.0 - Software engineering tasks in terminal environments"""
    
    VERSION = "2.0"
    
    # Known tasks (would be loaded from registry in full impl)
    TASKS = {
        "chess-best-move": "Chess best move prediction",
        "gpt2-codegolf": "GPT-2 code golf",
        "break-filter-js-from-html": "Break JS filter from HTML",
        "llm-inference-batching-scheduler": "LLM inference batching",
        "pytorch-model-cli": "PyTorch model CLI",
        "password-recovery": "Password recovery",
        "portfolio-optimization": "Portfolio optimization",
        "regex-chess": "Regex chess",
        "headless-terminal": "Headless terminal tasks",
    }
    
    @property
    def metadata(self) -> BenchmarkMetadata:
        return BenchmarkMetadata(
            name="terminal-bench",
            description="Software engineering tasks executed in terminal environments",
            version=self.VERSION,
            task_count=len(self.TASKS),
            categories=["software-engineering", "cli", "terminal"],
            url="https://github.com/laude-institute/terminal-bench-2",
        )
    
    def get_task(self, instance_id: str) -> tuple[TaskMetadata, TaskInput]:
        """Get a specific task"""
        if instance_id not in self.TASKS:
            raise KeyError(f"Task '{instance_id}' not found")
        
        return (
            TaskMetadata(
                id=instance_id,
                dataset="terminal-bench",
                instance_id=instance_id,
                difficulty="medium",
                tags=self.TASKS[instance_id].split(),
            ),
            TaskInput(
                instruction=f"Complete the {instance_id} task",
                resources=TaskResources(cpus=1, memory_mb=2048, timeout_sec=600),
            )
        )
    
    def list_instances(self) -> list[str]:
        """List all task instances"""
        return list(self.TASKS.keys())
