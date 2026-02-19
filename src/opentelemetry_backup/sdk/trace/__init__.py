class TracerProvider:
    def __init__(self, resource=None) -> None:
        self.resource = resource

    def add_span_processor(self, processor) -> None:
        return None
