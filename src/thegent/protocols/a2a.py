"""Legacy A2A protocol import surface backed by thegent_protocols."""

from thegent_protocols.protocols.a2a import (
    A2AMessage,
    A2AProtocol,
    A2ARouter,
    VALID_MESSAGE_TYPES,
    a2a_message_from_dict,
    a2a_message_to_dict,
    create_response,
    validate_a2a_message,
)

__all__ = [
    "A2AMessage",
    "A2AProtocol",
    "A2ARouter",
    "VALID_MESSAGE_TYPES",
    "a2a_message_from_dict",
    "a2a_message_to_dict",
    "create_response",
    "validate_a2a_message",
]
