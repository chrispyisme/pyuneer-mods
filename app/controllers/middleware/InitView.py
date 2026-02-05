
from lib.http import Response
from lib.logging.Logger import Logger

class InitView:
    """Middleware that creates a fresh Response, sets a header, and
    re-registers it in the container as the `response` singleton.

    Usage: register this middleware in the container under a name and include
    that name in `route.middleware` so the Router will `container.make()` it.
    """
    def __init__(self, c):
        self._settings = c.make("settings")
    # Init logger
        log_format = self._settings.get("log_format", "%(asctime)s [%(levelname)s] %(message)s")
        self._log = Logger(
            level="INFO",
            file="/usr/lib/cgi-bin/app/logs/InitView.log",
            format=log_format,
            name="InitView"
        )

    def handle(self, c, request, nxt):
        # Lazily import Response to avoid circular imports at module load
        response = c.make(Response)
    
        response.set_header('X-MW', 'template')

        response.set_body("<h1>Template Loaded in body</h1>")
        # Re-register the new response instance as the container singleton
        # so later `container.make('response')` returns this response
        
        

        # Continue middleware chain
        return nxt()