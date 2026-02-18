class DocInit:
    def __init__(self, container, request, next):
        self.c = container
        self.req = request
        self.nxt = next
        
        res = container.make("response")
        res.set_status_code(200)
        res.set_header("Content-Type", "text/html")
        res.set_body("mw")
        self.nxt()
        
    def handle(self):
        # Do your middleware stuff here
        # You can use self.c, self.req, etc.
        pass
        