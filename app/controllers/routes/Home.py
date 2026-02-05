from lib.http.Response import Response

class Home:
    def __init__(self, container, request, **params):
        pass
        
    def index(self, container, request, **params):
        response = container.make(Response)
        

        response.send()