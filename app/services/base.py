services = [
    {
        "abstract":"router",
        "concrete":"lib.routing.Router.Router",
        "type":"singleton",
        "params": {
            "request":"Request"
        },
        "tags":[
            "API", "router", "REST"
        ]
    },
    {
        "abstract":"Request",
        "concrete":"lib.http.Request.Request",
        "type":"factory",
        "params": {
            "request":"lib.http.Request.Request"
        },
        "tags":[
            "API", "router", "REST"
        ]       
    }
]

__all__ = ["services"]