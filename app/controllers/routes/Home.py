from lib.http.Response import Response

class Home:
    def __init__(self, container, request, **params):
        pass
        
    def index(self, container, request, **params):
        try:
            response = container.make("response")

            response.set_body(f"{response.get_body()}{request.get_params()}")
            response.send()
        except Exception as e:
            print(f"Error in Home@index: {e}")