"""Legacy JSON-RPC agent server import surface backed by thegent_protocols."""

from thegent_protocols.protocols import jsonrpc_agent_server as _authority

for _name in dir(_authority):
    if _name not in {"__builtins__", "__cached__", "__doc__", "__file__", "__loader__", "__name__", "__package__", "__spec__"}:
        globals()[_name] = getattr(_authority, _name)

__all__ = [name for name in dir(_authority) if name not in {"__builtins__", "__cached__", "__doc__", "__file__", "__loader__", "__name__", "__package__", "__spec__"}]
