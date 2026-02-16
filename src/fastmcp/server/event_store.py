class EventStore:
    def __init__(self, storage: object | None = None) -> None:
        self.storage = storage
