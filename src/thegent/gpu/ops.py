"""
GPU Operations

GPU-accelerated operations for embeddings and inference.
"""

from typing import Optional, Any
import time


class GPUOperations:
    """GPU-accelerated operations."""

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self._torch = None
        self._device = None

        try:
            import torch
            self._torch = torch
            if torch.cuda.is_available():
                self._device = torch.device(f"cuda:{device_index}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self._device = torch.device("mps")
        except ImportError:
            pass

    @property
    def available(self) -> bool:
        return self._device is not None

    def to_gpu(self, tensor: Any) -> Any:
        """Move tensor to GPU."""
        if self._device and hasattr(tensor, 'to'):
            return tensor.to(self._device)
        return tensor

    def to_cpu(self, tensor: Any) -> Any:
        """Move tensor to CPU."""
        if hasattr(tensor, 'cpu'):
            return tensor.cpu()
        return tensor

    def cosine_similarity(self, a: Any, b: Any) -> Any:
        """Compute cosine similarity on GPU."""
        if not self._torch:
            return None

        a_tensor = self._torch.tensor(a) if not isinstance(a, self._torch.Tensor) else a
        b_tensor = self._torch.tensor(b) if not isinstance(b, self._torch.Tensor) else b

        if self._device:
            a_tensor = a_tensor.to(self._device)
            b_tensor = b_tensor.to(self._device)

        a_norm = self._torch.nn.functional.normalize(a_tensor, dim=-1)
        b_norm = self._torch.nn.functional.normalize(b_tensor, dim=-1)

        return (a_norm * b_norm).sum(dim=-1)

    def batch_embeddings(self, texts: list[str], model: Any = None) -> Any:
        """Compute embeddings on GPU."""
        if not self._torch or not model:
            return None

        # Move model to GPU
        if self._device and hasattr(model, 'to'):
            model = model.to(self._device)

        # Compute embeddings
        with self._torch.no_grad():
            if hasattr(model, 'encode'):
                embeddings = model.encode(texts)
            else:
                # Assume transformers-style model
                import transformers
                tokenizer = transformers.AutoTokenizer.from_pretrained(model)
                model_obj = transformers.AutoModel.from_pretrained(model)

                if self._device:
                    model_obj = model_obj.to(self._device)

                inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
                if self._device:
                    inputs = {k: v.to(self._device) for k, v in inputs.items()}

                outputs = model_obj(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings

    def benchmark(self, size: int = 1000) -> dict:
        """Run GPU benchmark."""
        if not self._torch or not self._device:
            return {"available": False}

        # CPU benchmark
        a_cpu = self._torch.randn(size, size)
        b_cpu = self._torch.randn(size, size)

        start = time.time()
        for _ in range(10):
            c_cpu = self._torch.mm(a_cpu, b_cpu)
        cpu_time = time.time() - start

        # GPU benchmark
        a_gpu = a_cpu.to(self._device)
        b_gpu = b_cpu.to(self._device)

        # Warmup
        _ = self._torch.mm(a_gpu, b_gpu)
        if self._torch.cuda.is_available():
            self._torch.cuda.synchronize()

        start = time.time()
        for _ in range(10):
            c_gpu = self._torch.mm(a_gpu, b_gpu)
        if self._torch.cuda.is_available():
            self._torch.cuda.synchronize()
        gpu_time = time.time() - start

        return {
            "available": True,
            "device": str(self._device),
            "matrix_size": size,
            "cpu_time": cpu_time,
            "gpu_time": gpu_time,
            "speedup": cpu_time / gpu_time if gpu_time > 0 else 0
        }
