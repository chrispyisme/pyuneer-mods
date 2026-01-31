class ResponseMiddleware:
    """Middleware that creates a fresh Response, sets a header, and
    re-registers it in the container as the `response` singleton.

    Usage: register this middleware in the container under a name and include
    that name in `route.middleware` so the Router will `container.make()` it.
    """
    def handle(self, container, request, nxt):
        # Lazily import Response to avoid circular imports at module load
        from lib.http.Response import Response

        resp = Response()
        resp.set_header('X-MW', 'template')

        # Re-register the new response instance as the container singleton
        # so later `container.make('response')` returns this response
        container.singleton('response', resp)

        # Continue middleware chain
        return nxt()
