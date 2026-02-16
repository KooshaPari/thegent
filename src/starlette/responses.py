class Response:
    pass

class JSONResponse(Response):
    def __init__(self, content, status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code
