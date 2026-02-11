from lib.http.Response import Response

class Home:
    def __init__(self, container, request, **params):
        pass
        
    def index(self, container, request, **params):
        response = container.make(Response)

        response.set_body(f"<h1>{request.get_uri()}</h1>")
        response.send()