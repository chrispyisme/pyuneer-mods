"""app.controllers.TestController

Changelog:
- 2026-01-29: Added example `TestController` to demonstrate constructor
    injection and usage of `handler_params` passed from `Router`.
"""

class TestController:
    def __init__(self, config="default", timeout: int = 5):
        self.config = config
        self.timeout = timeout

    def index(self, container, request, **params):
        response = container.make("response")
        response.set_status_code(200)
        response.set_content_type("text/html")
        body = f"TestController: config={self.config}, timeout={self.timeout}, params={params}"
        response.set_body(body)
        response.send()
        return response
