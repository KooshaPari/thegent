class BatchSpanProcessor:
    def __init__(self, exporter) -> None:
        self.exporter = exporter


class ConsoleSpanExporter:
    def __init__(self) -> None:
        pass
