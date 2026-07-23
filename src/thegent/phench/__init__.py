"""Package: thegent.phench - re-exports from local phench implementation."""

from __future__ import annotations

from . import service
from . import models
from . import runner
from . import store

# Re-export everything from service, models, runner, store
from .service import *
from .models import *
from .runner import *
from .store import *

# Keep export discovery aligned with the implementation modules.
__all__ = list(service.__all__) + (  # noqa: PLE0605 -- dynamic re-export API is intentional
    list(models.__all__) if hasattr(models, "__all__") else []
)
